from dataclasses import dataclass

from Options import NamedRange, Choice, Range, Toggle, DefaultOnToggle, PerGameCommonOptions, StartInventoryPool, OptionGroup

class StrengthIncrease(Range):
    """
    Determines the number of Strength Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "STR Increases"
    range_start = 0
    range_end = 100
    default = 24

class DefenseIncrease(Range):
    """
    Determines the number of Defense Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "DEF Increases"
    range_start = 0
    range_end = 100
    default = 24

class HPIncrease(Range):
    """
    Determines the number of HP Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "HP Increases"
    range_start = 0
    range_end = 100
    default = 23

class APIncrease(Range):
    """
    Determines the number of AP Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "AP Increases"
    range_start = 0
    range_end = 100
    default = 18

class MPIncrease(Range):
    """
    Determines the number of MP Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "MP Increases"
    range_start = 0
    range_end = 20
    default = 7

class AccessorySlotIncrease(Range):
    """
    Determines the number of Accessory Slot Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "Accessory Slot Increases"
    range_start = 0
    range_end = 6
    default = 1

class ItemSlotIncrease(Range):
    """
    Determines the number of Item Slot Increases to add to the multiworld.
    
    The randomizer will add all stat ups defined here into a pool and choose up to 100 to add to the multiworld.
    Accessory Slot Increases and Item Slot Increases are prioritized first, then the remaining items (up to 100 total) are chosen at random.
    """
    display_name = "Item Slot Increases"
    range_start = 0
    range_end = 5
    default = 3

class Atlantica(Toggle):
    """
    Toggle whether to include checks in Atlantica.
    """
    display_name = "Atlantica"

class HundredAcreWood(Toggle):
    """
    Toggle whether to include checks in the 100 Acre Wood.
    """
    display_name = "100 Acre Wood"

class SuperBosses(Toggle):
    """
    Toggle whether to include checks behind Super Bosses.
    If Final Rest Door is set to Superbosses these locations are also included.
    """
    display_name = "Super Bosses"

class Cups(Choice):
    """
    Determines which cups have their locations added to the multiworld.
    Please note that the cup items will still appear in the multiworld even if set to off, as they are required to challenge Sephiroth.

    Off: All cup locations are removed
    Cups: Phil, Pegasus, and Hercules cups are included
    Hades Cup: Hades Cup is included in addition to Phil, Pegasus, and Hercules cups. If Super Bosses are enabled, then Ice Titan is included
    """
    display_name = "Cups"
    option_off = 0
    option_cups = 1
    option_hades_cup = 2

class Goal(Choice):
    """
    Determines when victory is achieved in your playthrough.
    
    Sephiroth: Defeat Sephiroth
    Unknown: Defeat Unknown
    Postcards: Turn in an amount of postcards in Traverse Town
    Final Ansem: Enter End of the World and defeat Ansem as normal
    Puppies: Rescue and return an amount of puppies in Traverse Town
    Final Rest: Open the chest in End of the World Final Rest
    """
    display_name = "Goal"
    option_sephiroth = 0
    option_unknown = 1
    option_postcards = 2
    option_final_ansem = 3
    option_puppies = 4
    option_final_rest = 5
    default = 3

class EndoftheWorldUnlock(Choice):
    """Determines how End of the World is unlocked.
    
    Item: You can receive an item called "End of the World" which unlocks the world
    Reports: A certain amount of reports are required to unlock End of the World, which is defined in your options"""
    display_name = "End of the World Unlock"
    option_item = 0
    option_reports = 1
    default = 1

class FinalRestDoor(Choice):
    """Determines what conditions need to be met to manifest the door in Final Rest, allowing the player to challenge Ansem.
    
    Reports: A certain number of Ansem's Reports are required, determined by the "Reports to Open Final Rest Door" option
    Puppies: Having all 99 puppies is required
    Postcards: Turning in all 10 postcards is required
    Superbosses: Defeating Sephiroth, Unknown, Kurt Zisa, and Phantom is required
    """
    display_name = "Final Rest Door"
    option_reports = 0
    option_puppies = 1
    option_postcards = 2
    option_superbosses = 3

class RequiredPostcards(Range):
    """
    If your goal is set to "Postcards", defines how many postcards are needed to achieve victory.
    """
    display_name = "Required Postcards"
    default = 8
    range_start = 1
    range_end = 10

class RequiredPuppies(Choice):
    """
    If your goal is set to "Puppies", defines how many puppies are needed to achieve victory.
    """
    display_name = "Required Puppies"
    default = 80
    option_10 = 10
    option_20 = 20
    option_30 = 30
    option_40 = 40
    option_50 = 50
    option_60 = 60
    option_70 = 70
    option_80 = 80
    option_90 = 90
    option_99 = 99

class Puppies(Choice):
    """
    Determines how dalmatian puppies are shuffled into the pool.
    Full: All 99 puppies are found in a single item.
    Triplets: Puppies are found in 33 triplet "Puppies" items anywhere in the multiworld.
    Individual: Puppies are found in 99 individual "Puppy" items.
    Vanilla: Puppies are found in triplets in the same locations as the vanilla game.
    """
    display_name = "Puppies"
    option_full = 0
    option_triplets = 1
    option_individual = 2
    option_vanilla = 3
    default = 1

class EXPMultiplier(NamedRange):
    """
    Determines the multiplier to apply to EXP gained.
    """
    display_name = "EXP Multiplier"
    default = 16
    range_start = default // 4
    range_end = 128
    special_range_names = {
        "0.25x": int(default // 4),
        "0.5x": int(default // 2),
        "1x": default,
        "2x": default * 2,
        "3x": default * 3,
        "4x": default * 4,
        "8x": default * 8,
    }

class RequiredReportsEotW(Range):
    """
    If End of the World Unlock is set to "Reports", determines the number of Ansem's Reports required to open End of the World.
    """
    display_name = "Reports to Open End of the World"
    default = 4
    range_start = 0
    range_end = 13

class RequiredReportsDoor(Range):
    """
    If Final Rest Door is set to "Reports", determines the number of Ansem's Reports required to manifest the door in Final Rest to challenge Ansem.
    """
    display_name = "Reports to Open Final Rest Door"
    default = 4
    range_start = 0
    range_end = 13

class ReportsInPool(Range):
    """
    Determines the number of Ansem's Reports in the item pool.
    """
    display_name = "Reports in Pool"
    default = 4
    range_start = 0
    range_end = 13

class KeybladeStats(Choice):
    """
    Determines whether Keyblade stats should be randomized.
    Randomize: Randomly generates STR and MP bonuses for each keyblade between the defined minimums and maximums
    Shuffle: Shuffles the stats of the vanilla keyblade amongst each other.
    Vanilla: Keyblade stats are unchanged.
    """
    display_name = "Keyblade Stats"
    option_randomize = 0
    option_shuffle = 1
    option_vanilla = 2

class KeybladeMinStrength(Range):
    """
    Determines the minimum STR bonus a keyblade can have.
    """
    display_name = "Keyblade Minimum STR Bonus"
    default = 3
    range_start = 0
    range_end = 20

class KeybladeMaxStrength(Range):
    """
    Determines the maximum STR bonus a keyblade can have.
    """
    display_name = "Keyblade Maximum STR Bonus"
    default = 14
    range_start = 0
    range_end = 20

class KeybladeMinMP(Range):
    """
    Determines the minimum MP bonus a keyblade can have.
    """
    display_name = "Keyblade Minimum MP Bonus"
    default = -2
    range_start = -2
    range_end = 5

class KeybladeMaxMP(Range):
    """
    Determines the maximum MP bonus a keyblade can have.
    """
    display_name = "Keyblade Maximum MP Bonus"
    default = 3
    range_start = -2
    range_end = 5

class LevelChecks(Range):
    """
    Determines the maximum level for which checks can be obtained.
    """
    display_name = "Level Checks"
    default = 100
    range_start = 0
    range_end = 100

class ForceStatsOnLevels(NamedRange):
    """
    If this value is less than the value for Level Checks, this determines the minimum level from which only stat ups are obtained at level up locations.
    For example, if you want to be able to find any multiworld item from levels 1-50, then just stat ups for levels 51-100, set this value to 51.
    """
    display_name = "Force Stats on Level Starting From"
    default = 1
    range_start = 1
    range_end = 101
    special_range_names = {
        "none": 101,
        "multiworld-to-level-50": 51,
        "all": 1
    }

class BadStartingWeapons(Toggle):
    """
    Forces Kingdom Key, Dream Sword, Dream Shield, and Dream Staff to have vanilla stats.
    """
    display_name = "Bad Starting Weapons"

class DonaldDeathLink(Toggle):
    """
    If Donald is KO'ed, so is Sora.  If Death Link is toggled on in your client, this will send a death to everyone.
    """
    display_name = "Donald Death Link"

class GoofyDeathLink(Toggle):
    """
    If Goofy is KO'ed, so is Sora.  If Death Link is toggled on in your client, this will send a death to everyone.
    """
    display_name = "Goofy Death Link"

class KeybladesUnlockChests(Toggle):
    """
    If toggled on, the player is required to have a certain keyblade to open chests in certain worlds.
    TT   - Lionheart
    WL   - Lady Luck
    OC   - Olympia
    DJ   - Jungle King
    AG   - Three Wishes
    MS   - Wishing Star
    HT   - Pumpkinhead
    NL   - Fairy Harp
    HB   - Divine Rose
    EotW - Oblivion
    HAW  - Oathkeeper
    
    Note: Does not apply to Atlantica, the emblem and carousel chests in Hollow Bastion, or the Aero chest in Neverland currently.
    """
    display_name = "Keyblades Unlock Chests"

class InteractInBattle(Toggle):
    """
    Allow Sora to talk to people, examine objects, and open chests in battle.
    """
    display_name = "Interact in Battle"

class AdvancedLogic(Toggle):
    """
    If on, logic may expect you to do advanced skips like using Combo Master, Dumbo, and other unusual methods to reach locations.
    """
    display_name = "Advanced Logic"

class ExtraSharedAbilities(Toggle):
    """
    If on, adds extra shared abilities to the pool.  These can stack, so multiple high jumps make you jump higher and multiple glides make you superglide faster.
    """
    display_name = "Extra Shared Abilities"

class EXPZeroInPool(Toggle):
    """
    If on, adds EXP Zero ability to the item pool.  This is redundant if you are planning on playing on Proud.
    """
    display_name = "EXP Zero in Pool"

class RandomizeEmblemPieces(Toggle):
    """
    If off, the Hollow Bastion emblem pieces are in their vanilla locations.
    """
    display_name = "Randomize Emblem Pieces"

class RandomizePostcards(Choice):
    """
    Determines how Postcards are randomized

    All: All Postcards are randomized
    Chests: Only the 3 Postcards in chests are randomized
    Vanilla: Postcards are in their original locations
    """
    display_name = "Randomize Postcards"
    option_all = 0
    option_chests = 1
    option_vanilla = 2

class JungleSlider(Toggle):
    """
    Determines whether checks are behind the Jungle Slider minigame.
    """
    display_name = "Jungle Slider"

class StartingWorlds(Range):
    """
    Number of random worlds to start with in addition to Traverse Town, which is always available.  Will only consider Atlantica if toggled, and will only consider End of the World if its unlock is set to "Item".
    """
    display_name = "Starting Worlds"
    default = 0
    range_start = 0
    range_end = 10
    
class StartingTools(DefaultOnToggle):
    """
    Determines whether you start with Scan and Dodge Roll.
    """
    display_name = "Starting Tools"

@dataclass
class KH1Options(PerGameCommonOptions):
    goal: Goal
    end_of_the_world_unlock: EndoftheWorldUnlock
    final_rest_door: FinalRestDoor
    required_reports_eotw: RequiredReportsEotW
    required_reports_door: RequiredReportsDoor
    reports_in_pool: ReportsInPool
    required_postcards: RequiredPostcards
    required_puppies: RequiredPuppies
    super_bosses: SuperBosses
    atlantica: Atlantica
    hundred_acre_wood: HundredAcreWood
    cups: Cups
    puppies: Puppies
    starting_worlds: StartingWorlds
    keyblades_unlock_chests: KeybladesUnlockChests
    interact_in_battle: InteractInBattle
    exp_multiplier: EXPMultiplier
    advanced_logic: AdvancedLogic
    extra_shared_abilities: ExtraSharedAbilities
    exp_zero_in_pool: EXPZeroInPool
    randomize_emblem_pieces: RandomizeEmblemPieces
    randomize_postcards: RandomizePostcards
    donald_death_link: DonaldDeathLink
    goofy_death_link: GoofyDeathLink
    keyblade_stats: KeybladeStats
    bad_starting_weapons: BadStartingWeapons
    keyblade_min_str: KeybladeMinStrength
    keyblade_max_str: KeybladeMaxStrength
    keyblade_min_mp: KeybladeMinMP
    keyblade_max_mp: KeybladeMaxMP
    level_checks: LevelChecks
    force_stats_on_levels: ForceStatsOnLevels
    strength_increase: StrengthIncrease
    defense_increase: DefenseIncrease
    hp_increase: HPIncrease
    ap_increase: APIncrease
    mp_increase: MPIncrease
    accessory_slot_increase: AccessorySlotIncrease
    item_slot_increase: ItemSlotIncrease
    start_inventory_from_pool: StartInventoryPool
    jungle_slider: JungleSlider
    starting_tools: StartingTools

kh1_option_groups = [
    OptionGroup("Goal", [
        Goal,
        EndoftheWorldUnlock,
        FinalRestDoor,
        RequiredReportsDoor,
        RequiredReportsEotW,
        ReportsInPool,
        RequiredPostcards,
        RequiredPuppies,
    ]),
    OptionGroup("Locations", [
        SuperBosses,
        Atlantica,
        Cups,
        HundredAcreWood,
        JungleSlider,
        RandomizeEmblemPieces,
        RandomizePostcards,
    ]),
    OptionGroup("Levels", [
        EXPMultiplier,
        LevelChecks,
        ForceStatsOnLevels,
        StrengthIncrease,
        DefenseIncrease,
        HPIncrease,
        APIncrease,
        MPIncrease,
        AccessorySlotIncrease,
        ItemSlotIncrease,
    ]),
    OptionGroup("Keyblades", [
        KeybladesUnlockChests,
        KeybladeStats,
        BadStartingWeapons,
        KeybladeMaxStrength,
        KeybladeMinStrength,
        KeybladeMaxMP,
        KeybladeMinMP,
    ]),
    OptionGroup("Misc", [
        StartingWorlds,
        StartingTools,
        Puppies,
        InteractInBattle,
        AdvancedLogic,
        ExtraSharedAbilities,
        EXPZeroInPool,
        DonaldDeathLink,
        GoofyDeathLink,
    ])
]
