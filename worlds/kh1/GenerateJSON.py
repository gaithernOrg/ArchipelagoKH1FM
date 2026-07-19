import os
import io
import re
import struct
import pkgutil
from typing import Dict, Optional
import Utils
import zipfile
import json
from copy import deepcopy

from .Locations import location_table
from .Items import item_table
from .Data import CHAR_TO_KH, WORD, ITEMHELP, SYSMSG, GUMI_MES

from worlds.Files import APPlayerContainer



class KH1Container(APPlayerContainer):
    game: str = 'Kingdom Hearts'
    patch_file_ending = ".zip"

    def __init__(self, patch_data: Dict[str, str | bytes] | io.BytesIO, base_path: str = "", output_directory: str = "",
        player: Optional[int] = None, player_name: str = "", server: str = ""):
        self.patch_data = patch_data
        self.file_path = base_path
        container_path = os.path.join(output_directory, base_path + self.patch_file_ending)
        super().__init__(container_path, player, player_name, server)

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        for filename, text in self.patch_data.items():
            opened_zipfile.writestr(filename, text)
        super().write_contents(opened_zipfile)


def generate_json(world, output_directory):
    mod_name = f"AP-{world.multiworld.seed_name}-P{world.player}-{world.multiworld.get_file_safe_player_name(world.player)}"
    mod_dir = os.path.join(output_directory, mod_name + "_" + Utils.__version__)
    
    item_location_map = get_item_location_map(world)
    location_spheres = get_location_spheres(world)
    settings = get_settings(world)
    keyblade_stats = world.get_keyblade_stats()
    hints = get_progression_hints(world)
    gumi_mes_data = generate_gumi_mes_data(hints)

    files = {
        "item_location_map.json":  json.dumps(item_location_map),
        "location_spheres.json":   json.dumps(location_spheres),
        "keyblade_stats.json":     json.dumps(keyblade_stats),
        "settings.json":           json.dumps(settings),
        "ap_costs.json":           json.dumps(world.get_ap_costs()),
        "mp_costs.json":           json.dumps(world.get_mp_costs()),
        "mod.yml":                 get_mod_yml(settings),
        "UK_Word.bin":             generate_word(settings),
        "UK_ItemHelp.bin":         generate_itemhelp(keyblade_stats, item_location_map),
        "UK_sysmsg.binl":          generate_sysmsg(world.get_mp_costs()),
        "UK_gumi_mes_data.bin":    gumi_mes_data,
        "UK_gumi_mes_ofs.bin":     generate_gumi_mes_ofs(gumi_mes_data),
        "icon.png":                pkgutil.get_data(__name__, "icons/mod_icon.png"),
    }

    mod = KH1Container(files, mod_dir, output_directory, world.player,
            world.multiworld.get_file_safe_player_name(world.player))
    mod.write()

def get_item_location_map(world):
    location_item_map = {}
    for location in world.multiworld.get_filled_locations(world.player):
        if location.name != "Final Ansem":
            if world.player != location.item.player or (world.player == location.item.player and world.options.remote_items.current_key == "full" and (location_table[location.name].type not in ["Starting Accessory", "Augment"])):
                item_id = 2641230
            else:
                item_id = location.item.code
            location_data = location_table[location.name]
            location_id = location_data.code
            location_item_map[location_id] = item_id
    return location_item_map

def get_location_spheres(world):
    """
    Maps this player's location codes to the logical sphere they fall in
    (0-indexed, in playthrough order). Locations that turn out to be
    unreachable (e.g. under minimal accessibility) are mapped to -1.
    """
    location_spheres = {}
    reachable = True
    for sphere_index, sphere in enumerate(world.multiworld.get_spheres()):
        if not sphere:
            reachable = False
            continue
        for location in sphere:
            if location.player != world.player or location.name == "Final Ansem":
                continue
            location_data = location_table[location.name]
            location_spheres[location_data.code] = sphere_index if reachable else -1
    return location_spheres

def get_progression_hints(world):
    """
    Pairs each of this player's own progression items with the location it's
    found at, ordered by how early the location is reachable (unreachable
    locations sort last). Capped to the number of gummi name/description slots
    actually eligible for hint text (see GUMI_ELIGIBLE_NAME_INDICES).
    """
    location_spheres = get_location_spheres(world)
    candidates = []
    for location in world.multiworld.get_filled_locations(world.player):
        if location.name == "Final Ansem" or not location.item.advancement:
            continue
        item_name = location.item.name
        if location.item.player != world.player:
            item_name += f" ({world.multiworld.get_player_name(location.item.player)})"
        sphere = location_spheres.get(location_table[location.name].code, -1)
        candidates.append((sphere, location.name, item_name))
    candidates.sort(key=lambda candidate: (candidate[0] == -1, candidate[0], candidate[1]))
    return [(item_name, location_name) for _, location_name, item_name in candidates[:len(GUMI_ELIGIBLE_NAME_INDICES)]]

def get_mod_yml(settings):
    seed_str = settings["seed"].lstrip("W")
    hex_seed = f"{int(seed_str):X}" if seed_str.isdigit() else settings["seed"]
    return f"""
title: KH1 Randomizer Seed {hex_seed}
originalAuthor: Gicu
description: KH1 Randomizer Seed Information.  For use with gaithern/KH1-RANDOMIZER
assets:
- name: scripts/io_packages/json/item_location_map.json
  method: copy
  source:
    - name: item_location_map.json
- name: scripts/io_packages/json/keyblade_stats.json
  method: copy
  source:
    - name: keyblade_stats.json
- name: scripts/io_packages/json/settings.json
  method: copy
  source:
    - name: settings.json
- name: scripts/io_packages/json/ap_costs.json
  method: copy
  source:
    - name: ap_costs.json
- name: scripts/io_packages/json/mp_costs.json
  method: copy
  source:
    - name: mp_costs.json
- name: remastered/btltbl.bin/UK_Word.bin
  method: copy
  source:
    - name: UK_Word.bin
- name: remastered/btltbl.bin/UK_ItemHelp.bin
  method: copy
  source:
    - name: UK_ItemHelp.bin
- name: remastered/menu/uk/sysmsg.bin/UK_sysmsg.binl
  method: copy
  source:
    - name: UK_sysmsg.binl
- name: exchange/UK_gumi_mes_data.bin
  method: copy
  source:
    - name: UK_gumi_mes_data.bin
- name: exchange/UK_gumi_mes_ofs.bin
  method: copy
  source:
    - name: UK_gumi_mes_ofs.bin"""

def get_settings(world):
    settings = world.fill_slot_data()
    return settings

def generate_word(settings):
    seed_words = deepcopy(WORD)
    seed_words[seed_words.index("Puppy")] = f"{settings["puppy_value"]} Puppies"
    encoded_words = []
    for word in seed_words:
        encoded_word = bytearray()
        for token in re.findall(r"\{[^}]*\}|.", word):
            encoded_word.append(CHAR_TO_KH[token])
        encoded_words.append(bytes(encoded_word))
    return b"\x00".join(encoded_words)

def generate_itemhelp(keyblade_stats, item_location_map):
    seed_itemhelp = deepcopy(ITEMHELP)

    # Handle keyblade stats
    for i, stats in enumerate(keyblade_stats):
        seed_itemhelp[80 + i] = "".join(f"{key} {value} " for key, value in stats.items())
    
    # Handle augments
    item_code_to_name = {data.code: name for name, data in item_table.items()}
    for _, loc_data in location_table.items():
        if loc_data.type == "Augment":
            item_id = item_location_map.get(loc_data.code)
            if item_id is not None:
                item_name = item_code_to_name.get(item_id, "Unknown")
                itemhelp_idx = loc_data.code - 2659100 + 16
                seed_itemhelp[itemhelp_idx] = f"Augment: {item_name}"

    encoded_itemhelp = []
    for entry in seed_itemhelp:
        encoded_entry = bytearray()
        for token in re.findall(r"\{[^}]*\}|.", entry):
            encoded_entry.append(CHAR_TO_KH[token])
        encoded_itemhelp.append(bytes(encoded_entry))
    return b"\x00".join(encoded_itemhelp)

_MP_COST_LABELS = {15: "0.5 CP", 30: "1 CP", 100: "1 MP", 200: "2 MP", 300: "3 MP"}

_SPELL_GROUPS = [
    (212, ["Fire",    "Fira",    "Firaga"   ]),
    (215, ["Blizzard","Blizzara","Blizzaga" ]),
    (218, ["Thunder", "Thundara","Thundaga" ]),
    (221, ["Cure",    "Cura",    "Curaga"   ]),
    (224, ["Gravity", "Gravira", "Graviga"  ]),
    (227, ["Stop",    "Stopra",  "Stopga"   ]),
    (230, ["Aero",    "Aerora",  "Aeroga"   ]),
]

def generate_sysmsg(mp_costs):
    messages = list(SYSMSG)
    for group_idx, (sysmsg_idx, names) in enumerate(_SPELL_GROUPS):
        base = group_idx * 3
        desc = "{lf}".join(f"{names[i]} - {_MP_COST_LABELS[mp_costs[base + i]]}" for i in range(3))
        for i in range(3):
            messages[sysmsg_idx + i] = desc

    encoded_messages = []
    for message in messages:
        encoded_message = bytearray()
        for token in re.findall(r"\{[^}]*\}|.", message):
            encoded_message.append(CHAR_TO_KH[token])
        encoded_messages.append(bytes(encoded_message))

    count = len(encoded_messages)
    tbl_start = 0x20
    tbl_size = (count + 1) * 2
    str_base = tbl_start + tbl_size

    offsets = []
    blob = bytearray()
    for encoded_message in encoded_messages:
        offsets.append(len(blob))
        blob += encoded_message + b"\x00"
    offsets.append(len(blob))  # sentinel entry marking the end of the blob
    if len(blob) % 2:
        blob += b"\x00"  # pad the blob to an even length, as the original files do

    header = bytearray(str_base)
    header[0x00:0x0C] = b"Message v361"
    struct.pack_into("<I", header, 0x0C, count)
    struct.pack_into("<I", header, 0x10, tbl_start)
    struct.pack_into("<I", header, 0x14, str_base)
    struct.pack_into("<I", header, 0x18, tbl_size)
    struct.pack_into("<I", header, 0x1C, len(blob))
    for i, offset in enumerate(offsets):
        struct.pack_into("<H", header, tbl_start + i * 2, offset)

    result = bytes(header) + blob
    remainder = len(result) % 16
    if remainder:
        result += b"\xCD" * (16 - remainder)
    return result

GUMI_MES_OFS_SENTINEL = b"\xCD" * 10
GUMI_NAME_WIDTH = 18  # the gummi item list row is a single fixed-width line, not wrappable
GUMI_DESC_WRAP_WIDTH = 45
GUMI_DESC_MAX_LINES = 4

def truncate_gumi_name(text, width=GUMI_NAME_WIDTH):
    if len(text) <= width:
        return text
    return text[:width - 3].rstrip() + "..."

def wrap_gumi_text(text, width=GUMI_DESC_WRAP_WIDTH, max_lines=GUMI_DESC_MAX_LINES):
    lines = []
    line = ""
    for word in text.split(" "):
        candidate = f"{line} {word}".strip()
        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:width - 3].rstrip() + "..."
    return "{lf}".join(lines)

GUMI_MES_DATA_BUFFER_SIZE = 0x1800  # exact size the game reads exchange/UK_gumi_mes_data.bin into
# (Axa::FileIO::LoadFileToBuffer call in FUN_1402266c0, confirmed via Ghidra); it's a fixed static
# buffer unrelated to the vanilla file's own size, and exceeding it corrupts adjacent memory and
# crashes the game rather than failing gracefully.

def encode_kh_string(text):
    encoded = bytearray()
    for token in re.findall(r"\{[^}]*\}|.", text):
        encoded.append(CHAR_TO_KH[token])
    return bytes(encoded)

# Indices 64-127 are off-limits for hint text even though some of them are blank in vanilla:
# 71-118 is the 48-entry ship model block, and at least index 71 ("Kingdom") is read by native
# code as a raw 32-byte setup struct rather than display text (confirmed via Ghidra - FUN_14020d5b0
# copies 32 bytes straight out of it while building the gummi editor's model data); the rest of the
# block is treated the same way since it's a uniform set of records. 116-122 additionally overlap
# gummi item slots the KH1-RANDOMIZER Lua client repurposes as hidden save-data counters (the AP
# check-sync counter and starting-inventory/accessory/level-tracking flags in item_location_handlers.lua,
# 1fmRandoStartingAccessories.lua, 1fmRandoLevelUpItems.lua) - writing hint text there wouldn't corrupt
# those counters (they live in a separate runtime memory region, not this text table) but would show
# hint text next to an unrelated raw counter value in any UI that lists owned quantities. 64-70 (Spray,
# Palette, SYS. UP1/2, COM. LV1/2/3) have no confirmed non-text usage either way and are excluded
# conservatively rather than assumed safe.
GUMI_ELIGIBLE_NAME_INDICES = [i for i in range(160) if not (64 <= i <= 127)]

def generate_gumi_mes_data(hints):
    encoded_entries = [encode_kh_string(entry) for entry in GUMI_MES]
    content_budget = GUMI_MES_DATA_BUFFER_SIZE - (len(encoded_entries) - 1)  # minus null separators
    content_size = sum(len(entry) for entry in encoded_entries)

    for slot, (item_name, location_name) in zip(GUMI_ELIGIBLE_NAME_INDICES, hints):
        new_name = encode_kh_string(truncate_gumi_name(item_name))
        new_location = encode_kh_string(wrap_gumi_text(location_name))
        delta = (len(new_name) - len(encoded_entries[slot])) + (len(new_location) - len(encoded_entries[slot + 160]))
        if content_size + delta > content_budget:
            break
        encoded_entries[slot] = new_name
        encoded_entries[slot + 160] = new_location
        content_size += delta

    return b"\x00".join(encoded_entries)

def generate_gumi_mes_ofs(gumi_mes_data):
    offsets = [0]
    for i in range(len(gumi_mes_data)):
        if gumi_mes_data[i] == 0x00:
            offsets.append(i + 1)
    offsets = offsets[:-2]  # the source data always ends in two unreferenced entries
    return b"".join(struct.pack("<H", offset) for offset in offsets) + GUMI_MES_OFS_SENTINEL
