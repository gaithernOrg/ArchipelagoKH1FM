from typing import Dict, List, Set

from BaseClasses import Entrance, EntranceType, Region
from entrance_rando import disconnect_entrance_for_randomization, randomize_entrances
from . import Data
from .Locations import KH1Location, KH1LocationData, event_location_table, location_table
from .Locations import doorway_into_room_name, doorway_out_of_room_name, doorway_region_name
from .Rules.traverse_town import build_room_rules


REGION_EXITS: Dict[str, List[str]] = {
    "Menu":             ["Awakening", "Levels", "World Map"],
    "Awakening":        [],
    "Destiny Islands":  [],
    "Wonderland":       [],
    "Olympus Coliseum": [],
    "Deep Jungle":      [],
    "Agrabah":          [],
    "Monstro":          [],
    "Atlantica":        [],
    "Halloween Town":   [],
    "Neverland":        [],
    "Hollow Bastion":   [],
    "End of the World": [],
    "100 Acre Wood":    [],
    "Levels":           [],
    "Homecoming":       [],
    "Accessories":      [],
    "World Map":        ["Destiny Islands", "Traverse Town", "Wonderland", "Olympus Coliseum", "Deep Jungle",
                         "Agrabah", "Monstro", "Atlantica", "Halloween Town", "Neverland", "Hollow Bastion",
                         "End of the World", "Homecoming", "Accessories"],
}

EXIT_TARGETS: Dict[str, str] = {
    "Traverse Town": "Traverse Town 1st District",
}

WORLD_NUMBERS: Dict[str, int] = {
    "Traverse Town": 3,
}

OPTION_DRIVEN_LOCATION_GROUPS: Set[str] = {"Levels", "Accessory", "Augment"}


def get_active_locations(kh1world) -> Dict[str, KH1LocationData]:
    option_driven_names = set(kh1world.get_level_check_locations())
    option_driven_names.update(kh1world.get_starting_accessory_locations())
    option_driven_names.update(kh1world.get_accessory_locations())
    active = {name: data for name, data in location_table.items()
              if OPTION_DRIVEN_LOCATION_GROUPS.isdisjoint((data.region, *data.groups)) or name in option_driven_names}
    return active | event_location_table


def get_locked_rooms() -> Set[str]:
    return set(build_room_rules())


def get_region_names() -> List[str]:
    locked_rooms = get_locked_rooms()
    names = list(REGION_EXITS)
    for row in Data.entrances:
        for name in (row["From Region"], row["To Region"]):
            if name not in names:
                names.append(name)
        if row["From Region"] in locked_rooms:
            names.append(doorway_region_name(row["Entrance Name"]))
    return names


def create_regions(kh1world):
    player = kh1world.player
    locked_rooms = get_locked_rooms()
    regions = {name: Region(name, player, kh1world.multiworld) for name in get_region_names()}

    for name, data in get_active_locations(kh1world).items():
        region = regions[data.region]
        region.locations.append(KH1Location(player, name, data.code, region))

    for name, exits in REGION_EXITS.items():
        regions[name].exits += [Entrance(player, exit, regions[name]) for exit in exits]

    for row in Data.entrances:
        entrance_name = row["Entrance Name"]
        source = regions[row["From Region"]]
        if row["From Region"] in locked_rooms:
            doorway = regions[doorway_region_name(entrance_name)]
            source.exits.append(Entrance(player, doorway_out_of_room_name(entrance_name), source))
            doorway.exits.append(Entrance(player, doorway_into_room_name(entrance_name), doorway))
            source = doorway
        source.exits.append(Entrance(player, entrance_name, source))

    kh1world.multiworld.regions += regions.values()


def find_arrival_region_name(row: Dict[str, str], locked_rooms: Set[str]) -> str:
    target = row["To Region"]
    if target not in locked_rooms:
        return target
    first_door_of_target = None
    for other_row in Data.entrances:
        if other_row["From Region"] != target:
            continue
        if first_door_of_target is None:
            first_door_of_target = other_row
        if other_row["To Region"] == row["From Region"]:
            return doorway_region_name(other_row["Entrance Name"])
    return doorway_region_name(first_door_of_target["Entrance Name"])


def has_randomized_way_back(row: Dict[str, str]) -> bool:
    for other_row in Data.entrances:
        if other_row["Randomize"] != "1":
            continue
        if other_row["From Region"] == row["To Region"] and other_row["To Region"] == row["From Region"]:
            return True
    return False


def get_randomized_door_names() -> List[str]:
    names = []
    for row in Data.entrances:
        if row["Randomize"] == "1" and has_randomized_way_back(row):
            names.append(row["Entrance Name"])
    return names


def connect_vanilla_entrances(kh1world):
    locked_rooms = get_locked_rooms()
    for exits in REGION_EXITS.values():
        for exit in exits:
            target = EXIT_TARGETS.get(exit, exit)
            kh1world.get_entrance(exit).connect(kh1world.get_region(target))

    for row in Data.entrances:
        entrance_name = row["Entrance Name"]
        if row["From Region"] in locked_rooms:
            room = kh1world.get_region(row["From Region"])
            doorway = kh1world.get_region(doorway_region_name(entrance_name))
            kh1world.get_entrance(doorway_out_of_room_name(entrance_name)).connect(doorway)
            kh1world.get_entrance(doorway_into_room_name(entrance_name)).connect(room)
        arrival = kh1world.get_region(find_arrival_region_name(row, locked_rooms))
        kh1world.get_entrance(entrance_name).connect(arrival)


def shuffle_doors(kh1world):
    for name in get_randomized_door_names():
        entrance = kh1world.get_entrance(name)
        entrance.randomization_type = EntranceType.TWO_WAY
        disconnect_entrance_for_randomization(entrance)
    placement = randomize_entrances(kh1world, True, {0: [0]})
    kh1world.entrance_pairings = dict(placement.pairings)
    for exit_name, target_name in placement.pairings:
        kh1world.multiworld.spoiler.set_entrance(exit_name, target_name, "entrance", kh1world.player)


def connect_entrances(kh1world):
    connect_vanilla_entrances(kh1world)
    kh1world.entrance_pairings = {}
    if kh1world.options.randomize_entrances:
        shuffle_doors(kh1world)


def get_door_destinations(kh1world) -> List[Dict[str, int]]:
    rows_by_name = {row["Entrance Name"]: row for row in Data.entrances}
    destinations = []
    for exit_name, target_name in kh1world.entrance_pairings.items():
        exit_row = rows_by_name[exit_name]
        target_row = rows_by_name[target_name]
        destinations.append({
            "world": WORLD_NUMBERS[exit_row["World"]],
            "area": int(exit_row["Area"], 16),
            "exit": int(exit_row["Exit ID"], 16),
            "back": int(exit_row["Arrival ID"], 16),
            "to_world": WORLD_NUMBERS[target_row["World"]],
            "to_area": int(target_row["Area"], 16),
            "to_entrance": int(target_row["Arrival ID"], 16),
        })
    return destinations
