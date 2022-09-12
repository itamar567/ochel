import math
import random

import constants


def chance(num, out_of=1.0):
    return random.random() * out_of < num


def dmg_type_2_str(dmg_type):
    assert dmg_type != constants.DMG_TYPE_SCYTHE
    if dmg_type == constants.DMG_TYPE_MAGIC:
        return "magic"
    elif dmg_type == constants.DMG_TYPE_MELEE:
        return "melee"
    else:
        return "pierce"


def dmg_type_2_bpd(dmg_type):
    assert dmg_type != constants.DMG_TYPE_SCYTHE
    if dmg_type == constants.DMG_TYPE_MAGIC:
        return "dodge"
    elif dmg_type == constants.DMG_TYPE_MELEE:
        return "block"
    else:
        return "parry"


def add_value(dictionary, key, value, cap=math.inf, dict_of_lists=False):
    if dict_of_lists:
        if key in dictionary:
            dictionary[key].append(value)
            return
        dictionary[key] = [value]
        return

    if key in dictionary.keys():
        dictionary[key] = min(dictionary[key] + value, cap)
        return
    dictionary[key] = min(value, cap)


def check_if_entities_alive(enemies_list, player):
    enemies_alive = len(enemies_list)
    for entity in enemies_list:
        if entity.hp <= 0:
            enemies_alive -= 1
    if enemies_alive == 0:
        return False
    return player.hp > 0


# TODO: fix edge cases (e.g. if 2 mainstats are bigger than the 3rd)
# TODO: if STR=INT=DEX, set damage type based on base class
def determine_damage_type_by_stats(entity):
    if entity.stats.STR == entity.stats.INT == entity.stats.DEX:
        return constants.DMG_TYPE_MAGIC
    else:
        if entity.stats.DEX >= entity.stats.STR and entity.stats.DEX >= entity.stats.INT:
            return constants.DMG_TYPE_PIERCE
        elif entity.stats.INT >= entity.stats.STR and entity.stats.INT >= entity.stats.DEX:
            return constants.DMG_TYPE_MAGIC
        else:
            return constants.DMG_TYPE_MELEE


def stun_chance(entity):
    immobility_resist = entity.resists.get("immobility", 0) + entity.resists.get("all", 0)
    print(immobility_resist)
    chance_to_stun = (100 - immobility_resist) / 100
    chance_to_stun = max(chance_to_stun, 0)
    return chance(chance_to_stun)


def dot_dpt(entity, multiplier):
    return multiplier * entity.damage[0] * entity.dot_multiplier, multiplier * entity.damage[1] * entity.dot_multiplier


def num_to_str_with_plus_minus_sign(num):
    if num < 0:
        return str(num)
    return "+" + str(num)


def get_effect_duration(effect, effect_fade_turn, current_turn):
    for turn in effect_fade_turn.keys():
        if turn < current_turn:
            continue
        for eff in effect_fade_turn[turn]:
            if eff.name == effect.name:
                return turn - current_turn


def player_full_heal(match):
    match.player.attacked(9999999, "health")
