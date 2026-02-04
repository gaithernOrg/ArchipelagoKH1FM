from __future__ import annotations
from argparse import Namespace
import os
import json
import sys
import asyncio
import shutil
import logging
import re
import time
import socket
from calendar import timegm

import ModuleUpdate
ModuleUpdate.update()

import Utils

iam = "KH1 AP Client"

logger = logging.getLogger("Client")

if __name__ == "__main__":
    Utils.init_logging("KH1Client", exception_logger="Client")

from NetUtils import NetworkItem, ClientStatus
from CommonClient import gui_enabled, handle_url_arg, logger, get_base_parser, ClientCommandProcessor, \
    CommonContext, server_loop

def recv_line(sock, timeout=2.0):
    sock.settimeout(timeout)
    data = bytearray()
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                raise ConnectionError("Server closed connection")
            data.extend(chunk)
            if b"\n" in data:
                line, _, remainder = data.partition(b"\n")
                return line.decode("utf-8")
        except socket.timeout:
            return None

#def send_to_game_server(msg):
#    s = socket.socket()
#    s.connect(("127.0.0.1", 13138))
#    msg_bytes = (json.dumps(msg) + "\n").encode("utf-8")
#    s.sendall(msg_bytes)
#    data = json.loads(recv_line(s))
#    s.close()
#    return data


def check_stdin() -> None:
    if Utils.is_windows and sys.stdin:
        print("WARNING: Console input is not routed reliably on Windows, use the GUI instead.")

class GameClient:
    def __init__(self, host="127.0.0.1", port=13138):
        self.host = host
        self.port = port
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.lock = asyncio.Lock()
        self.connected = False

    async def connect(self):
        if self.connected:
            return
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port
        )
        self.connected = True

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False

    async def send(self, payload: dict) -> dict | None:
        async with self.lock:
            for attempt in (1, 2):
                try:
                    if not self.connected:
                        await self.connect()
                    msg = json.dumps(payload).encode("utf-8") + b"\n"
                    self.writer.write(msg)
                    await self.writer.drain()
                    line = await asyncio.wait_for(
                        self.reader.readline(), timeout=2.0
                    )
                    if not line:
                        raise ConnectionError("Server closed connection")
                    return json.loads(line.decode("utf-8"))
                except (ConnectionError, OSError, asyncio.TimeoutError) as e:
                    self.connected = False
                    if self.writer:
                        try:
                            self.writer.close()
                            await self.writer.wait_closed()
                        except Exception:
                            pass
                    self.reader = None
                    self.writer = None
                    if attempt == 1:
                        await asyncio.sleep(0.2)
                        continue
                    raise

class KH1ClientCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)

    def _cmd_slot_data(self):
        """Prints slot data settings for the connected seed"""
        for key in self.ctx.slot_data.keys():
            if key not in ["remote_location_ids", "synthesis_item_name_byte_arrays"]:
                self.output(str(key) + ": " + str(self.ctx.slot_data[key]))

    def _cmd_deathlink(self):
        """If your Death Link setting is set to "Toggle", use this command to turn Death Link on and off."""
        if "death_link" in self.ctx.slot_data.keys():
            if self.ctx.slot_data["death_link"] == "toggle":
                if self.ctx.death_link:
                    self.ctx.death_link = False
                    self.output(f"Death Link turned off")
                else:
                    self.ctx.death_link = True
                    self.output(f"Death Link turned on")
            else:
                self.output(f"'death_link' is not set to 'toggle' for this seed.")
                self.output(f"'death_link' = " + str(self.ctx.slot_data["death_link"]))
        else:
            self.output(f"No 'death_link' in slot_data keys. You probably aren't connected or are playing an older seed.")

class KH1Context(CommonContext):
    command_processor: int = KH1ClientCommandProcessor
    game = "Kingdom Hearts"
    items_handling = 0b011  # full remote except start inventory

    def __init__(self, server_address, password):
        super(KH1Context, self).__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = False
        self.awaiting_bridge = False
        self.hinted_location_ids: list[int] = []
        self.slot_data: dict = {}

        # Moved globals into instance attributes
        self.death_link: bool = False
        self.items_received: list[int] = []
        self.remote_location_ids: list[int] = []
        self.sora_koed = False
        self.sora_prev_koed = False
        self.game_client = GameClient()
        self.locations_checked: list[int] = []
        self.expecting_death: bool = False

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(KH1Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(KH1Context, self).connection_closed()
        self.items_received = []

    @property
    def endpoints(self):
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super(KH1Context, self).shutdown()
        await self.game_client.close()
        self.items_received = []

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:

            # Handle Slot Data
            self.slot_data = args['slot_data']
            for key in list(args['slot_data'].keys()):
                if key == "remote_location_ids":
                    self.remote_location_ids = args['slot_data'][key]
                if key == "death_link":
                    if args['slot_data']["death_link"] != "off":
                        self.death_link = True
            # End Handle Slot Data

        if cmd in {"ReceivedItems"}:
            self.items_received = []
            if args['index'] == 0:
                for item in args['items']:
                    item_obj = NetworkItem(*item)
                    item_id = item_obj.item
                    item_sender_id = item_obj.player
                    item_location_id = item_obj.location
                    if 2641017 <= item_id <= 2641071:
                        acc_location_id = item_id - 2641017 + 2659100
                        if acc_location_id not in self.locations_checked:
                            self.locations_checked.append(acc_location_id)
                    is_from_self_and_remote = item_sender_id == self.slot and item_location_id in self.remote_location_ids
                    is_from_server = item_location_id < 0
                    is_from_someone_else = item_sender_id != self.slot
                    if is_from_self_and_remote or is_from_server or is_from_someone_else:
                        self.items_received.append(item_id)
                asyncio.create_task(self.game_client.send({"items": self.items_received}))

        if cmd in {"PrintJSON"} and "type" in args:
            if args["type"] == "ItemSend":
                message = None
                item = args["item"]
                networkItem = NetworkItem(*item)
                receiverID = args["receiving"]
                senderID = networkItem.player
                locationID = networkItem.location
                if receiverID == self.slot or senderID == self.slot:
                    itemName = self.item_names.lookup_in_slot(networkItem.item, receiverID)[:20]
                    itemCategory = networkItem.flags
                    receiverName = self.player_names[receiverID][:20]
                    senderName = self.player_names[senderID][:20]
                    if receiverID == self.slot and receiverID != senderID: # Item received from someone else
                        message = ["From " + senderName, itemName]
                    elif senderID == self.slot and receiverID != senderID: # Item sent to someone else
                        message = [itemName, "to " + receiverName]
                    elif locationID in self.remote_location_ids: # Found a remote item
                        message = [itemName, ""]
                    if message is not None:
                        asyncio.create_task(self.game_client.send({"prompt": message}))
            if args["type"] == "ItemCheat":
                message = ["", ""]
                item = args["item"]
                networkItem = NetworkItem(*item)
                receiverID = args["receiving"]
                if receiverID == self.slot:
                    itemName = self.item_names.lookup_in_slot(networkItem.item, receiverID)[:20]
                    filename = "msg"
                    message = ["Received " + itemName, "from server"]
                    asyncio.create_task(self.game_client.send({"prompt": message}))

    def on_deathlink(self, data: dict[str, object]):
        self.expecting_death = True
        asyncio.create_task(self.game_client.send({"effect": {"sora_ko": True}}))

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class KH1Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago KH1 Client"

        self.ui = KH1Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def game_watcher(ctx: KH1Context):
    while not ctx.exit_event.is_set():
        if ctx.death_link and "DeathLink" not in ctx.tags:
            await ctx.update_death_link(ctx.death_link)
        if not ctx.death_link and "DeathLink" in ctx.tags:
            await ctx.update_death_link(ctx.death_link)
        if ctx.syncing is True:
            sync_msg = [{'cmd': 'Sync'}]
            if ctx.locations_checked:
                sync_msg.append({"cmd": "LocationChecks", "locations": list(ctx.locations_checked)})
            await ctx.send_msgs(sync_msg)
            ctx.syncing = False
        
        try:
            curr_state = await ctx.game_client.send({"get_state": True})
        except:
            curr_state = None
        
        if curr_state is not None:
            
            # Handle Deathlink
            ctx.sora_koed = curr_state["sora_koed"]
            if ctx.sora_koed:
                if ctx.expecting_death:
                    ctx.expecting_death = False
                elif not ctx.sora_prev_koed and ctx.death_link:
                    await ctx.send_death(death_text = "Sora was defeated!")
            ctx.sora_prev_koed = curr_state["sora_koed"]
            
            # Handle Victory
            victory = curr_state["victory"]
            if not ctx.finished_game and victory:
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
            
            # Handle Checked Locations
            ctx.locations_checked = list(set(ctx.locations_checked + curr_state["locations"]))
            await ctx.check_locations(ctx.locations_checked)
            
            # Handle Hinted Locations
            hinted_locations = curr_state["hinted_locations"]
            for hint_location_id in hinted_locations:
                if hint_location_id not in ctx.hinted_location_ids:
                    await ctx.send_msgs([{
                                "cmd": "LocationScouts",
                                "locations": [hint_location_id],
                                "create_as_hint": 2
                            }])
                    ctx.hinted_location_ids.append(hint_location_id)
        
        # Sync up items in case the player died or reloaded a save
        await ctx.game_client.send({"items": ctx.items_received})
        
        # Wait a bit to not constantly poll the game
        await asyncio.sleep(0.5)

async def main(args: Namespace):
    ctx = KH1Context(args.connect, args.password)
    ctx.auth = args.name
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()
    progression_watcher = asyncio.create_task(
        game_watcher(ctx), name="KH1ProgressionWatcher")

    await ctx.exit_event.wait()
    ctx.server_address = None

    await progression_watcher

    await ctx.shutdown()

def launch(*args: str):
    import colorama

    parser = get_base_parser(description="KH1 Client, for text interfacing.")
    parser.add_argument("--name", default=None)
    parser.add_argument("url", nargs="?")

    launch_args = handle_url_arg(parser.parse_args(args))

    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()