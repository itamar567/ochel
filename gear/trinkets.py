import misc
from gear.gear import Trinket

trinkets = {}


def _the_corrupted_seven_ability_func(match):
    match.player.add_effect(misc.Effect("Empowered", "the_corrupted_seven_empowered", 4, {"boost": 5}, {}))
    for i in range(5):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="poison")
    for i in range(6):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="darkness")
    for i in range(7):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="energy")
    for i in range(5):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="fire")
    for i in range(8):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="wind")
    for i in range(1):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="nature")
    for i in range(2):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/34, element="water")


def _elemental_unity_func(match):
    for i in range(17):
        match.player.attack(match.targeted_enemy, damage_multiplier=2/17, element="good", inflicts=[misc.Effect("Blinded", "elemental_unity_blinded", 3, {"bonus": -30}, {})])


trinkets["empty_trinket"] = Trinket("None", "empty_trinket", {}, {})
trinkets["the_corrupted_seven"] = Trinket("The Corrupted Seven", "the_corrupted_seven", {"crit": 5, "WIS": 5, "END": 5, "CHA": 5, "LUK": 5, "INT": 8, "DEX": 8, "STR": 8, "bonus": 5}, {"all": 4, "health": -4}, ability_func=_the_corrupted_seven_ability_func, ability_cooldown=34, ability_mana_cost=30, ability_name="Seven")
trinkets["elemental_unity_defender_15"] = Trinket("Elemental Unity Defender XV", "elemental_unity_defender_15", {"block": 1, "bpd": 1, "crit": 6, "mpm": 5, "WIS": 6, "END": 5, "CHA": 6, "LUK": 6, "INT": 7, "DEX": 7, "STR": 7, "bonus": 7}, {"all": 5, "health": -5}, ability_func=_elemental_unity_func, ability_cooldown=29, ability_mana_cost=10, ability_name="Unity", ability_img_name="elemental_unity")
