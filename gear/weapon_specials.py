import constants
import misc


class WeaponSpecial:
    def __init__(self, name, identifier, default=False,
                 on_hit_func=None, on_hit_apply_time=constants.ON_HIT_APPLY_AFTER_HIT, on_hit_chance=0.0, on_hit_messages=None,
                 on_attack_func=None, on_attack_chance=0.0):
        self.name = f"{name} (Special)"
        self.identifier = identifier
        self.default = default
        self.on_hit_func = on_hit_func
        self.on_hit_apply_time = on_hit_apply_time
        self.on_hit_chance = on_hit_chance
        self.on_hit_messages = on_hit_messages
        self.on_attack_func = on_attack_func
        self.on_attack_chance = on_attack_chance


weapon_specials = {}


def _ice_scythe_on_hit(match, entity, damage):
    entity.add_effect(misc.Effect("Icy Chill", "ice_scythe_on_hit_icy_chill", 3, {}, {"ice": -30}))
    return damage


def _blade_of_destiny_on_attack(match):
    match.targeted_enemy.add_effect(misc.Effect("Weakness", "blade_of_destiny_on_attack_weakness", 5, {}, {"light": -30}))
    for i in range(3):
        match.player.attack(match.targeted_enemy, damage_multiplier=0.75, element="light")


def _blade_of_destiny_90_on_hit(match, entity, damage):
    entity.add_effect(misc.Effect("Overwhelming Light", "blade_of_destiny_90_on_hit_overwhelming_light", 3, {}, {"light": -30}))
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
weapon_specials["ice_scythe"] = WeaponSpecial("Ice Scythe", "ice_scythe", on_hit_func=_ice_scythe_on_hit, on_hit_apply_time=constants.ON_HIT_APPLY_BEFORE_HIT, on_hit_chance=7/100, on_hit_messages=["The power locked inside the scythe chills your foe!"])
weapon_specials["blade_of_destiny_80"] = WeaponSpecial("Blade of Destiny (Level 80)", "blade_of_destiny_80", on_attack_func=_blade_of_destiny_on_attack, on_attack_chance=20/100)
weapon_specials["blade_of_destiny_90"] = WeaponSpecial("Blade of Destiny (Level 90)", "blade_of_destiny_90", on_hit_func=_blade_of_destiny_90_on_hit, on_hit_apply_time=constants.ON_HIT_APPLY_BEFORE_HIT, on_hit_chance=7/100, on_hit_messages=["The light spirit inside your blade shines brightly!"], on_attack_func=_blade_of_destiny_on_attack, on_attack_chance=7/100)

# On-Attack
weapon_specials["aww_weapon"] = WeaponSpecial("Aww Weapon", "aww_weapon", on_attack_func=_aww_weapon_on_attack, on_attack_chance=5/100)
weapon_specials["creatioux_claw"] = WeaponSpecial("Creatioux Claw", "creatioux_claw", on_attack_func=_creatioux_claw_on_attack, on_attack_chance=33/100)
weapon_specials["frozen_weapon"] = WeaponSpecial("Frozen Weapon", "frozen_weapon", on_attack_func=_frozen_weapon_on_attack, on_attack_chance=5/100)
weapon_specials["necrotic_sword_of_doom"] = WeaponSpecial("Necrotic Sword of Doom", "necrotic_sword_of_doom", on_attack_func=_necrotic_sword_of_doom_on_attack, on_attack_chance=5/100)
weapon_specials["vanilla_ice_katana"] = WeaponSpecial("Vanilla Ice Katana", "vanilla_ice_katana", on_attack_func=_vanilla_ice_katana_on_attack, on_attack_chance=20/100)
