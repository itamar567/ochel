import random

import constants
import misc
import utilities


class WeaponSpecial:
    def __init__(self, name, identifier, default=False,
                 on_hit_func=None, on_hit_apply_time=constants.ON_HIT_APPLY_BEFORE_HIT, on_hit_chance=0.0, on_hit_messages=None, on_hit_bonuses_func=None,
                 on_attack_func=None, on_attack_chance=0.0):
        self.name = f"{name} (Special)"
        self.original_name = name
        self.identifier = f"{identifier}_special"
        self.default = default
        self.on_hit_func = on_hit_func
        self.on_hit_apply_time = on_hit_apply_time
        self.on_hit_chance = on_hit_chance
        if on_hit_messages is None:
            self.on_hit_messages = []
        else:
            self.on_hit_messages = on_hit_messages
        if on_hit_bonuses_func is None:
            self.on_hit_bonuses_func = lambda match, entity: {}
        else:
            self.on_hit_bonuses_func = on_hit_bonuses_func
        self.on_attack_func = on_attack_func
        self.on_attack_chance = on_attack_chance


weapon_specials = {}


def _dragon_blade_on_hit(match, entity, damage):
    if entity.race == "reptilian":
        return damage * 1.1
    if entity.race == "dragon":
        return damage * 1.15
    return damage


def _dragon_blade_on_hit_bonuses(match, entity):
    if entity.race == "reptilian":
        return {"bonus": 10}
    if entity.race == "dragon":
        return {"bonus": 15}
    return {}


def _dragonblaser_on_hit(match, entity, damage):
    if entity.race == "reptilian":
        return damage * 1.15
    if entity.race == "dragon":
        return damage * 1.3
    return damage


def _escelense_blade_on_hit(match, entity, damage):
    if entity.race == "elemental":
        return damage * 1.3
    return damage


def _zardslayer_blade_on_hit(match, entity, damage):
    if entity.race == "reptilian":
        return damage * 1.3
    return damage


def _light_of_destiny_on_hit_bonuses(match, entity):
    if entity.race == "undead":
        return {"bonus": 20, "crit": 20}
    return {}


def _spiders_embrace_on_hit(match, entity, damage):
    if entity.race == "bug":
        return 1.2 * damage
    return damage


def _vile_infused_rose_weapon_on_hit(match, entity, damage):
    if entity.race == "human":
        return damage * 1.1
    return damage


def _lucky_hammer_on_hit_bonuses(match, entity):
    return {"crit_multiplier": 0.1}


def _pandoras_scythe_on_hit(match, entity, damage):
    return damage * 1.2


def _ruby_spike_on_hit(match, entity, damage):
    return damage * 1.1


def _thorn_replica_on_hit_bonuses(match, entity):
    return {"crit_multiplier": 0.05}


def _light_of_ebil_dread_on_hit_bonuses(match, entity):
    return {"non_crit_multiplier": 0.05}


def _roliths_backup_hammer_on_hit_bonuses(match, entity):
    utilities.add_value(match.on_hit_data, "roliths_backup_hammer", 1)
    if match.on_hit_data["roliths_backup_hammer"] == 10:
        match.on_hit_data["roliths_backup_hammer"] = 0
        return {"crit": 200}
    return {}


def _destiny_weapon_on_hit(match, entity, damage):
    dot_dpt = utilities.dot_dpt(match.player, 0.2)
    entity.add_effect(misc.Effect("Destiny", "destiny_weapon_on_hit_destiny", 5, {}, {}, dot=misc.DoT(dot_dpt[0], dot_dpt[1], "light", match.player)))
    return damage


def _doom_weapon_on_hit(match, entity, damage):
    dot_dpt = utilities.dot_dpt(match.player, 0.2)
    entity.add_effect(misc.Effect("Doooom", "doom_weapon_on_hit_doooom", 5, {}, {}, dot=misc.DoT(dot_dpt[0], dot_dpt[1], "darkness", match.player)))
    return damage


def _fourth_of_july_weapon_on_hit(match, entity, damage):
    random_num = random.randint(0, 2)
    if random_num == 0:
        element = "Fire"
    elif random_num == 1:
        element = "Ice"
    else:
        element = "Water"
    dot_dpt = utilities.dot_dpt(match.player, 0.4)
    entity.add_effect(misc.Effect(f"Spirit of {element}", "fourth_of_july_weapon_on_hit_dot", 5, {}, {}, dot=misc.DoT(dot_dpt[0], dot_dpt[1], element.lower(), match.player)))
    return damage


def _amulet_weapon_on_hit(match, entity, damage):
    match.player.add_effect(misc.Effect("Dragon Magic", "amulet_weapon_dragon_magic", 5, {"boost": 7}, {}))
    return damage


def _ancient_frost_moglin_weapon_on_hit(match, entity, damage):
    entity.add_effect(misc.Effect("Ancient Chill", "ancient_frost_moglin_weapon_ancient_chill", 10, {}, {"health": 10}))
    return damage


def _doom_blade_of_sorrows_on_hit(match, entity, damage):
    entity.add_effect(misc.Effect("Doomed", "doom_blade_of_sorrows_on_hit_doomed", 2, {"boost": -20}, {}))
    return damage


def _blade_of_awe_on_hit(match, entity, damage):
    match.player.attacked(0.04 * match.player.max_hp, "health", entity=match.player)
    match.player.mp = utilities.clamp(match.player.mp + 0.04 * match.player.max_mp, 0, match.player.max_mp)
    return damage


def _frostval_weapon_on_hit(match, entity, damage):
    match.player.attacked(0.05 * match.player.max_hp, "health", entity=match.player)
    return damage


def _the_quadstaff_on_hit(match, entity, damage):
    match.player.mp = utilities.clamp(match.player.mp + match.player.level * 0.75, 0, match.player.max_mp)
    return damage


def _twillys_staff_on_hit(match, entity, damage):
    dot_dpt = utilities.dot_dpt(match.player, 0.6)
    match.player.add_effect(misc.Effect("Moglin Healing Magic", "twillys_staff_on_hit_moglin_healing_magic", 4, {}, {}, dot=misc.DoT(dot_dpt[0], dot_dpt[1], "health", match.player)))
    return damage


def _warlics_gift_on_hit(match, entity, damage):
    match.player.mp = utilities.clamp(match.player.mp + 0.08 * match.player.max_mp, 0, match.player.max_mp)
    return damage


def _blade_of_destiny_on_attack(match):
    match.targeted_enemy.add_effect(misc.Effect("Weakness", "blade_of_destiny_on_attack_weakness", 5, {}, {"light": -30}))
    for i in range(3):
        match.player.attack(match.targeted_enemy, damage_multiplier=0.75, element="light")


def _blade_of_destiny_90_on_hit(match, entity, damage):
    entity.add_effect(misc.Effect("Overwhelming Light", "blade_of_destiny_90_on_hit_overwhelming_light", 3, {}, {"light": -30}))
    return damage


def _hearts_whisper_on_hit(match, entity, damage):
    effect = misc.Effect("Heart's Pull", "hearts_whisper_on_hit_hearts_pull", 3, {"mpm": -50}, {})
    match.player.add_effect(effect)
    entity.add_effect(effect)
    return damage


def _ice_scythe_on_hit(match, entity, damage):
    entity.add_effect(misc.Effect("Icy Chill", "ice_scythe_on_hit_icy_chill", 3, {}, {"ice": -30}))
    return damage


def _aww_weapon_on_attack(match):
    dot_value = round(match.player.max_hp / 10)
    match.player.add_effect(misc.Effect("Mend", "aww_replica_weapons_on_attack_mend_hot", 3, {}, {}, dot=misc.DoT(dot_value, dot_value, "health", match.player)))
    match.targeted_enemy.add_effect(misc.Effect("Mend", "aww_replica_weapons_on_attack_mend_dot", 3, {}, {}, dot=misc.DoT(dot_value, dot_value, "darkness", match.player)))
    match.player.attack(match.targeted_enemy)


def _creatioux_claw_on_attack(match):
    match.player.attack(match.targeted_enemy, inflicts=[misc.Effect("Void Scar", "creatioux_claw_on_attack_void_scar", 3, {}, {"health": 20})])


def _frozen_weapon_on_attack(match):
    match.player.add_effect(misc.Effect("Strengthen", "frozen_weapon_on_attack_strengthen", 5, {}, {"fire": 10}))
    match.targeted_enemy.add_effect(misc.Effect("Weaken", "frozen_weapon_on_attack_weaken", 5, {}, {"ice": -50}))
    match.player.attack(match.targeted_enemy)


def _necrotic_sword_of_doom_on_attack(match):
    for i in range(12):
        match.player.attack(match.targeted_enemy, damage_multiplier=0.25)


def _vanilla_ice_katana_on_attack(match):
    match.targeted_enemy.add_effect(misc.Effect("Weaken", "vanilla_ice_katana_on_attack_weaken", 5, {}, {"ice": -30}))
    match.player.attack(match.targeted_enemy, damage_multiplier=3)


# On-Hit
# - Racial Triggers
weapon_specials["dragon_blade_special"] = WeaponSpecial("Dragon Blade", "dragon_blade", on_hit_chance=1, on_hit_func=_dragon_blade_on_hit, on_hit_bonuses_func=_dragon_blade_on_hit_bonuses)
weapon_specials["dragonblaser_special"] = WeaponSpecial("DragonBlaser", "dragonblaser", on_hit_chance=1, on_hit_func=_dragonblaser_on_hit)
weapon_specials["escelense_blade_special"] = WeaponSpecial("Escelense Blade", "escelense_blade", on_hit_chance=1, on_hit_func=_escelense_blade_on_hit)
weapon_specials["zardslayer_blade_special"] = WeaponSpecial("ZardSlayer Blade", "zardslayer_blade", on_hit_chance=1, on_hit_func=_zardslayer_blade_on_hit)
weapon_specials["light_of_destiny_special"] = WeaponSpecial("Light of Destiny", "light_of_destiny", on_hit_chance=1, on_hit_bonuses_func=_light_of_destiny_on_hit_bonuses)
weapon_specials["spiders_embrace_special"] = WeaponSpecial("Spider's Embrace", "spiders_embrace", on_hit_chance=1, on_hit_func=_spiders_embrace_on_hit)
weapon_specials["vile_infused_rose_weapon_special"] = WeaponSpecial("Vile Infused Rose Weapon", "vile_infused_rose_weapon", on_hit_chance=1, on_hit_func=_vile_infused_rose_weapon_on_hit)

# - Extra Damage
weapon_specials["lucky_hammer_special"] = WeaponSpecial("Lucky Hammer", "lucky_hammer", on_hit_chance=1, on_hit_bonuses_func=_lucky_hammer_on_hit_bonuses)
weapon_specials["pandoras_scythe_special"] = WeaponSpecial("Pandora's Scythe", "pandoras_scythe", on_hit_chance=5/100, on_hit_func=_pandoras_scythe_on_hit, on_hit_messages=["Pandora's Scythe flares!"])
weapon_specials["ruby_spike_special"] = WeaponSpecial("Ruby Spike", "ruby_spike", on_hit_chance=15/100, on_hit_func=_ruby_spike_on_hit)
weapon_specials["thorn_replica_special"] = WeaponSpecial("Thorn Replica", "thorn_replica", on_hit_chance=1, on_hit_bonuses_func=_thorn_replica_on_hit_bonuses)
weapon_specials["light_of_ebil_dread_special"] = WeaponSpecial("Light of Ebil Dread", "light_of_ebil_dread", on_hit_chance=1, on_hit_bonuses_func=_light_of_ebil_dread_on_hit_bonuses)
weapon_specials["roliths_backup_hammer_special"] = WeaponSpecial("Rolith's Backup Hammer", "roliths_backup_hammer", on_hit_chance=1, on_hit_bonuses_func=_roliths_backup_hammer_on_hit_bonuses)

# - DoTs
weapon_specials["destiny_weapon_special"] = WeaponSpecial("Destiny Weapon", "destiny_weapon", on_hit_chance=5/100, on_hit_func=_destiny_weapon_on_hit, on_hit_messages=["Your foe is infused with Light!"])
weapon_specials["doom_weapon_special"] = WeaponSpecial("Doom Weapon", "doom_weapon", on_hit_chance=5/100, on_hit_func=_doom_weapon_on_hit, on_hit_messages=["Doom Weapon: Hahaha!! Engulfed by Darkness!"])
weapon_specials["fourth_of_july_weapon_special"] = WeaponSpecial("Fourth of July Weapon", "fourth_of_july_weapon", on_hit_chance=10/100, on_hit_func=_fourth_of_july_weapon_on_hit, on_hit_messages=["Spirit of Liberty!"])

# - (De)buffs
weapon_specials["amulet_weapon_special"] = WeaponSpecial("Amulet Weapon", "amulet_weapon", on_hit_chance=10/100, on_hit_func=_amulet_weapon_on_hit, on_hit_messages=["Dragon Magic!!"], on_hit_apply_time=constants.ON_HIT_APPLY_NEXT_TURN)
weapon_specials["ancient_frost_moglin_weapon_special"] = WeaponSpecial("Ancient Frost Moglin Weapon", "ancient_frost_moglin_weapon", on_hit_chance=5/100, on_hit_func=_ancient_frost_moglin_weapon_on_hit, on_hit_messages=["The magic of Ancient Frost Moglins reduces your foe's healing!"], on_hit_apply_time=constants.ON_HIT_APPLY_AFTER_HIT)
weapon_specials["doom_blade_of_sorrows_special"] = WeaponSpecial("Doom Blade of Sorrows", "doom_blade_of_sorrows", on_hit_chance=5/100, on_hit_func=_doom_blade_of_sorrows_on_hit, on_hit_messages=["Your foe cowers before your power!"])
weapon_specials["blade_of_destiny_90_special"] = WeaponSpecial("Blade of Destiny (Level 90)", "blade_of_destiny_90", on_hit_func=_blade_of_destiny_90_on_hit, on_hit_chance=7/100, on_hit_messages=["The light spirit inside your blade shines brightly!"], on_attack_func=_blade_of_destiny_on_attack, on_attack_chance=7/100)
weapon_specials["hearts_whisper_special"] = WeaponSpecial("Heart's Whisper", "hearts_whisper", on_hit_chance=5/100, on_hit_func=_hearts_whisper_on_hit, on_hit_messages=["Hearts have been entwined."])
weapon_specials["ice_scythe_special"] = WeaponSpecial("Ice Scythe", "ice_scythe", on_hit_func=_ice_scythe_on_hit, on_hit_chance=7/100, on_hit_messages=["The power locked inside the scythe chills your foe!"])

# - Healing
weapon_specials["blade_of_awe_special"] = WeaponSpecial("Blade of Awe", "blade_of_awe", on_hit_chance=5/100, on_hit_func=_blade_of_awe_on_hit, on_hit_messages=["Your blade regenerates a small portion of your health and mana!"])
weapon_specials["frostval_weapon_special"] = WeaponSpecial("Frostval Weapon", "frostval_weapon", on_hit_chance=5/100, on_hit_func=_frostval_weapon_on_hit)
weapon_specials["the_quadstaff_special"] = WeaponSpecial("The Quadstaff", "the_quadstaff", on_hit_chance=5/100, on_hit_func=_the_quadstaff_on_hit, on_hit_messages=["The power of the Quadforce replenishes a small portion of your MP!"])
weapon_specials["twillys_staff_special"] = WeaponSpecial("Twilly's Staff", "twillys_staff", on_hit_chance=5/100, on_hit_func=_twillys_staff_on_hit, on_hit_messages=["Moglin Healing Magic!"])
weapon_specials["warlics_gift_special"] = WeaponSpecial("Warlic's Gift", "warlics_gift", on_hit_chance=5/100, on_hit_func=_warlics_gift_on_hit, on_hit_messages=["The staff recovers a small portion of your MP."])

# On-Attack
weapon_specials["aww_weapon_special"] = WeaponSpecial("Aww Weapon", "aww_weapon", on_attack_func=_aww_weapon_on_attack, on_attack_chance=5/100)
weapon_specials["creatioux_claw_special"] = WeaponSpecial("Creatioux Claw", "creatioux_claw", on_attack_func=_creatioux_claw_on_attack, on_attack_chance=33/100)
weapon_specials["frozen_weapon_special"] = WeaponSpecial("Frozen Weapon", "frozen_weapon", on_attack_func=_frozen_weapon_on_attack, on_attack_chance=5/100)
weapon_specials["necrotic_sword_of_doom_special"] = WeaponSpecial("Necrotic Sword of Doom", "necrotic_sword_of_doom", on_attack_func=_necrotic_sword_of_doom_on_attack, on_attack_chance=5/100)
weapon_specials["vanilla_ice_katana_special"] = WeaponSpecial("Vanilla Ice Katana", "vanilla_ice_katana", on_attack_func=_vanilla_ice_katana_on_attack, on_attack_chance=20/100)
weapon_specials["blade_of_destiny_80_special"] = WeaponSpecial("Blade of Destiny (Level 80)", "blade_of_destiny_80", on_attack_func=_blade_of_destiny_on_attack, on_attack_chance=20/100)