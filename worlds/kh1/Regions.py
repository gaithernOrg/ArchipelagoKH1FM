from typing import Dict, List, Set

from BaseClasses import Entrance, EntranceType, Region
from entrance_rando import disconnect_entrance_for_randomization, randomize_entrances
from . import Data
from .Locations import KH1Location, KH1LocationData, event_location_table, location_table
from .Locations import doorway_into_room_name, doorway_out_of_room_name, doorway_region_name
from .Rules import traverse_town, wonderland


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
    "Wonderland": "Wonderland Rabbit Hole",
}

WORLD_NUMBERS: Dict[str, int] = {
    "Traverse Town": 3,
    "Wonderland": 4,
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
    locked_rooms = set(traverse_town.build_room_rules())
    locked_rooms.update(wonderland.build_room_rules())
    return locked_rooms


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


def is_door(row: Dict[str, str]) -> bool:
    return bool(row["Area"] and row["Exit ID"])


def has_door_back(row: Dict[str, str]) -> bool:
    for other_row in Data.entrances:
        if not is_door(other_row):
            continue
        if other_row["From Region"] == row["To Region"] and other_row["To Region"] == row["From Region"]:
            return True
    return False


def is_two_way_door(row: Dict[str, str]) -> bool:
    return is_door(row) and has_door_back(row)


def is_one_way_door(row: Dict[str, str]) -> bool:
    return is_door(row) and not has_door_back(row)


def one_way_arrival_name(entrance_name: str) -> str:
    return f"{entrance_name} Arrival"


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


def disconnect_two_way_door(kh1world, entrance_name: str):
    entrance = kh1world.get_entrance(entrance_name)
    entrance.randomization_type = EntranceType.TWO_WAY
    disconnect_entrance_for_randomization(entrance)


def disconnect_one_way_door(kh1world, entrance_name: str):
    entrance = kh1world.get_entrance(entrance_name)
    entrance.randomization_type = EntranceType.ONE_WAY
    arrival_name = one_way_arrival_name(entrance_name)
    disconnect_entrance_for_randomization(entrance, one_way_target_name=arrival_name)


def shuffle_doors(kh1world):
    for row in Data.entrances:
        if is_two_way_door(row):
            disconnect_two_way_door(kh1world, row["Entrance Name"])
        if is_one_way_door(row):
            disconnect_one_way_door(kh1world, row["Entrance Name"])
    placement = randomize_entrances(kh1world, True, {0: [0]})
    kh1world.entrance_pairings = dict(placement.pairings)
    for exit_name, target_name in placement.pairings:
        kh1world.multiworld.spoiler.set_entrance(exit_name, target_name, "entrance", kh1world.player)


def connect_entrances(kh1world):
    connect_vanilla_entrances(kh1world)
    kh1world.entrance_pairings = {}
    if kh1world.options.randomize_entrances:
        shuffle_doors(kh1world)


def get_areas_by_region() -> Dict[str, int]:
    areas = {}
    for row in Data.entrances:
        if row["Area"]:
            areas[row["From Region"]] = int(row["Area"], 16)
    return areas


def get_arrivals_by_target_name() -> Dict[str, Dict[str, int]]:
    areas = get_areas_by_region()
    arrivals = {}
    for row in Data.entrances:
        if is_two_way_door(row):
            arrivals[row["Entrance Name"]] = {
                "to_world": WORLD_NUMBERS[row["World"]],
                "to_area": int(row["Area"], 16),
                "to_entrance": int(row["Arrival ID"], 16),
            }
        if is_one_way_door(row):
            arrivals[one_way_arrival_name(row["Entrance Name"])] = {
                "to_world": WORLD_NUMBERS[row["World"]],
                "to_area": areas[row["To Region"]],
                "to_entrance": int(row["Exit ID"], 16),
            }
    return arrivals


def get_door_destinations(kh1world) -> List[Dict[str, int]]:
    rows_by_name = {row["Entrance Name"]: row for row in Data.entrances}
    arrivals = get_arrivals_by_target_name()
    destinations = []
    for exit_name, target_name in kh1world.entrance_pairings.items():
        exit_row = rows_by_name[exit_name]
        arrival = arrivals[target_name]
        destination = {
            "world": WORLD_NUMBERS[exit_row["World"]],
            "area": int(exit_row["Area"], 16),
            "exit": int(exit_row["Exit ID"], 16),
        }
        if is_two_way_door(exit_row):
            destination["back"] = int(exit_row["Arrival ID"], 16)
        destination["to_world"] = arrival["to_world"]
        destination["to_area"] = arrival["to_area"]
        destination["to_entrance"] = arrival["to_entrance"]
        destinations.append(destination)
    return destinations
