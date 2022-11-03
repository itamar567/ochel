import math
import random
import sys
import os

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


def determine_damage_type_by_stats(entity):
    if entity.stats.STR == entity.stats.INT == entity.stats.DEX:
        return constants.DMG_TYPE_MAGIC
    else:
        if entity.stats.INT >= entity.stats.STR and entity.stats.INT >= entity.stats.DEX:
            return constants.DMG_TYPE_MAGIC
        if entity.stats.DEX >= entity.stats.STR and entity.stats.DEX >= entity.stats.INT:
            return constants.DMG_TYPE_PIERCE
        else:
            return constants.DMG_TYPE_MELEE


def stun_chance(entity):
    immobility_gear_resist = entity.gear_resists.get("immobility", 0) + entity.gear_resists.get("all", 0)
    immobility_general_resist = entity.general_resists.get("immobility", 0) + entity.general_resists.get("all", 0)
    immobility_resist = immobility_gear_resist + immobility_general_resist
    chance_to_stun = (100 - immobility_resist) / 100
    chance_to_stun = max(chance_to_stun, 0)
    return chance(chance_to_stun)


def dot_dpt(entity, multiplier, stat=False):
    if stat:
        stat_damage = math.ceil(3.125 * math.sqrt(entity.stats.get_by_dmg_type(entity.dmg_type) / 2.5) - 5)
    else:
        stat_damage = 0
    damage = (round(entity.damage[0] * multiplier) + round(stat_damage * multiplier), round(entity.damage[1] * multiplier) + round(stat_damage * multiplier))
    return round(entity.dot_multiplier * damage[0]), round(entity.dot_multiplier * damage[1])


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


def copy_dict(dict_to_copy):
    new_dict = {}
    for key in dict_to_copy.keys():
        new_dict[key] = dict_to_copy[key].copy()
    return new_dict


def clamp(value, minimum, maximum):
    return min(maximum, max(value, minimum))


def get_weakness_element(entity, default):
    element = default
    resist = entity.gear_resists.get(default, 0) + entity.general_resists.get(default, 0)
    element_list = list(entity.general_resists.keys())
    element_list.extend(list(entity.gear_resists.keys()))
    for elem in element_list:
        if elem in ("immobility", "health", "shrink", "all"):
            continue
        current_resist = entity.gear_resists.get(elem, 0) + entity.general_resists.get(elem, 0)
        if current_resist < resist:
            element = elem
            resist = current_resist
    return element


def stuffed(player):
    for effect in player.effects:
        if effect.identifier == "food_stuffed":
            return True
    return False


def select_all(event):
    event.widget.select_range(0, "end")
    event.widget.icursor("end")
    return "break"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
