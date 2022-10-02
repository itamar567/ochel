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


trinkets["the_corrupted_seven"] = Trinket("The Corrupted Seven", "the_corrupted_seven", {"crit": 5, "WIS": 5, "END": 5, "CHA": 5, "LUK": 5, "INT": 8, "DEX": 8, "STR": 8, "bonus": 5}, {"all": 4, "health": -4}, ability_func=_the_corrupted_seven_ability_func, ability_cooldown=34, ability_mana_cost=30, ability_name="Seven")
