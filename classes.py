import math
import random
import tkinter
import types

import constants
import utilities


class MainStats:
    def __init__(self, stats_list):
        self.STR = stats_list[0]
        self.DEX = stats_list[1]
        self.INT = stats_list[2]
        self.CHA = stats_list[3]
        self.LUK = stats_list[4]
        self.END = stats_list[5]
        self.WIS = stats_list[6]

    def __repr__(self):
        result = ""
        for stat in self.to_list():
            if stat[0] != 0:
                if result != "":
                    result += ", "
                result += f"{stat[0]} {stat[1]}"
        return result

    def copy(self):
        return MainStats([self.STR, self.DEX, self.INT, self.CHA, self.LUK, self.END, self.WIS])

    def add_by_str(self, stat, value):
        if stat == "STR":
            self.STR += value
        elif stat == "DEX":
            self.DEX += value
        elif stat == "INT":
            self.INT += value
        elif stat == "CHA":
            self.CHA += value
        elif stat == "LUK":
            self.LUK += value
        elif stat == "END":
            self.END += value
        else:
            self.WIS += value

    def get_by_dmg_type(self, dmg_type):
        if dmg_type == constants.DMG_TYPE_MAGIC:
            return self.INT
        elif dmg_type == constants.DMG_TYPE_MELEE:
            return self.STR
        else:
            return self.INT

    def to_list(self):
        return [(self.STR, "STR"), (self.DEX, "DEX"), (self.INT, "INT"), (self.CHA, "CHA"), (self.LUK, "LUK"), (self.END, "END"), (self.WIS, "WIS")]


class PetStats:
    def __init__(self, stats_list):
        self.protection = stats_list[0]
        self.magic = stats_list[1]
        self.fighting = stats_list[2]
        self.assistance = stats_list[3]
        self.mischief = stats_list[4]

    def __repr__(self):
        result = ""
        for stat in self.to_list():
            if stat[0] != 0:
                if result != "":
                    result += ", "
                result += f"{stat[0]} {stat[1]}"
        return result

    def to_list(self):
        return [(self.protection, "Protection"), (self.magic, "Magic"), (self.fighting, "Fighting"), (self.assistance, "Assistance"), (self.mischief, "Mischief")]


class Pet:
    def __init__(self, name, player):
        """
        :param name: Name of the pet
        :param player: The player
        """

        self.element = "fire"
        self.name = name
        self.level = player.level
        self.match = player.match
        self.bonuses = {"crit_multiplier": 1.75}
        self.damage = (player.stats.CHA//10, player.stats.CHA//10)
        self.skills = {}
        self.skill_images = {}
        self.skill_names = {}
        self.cooldowns = {}
        self.active_cooldowns = {}
        self.waking_up = False
        self.armor = "???"

        # Can be used by the entity to store the effects that it can apply/inflict
        self.available_effects = types.SimpleNamespace()

        # Rollback data
        self.rollback_cooldown = [self.active_cooldowns.copy()]
        self.rollback_waking_up = [self.waking_up]

    def update_skill_images(self):
        """
        Updates the skill_images dict.
        """
        for skill in self.skills.keys():
            file_name = "images/"
            if skill == " ":
                file_name += "attack"
            elif skill == "M":
                file_name += "skip"
            else:
                file_name += f"{self.armor.replace(' ', '_').lower()}/{skill}"
            self.skill_images[skill] = tkinter.PhotoImage(file=f"{file_name}.png")

    def attack(self, entity, damage_multiplier=1.0, damage_additive=0.0, multiply_first=False,
               dmg_type=constants.DMG_TYPE_MAGIC):
        """
        Attacks an entity.
        :param entity: The entity to attack
        :param damage_multiplier: Multiplies the base damage
        :param damage_additive: Added to the base damage
        :param multiply_first: If True, the base damage will first be multiplied by damage_multiplier, then added to the damage_additive. else, first added then multiplied
        :param dmg_type: The damage type to attack the entity with. can be one of the three: constants.DMG_TYPE_(MELEE/PIERCE/MAGIC)
        :return: constants.ATTACK_CODE_UNSUCCESSFUL if the attack resulted in a miss/glance, else constants.ATTACK_CODE_SUCCESS
        """

        glancing = False
        bonus = self.bonuses.get("bonus", 0)
        enemy_mpm = entity.bonuses.get(utilities.dmg_type_2_str(dmg_type) + "_def", 0)
        enemy_mpm += entity.bonuses.get("mpm", 0)

        mpm_roll = random.randint(0, 150)
        mpm_roll += bonus
        mpm_roll -= enemy_mpm

        if mpm_roll <= 0:
            self.match.update_main_log(f"{self.name} missed {entity.name}", f"{entity.tag_prefix}_missed")
            return constants.ATTACK_CODE_UNSUCCESSFUL

        bpd_type = utilities.dmg_type_2_bpd(dmg_type)
        enemy_bpd = entity.bonuses.get(bpd_type, 0)
        enemy_bpd += entity.bonuses.get("bpd", 0)

        bpd_roll = random.randint(0, 150)
        bpd_roll += bonus
        bpd_roll -= enemy_bpd

        if bpd_roll <= 0:
            glancing = True

        damage = random.randint(self.damage[0], self.damage[1])
        if multiply_first:
            damage *= damage_multiplier
            damage += damage_additive
        else:
            damage += damage_additive
            damage *= damage_multiplier

        crit_chance = (self.bonuses.get("crit", 0) / 200)
        crit = False
        if utilities.chance(crit_chance):
            if not glancing:
                damage *= self.bonuses["crit_multiplier"]
            crit = True

        damage = max(damage * (1 + self.bonuses.get("boost", 0) / 100), 0)

        if glancing:
            if crit:
                entity.attacked(damage, self.element, self, glancing=True, crit=True)
            else:
                entity.attacked(damage * 0.1, self.element, self, glancing=True)
        else:
            if crit:
                entity.attacked(damage, self.element, self, crit=True)
            else:
                entity.attacked(damage, self.element, self)
            return constants.ATTACK_CODE_SUCCESS
        return constants.ATTACK_CODE_UNSUCCESSFUL

    def attack_with_bonus(self, bonuses, entity, damage_multiplier=1.0, damage_additive=0.0, multiply_first=False,
                          dmg_type=constants.DMG_TYPE_MAGIC):
        """
        Attacks an entity with bonuses.

        :param bonuses: The bonuses to the attack
        :param entity: The entity to attack
        :param damage_multiplier: Multiplies the base damage
        :param damage_additive: Added to the base damage
        :param multiply_first: If True, the base damage will first be multiplied by damage_multiplier, then added to the damage_additive. else, first added then multiplied
        :param dmg_type: The damage type to attack the entity with. can be one of the three: constants.DMG_TYPE_(MELEE/PIERCE/MAGIC)
        :return: constants.ATTACK_CODE_UNSUCCESSFUL if the attack resulted in a miss/glance, else constants.ATTACK_CODE_SUCCESS
        """

        for bonus in bonuses.keys():
            utilities.add_value(self.bonuses, bonus, bonuses[bonus])
        self.attack(entity, damage_multiplier=damage_multiplier, damage_additive=damage_additive,
                    multiply_first=multiply_first, dmg_type=dmg_type)
        for bonus in bonuses.keys():
            utilities.add_value(self.bonuses, bonus, -bonuses[bonus])
            if self.bonuses[bonus] == 0:
                self.bonuses.pop(bonus)

    def use_skill(self, event):
        """
        Uses a skill based on a button click event

        :param event: The button click event
        :return:
        """

        if event.widget["state"] == "disabled":
            return
        self.rollback_cooldown.append(self.active_cooldowns.copy())
        self.rollback_waking_up.append(self.waking_up)
        if event.widget.skill != " ":
            self.match.update_rotation_log(self.skill_names[event.widget.skill], add_to_last_attack=True)
        if event.widget.skill != "M":
            self.active_cooldowns[event.widget.skill] = self.cooldowns[event.widget.skill] + 1
            self.skills[event.widget.skill]()
        self.match.next()

    def rollback(self):
        """
        Rollbacks the entity one turn back.
        """

        self.active_cooldowns = self.rollback_cooldown[-1]
        self.rollback_cooldown.pop()
        self.waking_up = self.rollback_waking_up[-1]
        self.rollback_waking_up.pop()


class Entity:
    def __init__(self, name, stats, level=constants.MAX_LEVEL, race="???"):
        self.match = None
        self.element = None
        self.dmg_type = None
        self.name = name
        self.race = race
        self.level = level
        self.stats = stats
        self.bonuses = {}
        self.max_hp = 100 + (level - 1) * 20 + stats.END * 5
        self.max_mp = 100 + (level - 1) * 5 + stats.WIS * 5
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.tag_prefix = ""  # Used for coloring the main log, 'e' if the entity is an enemy, else 'p'

        # Bonuses
        self.bonuses["mpm"] = self.stats.LUK // 20
        self.bonuses["crit"] = self.stats.LUK // 10
        self.bonuses["crit_multiplier"] = 1.75
        self.bonuses["bonus"] = self.stats.WIS // 10
        self.bonuses["boost"] = 0

        self.resists = {"health": -self.stats.WIS // 20}
        self.damage = (0, 0)
        self.armor = "???"
        self.effects = []
        self.effects_fade_turn = {}
        self.death_proof = False
        self.resist_cap = math.inf
        self.dmg_type = utilities.determine_damage_type_by_stats(self)
        self.stunned = False
        self.dot_multiplier = min(1 + self.stats.DEX / 400, 2)  # DEX DoT multiplier caps at +100%
        self.on_hit_special = constants.DEFAULT_ON_HIT_SPECIAL

        # Can be used by the entity to store the effects that it can apply/inflict
        self.available_effects = types.SimpleNamespace()

        # Rollback data
        self.rollback_bonuses = [self.bonuses.copy()]
        self.rollback_resists = [self.resists.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]
        self.rollback_death_proof = [self.death_proof]
        self.rollback_effects = [self.effects.copy()]
        self.rollback_stun = [False]
        self.rollback_effect_fade_turn = [self.effects_fade_turn.copy()]

    def recalculate_bonuses(self, old_stats):
        """
        Recalculates the bonuses from stats
        :param old_stats: The stats before they changed
        """

        self.max_hp = 100 + (self.level - 1) * 20 + self.stats.END * 5
        self.max_mp = 100 + (self.level - 1) * 5 + self.stats.WIS * 5
        self.hp = min(self.max_hp, self.hp)
        self.mp = min(self.max_mp, self.mp)
        self.bonuses["mpm"] += -(old_stats.LUK // 20) + (self.stats.LUK // 20)
        self.bonuses["crit"] += -(old_stats.LUK // 10) + (self.stats.LUK // 10)
        self.bonuses["bonus"] += -(old_stats.WIS // 10) + (self.stats.WIS // 10)
        self.resists["health"] -= -(old_stats.WIS // 20) + (self.stats.WIS // 20)
        self.dot_multiplier = (1 + self.stats.DEX / 400)

    def __repr__(self):
        result = f"""
Level: {self.level}
Stats: {self.stats.__repr__()}
HP: {self.hp}/{self.max_hp} (~{round((self.hp/self.max_hp)*100)}%)
MP: {self.mp}/{self.max_mp} (~{round((self.mp/self.max_mp)*100)}%)
Bonuses:"""
        for key in self.bonuses.keys():
            result += f"\n        {key}: {self.bonuses[key]}"
        result += """
Resistances:"""
        for key in self.resists.keys():
            result += f"\n        {key}: {self.resists[key]}"
        result += """
Effects:"""
        # The order the effects show in DF is the reversed order of self.effects
        for effect in reversed(self.effects):
            result += f"\n        {effect.name}: "
            if len(effect.bonuses.keys()) > 0:
                for bonus in effect.bonuses.keys():
                    result += f"{utilities.num_to_str_with_plus_minus_sign(effect.bonuses[bonus])} {bonus}, "
            if len(effect.resists.keys()) > 0:
                for elem in effect.resists.keys():
                    result += f"{utilities.num_to_str_with_plus_minus_sign(effect.resists[elem])} {elem}, "
            if effect.dot is not None:
                result += f"{effect.dot.dmg_min}-{effect.dot.dmg_max} damage per turn, "
            if effect.stun:
                result += "stunned, "
            effect_duration = utilities.get_effect_duration(effect, self.effects_fade_turn, self.match.current_turn)
            result += f"{effect_duration} turn(s) left."
        return result

    def attack(self, entity, damage_multiplier=1.0, damage_additive=0.0, multiply_first=False, element=None, can_miss=True, return_damage=False):
        """
        Attacks an entity.
        :param can_miss: Whether the attack can miss.
        :param element: The element used in the attack, will use self.element if not specified.
        :param entity: The entity to attack.
        :param damage_multiplier: Multiplies the base damage.
        :param damage_additive: Added to the base damage.
        :param multiply_first: If True, the base damage will first be multiplied by damage_multiplier, then added to the damage_additive. else, first added then multiplied.
        :param return_damage: If True, will return a tuple of the attack return value and the damage dealt.
        :return: constants.ATTACK_CODE_UNSUCCESSFUL if the attack resulted in a miss/glance, else constants.ATTACK_CODE_SUCCESS.
        """

        old_element = self.element
        if element is not None:
            self.element = element

        glancing = False
        if can_miss:
            bonus = self.bonuses["bonus"]
            enemy_mpm = entity.bonuses.get(utilities.dmg_type_2_str(self.dmg_type) + "_def", 0)
            enemy_mpm += entity.bonuses.get("mpm", 0)

            mpm_roll = random.randint(0, 150)
            mpm_roll += bonus
            mpm_roll -= enemy_mpm

            if mpm_roll <= 0:
                self.match.update_main_log(f"{self.name} missed {entity.name}", f"{entity.tag_prefix}_missed")
                return constants.ATTACK_CODE_UNSUCCESSFUL

            bpd_type = utilities.dmg_type_2_bpd(self.dmg_type)
            enemy_bpd = entity.bonuses.get(bpd_type, 0)
            enemy_bpd += entity.bonuses.get("bpd", 0)

            bpd_roll = random.randint(0, 150)
            bpd_roll += bonus
            bpd_roll -= enemy_bpd

            if bpd_roll <= 0:
                glancing = True

        damage = random.randint(self.damage[0], self.damage[1])
        damage += self.stats.get_by_dmg_type(self.dmg_type) // 10
        if multiply_first:
            damage *= damage_multiplier
            damage += damage_additive
        else:
            damage += damage_additive
            damage *= damage_multiplier

        damage = self.on_hit_special(self.match, entity, damage)

        crit_chance = (self.bonuses["crit"] / 200)
        crit = False
        if utilities.chance(crit_chance):
            if not glancing:
                damage *= self.bonuses["crit_multiplier"] + self.stats.INT / 1000
            crit = True

        damage = max(damage * (1 + self.bonuses.get("boost", 0) / 100), 0)
        damage *= (1 + self.stats.DEX / 4000)

        if glancing:
            if crit:
                damage_dealt = entity.attacked(damage * (1 + self.stats.STR / 1000), self.element, self, glancing=True, crit=True)
            else:
                damage_dealt = entity.attacked(damage * 0.1, self.element, self, glancing=True)
        else:
            if crit:
                damage_dealt = entity.attacked(damage, self.element, self, crit=True)
            else:
                damage_dealt = entity.attacked(damage * (1 + self.stats.STR / 1000), self.element, self)
            self.on_hit_special(self.match, entity, damage)
            self.element = old_element
            if return_damage:
                return constants.ATTACK_CODE_SUCCESS, damage_dealt
            return constants.ATTACK_CODE_SUCCESS
        self.element = old_element
        if return_damage:
            return constants.ATTACK_CODE_UNSUCCESSFUL, damage_dealt
        return constants.ATTACK_CODE_UNSUCCESSFUL

    def attack_with_bonus(self, bonuses, entity, damage_multiplier=1.0, damage_additive=0.0, multiply_first=False, element=None, can_miss=True, return_damage=False):
        """
        Attacks an entity with bonuses.

        :param bonuses: The bonuses to the attack
        :param can_miss: Whether the attack can miss.
        :param element: The element used in the attack, will use self.element if not specified.
        :param entity: The entity to attack.
        :param damage_multiplier: Multiplies the base damage.
        :param damage_additive: Added to the base damage.
        :param multiply_first: If True, the base damage will first be multiplied by damage_multiplier, then added to the damage_additive. else, first added then multiplied.
        :param return_damage: If True, will return a tuple of the attack return value and the damage dealt.
        :return: constants.ATTACK_CODE_UNSUCCESSFUL if the attack resulted in a miss/glance, else constants.ATTACK_CODE_SUCCESS.
        """

        for bonus in bonuses.keys():
            utilities.add_value(self.bonuses, bonus, bonuses[bonus])
        self.attack(entity, damage_multiplier=damage_multiplier, damage_additive=damage_additive,
                    multiply_first=multiply_first, element=element, can_miss=can_miss, return_damage=return_damage)
        for bonus in bonuses.keys():
            utilities.add_value(self.bonuses, bonus, -bonuses[bonus])
            if self.bonuses[bonus] == 0:
                self.bonuses.pop(bonus)

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False):
        """
        Receive damage from an attack

        :param damage: The received attack's damage
        :param element: The received attack's element
        :param entity: The entity that made the attack (used for logging)
        :param dot: Whether the received attack is from a DoT effect
        :param glancing: Whether the received attack was a glancing hit/crit
        :param crit: Whether the received attack was a crit
        :return: Damage taken
        """

        if element == "mana":
            if glancing:
                return 0
            damage = round(damage)
            self.mp = max(min(self.mp - damage, self.max_mp), 0)
            if damage < 0:
                if dot:
                    self.match.update_main_log(f"{self.name} recovers {-damage} MP from {entity.name}.", f"{self.tag_prefix}_mana_heal_dot")
                else:
                    self.match.update_main_log(f"{self.name} recovers {-damage} MP.", f"{self.tag_prefix}_mana_heal")
            else:
                if dot:
                    self.match.update_main_log(f"{self.name} takes {damage} {element} damage to MP from {entity.name}.", f"{self.tag_prefix}_mana_dot")
                else:
                    self.match.update_main_log(f"{entity.name} hits {self.name} for {damage} {element} damage to MP.", f"{self.tag_prefix}_mana_attacked")
            return damage
        cap = self.resist_cap
        if element == "immobility":
            cap = math.inf
        all_resist = self.resists.get("all", 0) if element != "null" else 0  # Null attacks ignore all resist
        resist = min(all_resist + self.resists.get(element, 0), cap)
        damage *= (100 - resist) / 100
        if element == "health":
            damage = round(damage)
            self.hp = max(min(self.hp + damage, self.max_hp), 0)
            if dot:
                self.match.update_main_log(f"{self.name} heals {self.name} for {damage} HP.", f"{self.tag_prefix}_hot")
            else:
                self.match.update_main_log(f"{self.name} recovers {damage} HP.", f"{self.tag_prefix}_heal")
        else:
            for effect in self.effects:
                if effect.retaliation is not None and entity is not self.match.pet:
                    dmg = effect.retaliation.get_damage()
                    entity.hp = utilities.clamp(entity.hp - dmg, 0, entity.max_hp)
                    self.match.update_main_log(f"{entity.name} takes {dmg} damage from {effect.name}", f"{entity.tag_prefix}_attacked")

            damage = round(damage)
            if self.death_proof and not dot:
                if damage >= self.hp:
                    if self.hp == 1:
                        damage = 0
                    else:
                        damage = self.hp // 2
            self.hp -= damage
            if dot:
                self.match.update_main_log(f"{self.name} takes {damage} {element} damage from {entity.name}.", f"{self.tag_prefix}_dot")
            else:
                if glancing:
                    if crit:
                        self.match.update_main_log(f"{entity.name} critically glances {self.name} for {damage} {element} damage.", f"{self.tag_prefix}_attacked_crit_glance")
                    else:
                        self.match.update_main_log(f"{entity.name} glances {self.name} for {damage} {element} damage.", f"{self.tag_prefix}_attacked_glance")
                else:
                    if crit:
                        self.match.update_main_log(f"{entity.name} critically hits {self.name} for {damage} {element} damage.", f"{self.tag_prefix}_attacked_crit")
                    else:
                        self.match.update_main_log(f"{entity.name} hits {self.name} for {damage} {element} damage.", f"{self.tag_prefix}_attacked")
        return damage

    def remove_effect(self, effect):
        """
        Removes an effect.

        :param effect: The effect to remove
        """

        removed = False
        for eff in self.effects:
            if eff == effect:
                self.effects.remove(eff)
                removed = True
                break

        if not removed:  # effect wasn't applied
            return

        for bonus in effect.bonuses.keys():
            utilities.add_value(self.bonuses, bonus, -effect.bonuses[bonus])
        for elem in effect.resists.keys():
            utilities.add_value(self.resists, elem, -effect.resists[elem])
        if effect.death_proof:
            death_proof = False
            for effect in self.effects:
                if effect.death_proof:
                    death_proof = True
                    break
            self.death_proof = death_proof
        latest_effect_fade_turn = -1
        latest_effect_instance = None
        for turn in self.effects_fade_turn.keys():
            for eff in self.effects_fade_turn[turn]:
                if eff == effect:
                    if turn > latest_effect_fade_turn:
                        latest_effect_fade_turn = turn
                        latest_effect_instance = eff
        self.effects_fade_turn[latest_effect_fade_turn].remove(latest_effect_instance)
        if effect.stun is True:
            for eff in self.effects:
                if eff.stun is True:
                    return
            self.stunned = False

    def add_effect(self, effect):
        """
        Adds an effect.

        :param effect: The effect to add.
        """

        if effect.stun is True:
            if utilities.stun_chance(self):
                self.stunned = True
            else:
                return

        already_applied = False
        for eff in self.effects:
            if effect == eff:
                already_applied = True
                self.remove_effect(effect)
                break

        fade_turn = self.match.current_turn + effect.duration
        if already_applied and effect.refreshable:
            fade_turn += 1

        self.effects.append(effect)
        utilities.add_value(self.effects_fade_turn, fade_turn, effect, dict_of_lists=True)
        for bonus in effect.bonuses.keys():
            utilities.add_value(self.bonuses, bonus, effect.bonuses[bonus])
        for elem in effect.resists.keys():
            utilities.add_value(self.resists, elem, effect.resists[elem])
        if effect.death_proof:
            self.death_proof = True

    def replace_effect(self, old_effect, new_effect):
        """
        Replaces an effect with a new one.

        :param old_effect: The effect to replace
        :param new_effect: The effect to replace the old effect with
        """

        effects_list = self.effects.copy()
        self.remove_effect(old_effect)
        self.add_effect(new_effect)
        effects_list[effects_list.index(old_effect)] = new_effect
        self.effects = effects_list

    def take_dot_damage(self, effect):
        """
        Takes DoT damage from an effect.

        :param effect: The effect to take DoT damage from.
        """

        self.attacked(random.randint(math.floor(effect.dot.dmg_min), math.floor(effect.dot.dmg_max)),
                      effect.dot.element, effect, dot=True)

    def next(self):
        """
        Prepares the entity before its turn.
        """
        if self.hp <= 0:
            return

        for effect in self.effects:
            if effect.dot is not None:
                self.take_dot_damage(effect)

    def update_rollback_data(self):
        """
        Updates rollback data.
        """

        self.rollback_effects.append(self.effects.copy())
        self.rollback_bonuses.append(self.bonuses.copy())
        self.rollback_resists.append(self.resists.copy())
        self.rollback_death_proof.append(self.death_proof)
        self.rollback_hp.append(self.hp)
        self.rollback_mp.append(self.mp)
        self.rollback_stun.append(self.stunned)
        self.rollback_effect_fade_turn.append(utilities.copy_dict(self.effects_fade_turn))

    def rollback(self):
        """
        Rollbacks the entity one turn back.
        """

        to_remove = []
        for effect in self.effects:
            if effect in self.rollback_effects[-2]:
                continue
            to_remove.append(effect)
        for effect in to_remove:
            self.remove_effect(effect)
        for effect in self.rollback_effects[-2]:
            if effect in self.effects:
                continue
            self.add_effect(effect)
        self.rollback_effects.pop()

        self.effects_fade_turn = utilities.copy_dict(self.rollback_effect_fade_turn[-2])
        self.rollback_effect_fade_turn.pop()

        self.bonuses = self.rollback_bonuses[-2].copy()
        self.rollback_bonuses.pop()
        self.resists = self.rollback_resists[-2].copy()
        self.rollback_resists.pop()
        self.hp = self.rollback_hp[-2]
        self.rollback_hp.pop()
        self.mp = self.rollback_mp[-2]
        self.rollback_mp.pop()
        self.death_proof = self.rollback_death_proof[-2]
        self.rollback_death_proof.pop()
        self.stunned = self.rollback_stun[-2]
        self.rollback_stun.pop()


class Player(Entity):
    def __init__(self, name, stats, level=constants.MAX_LEVEL, hp_potion_level=constants.HP_POTION_MAX_LEVEL,
                 mp_potion_level=constants.MP_POTION_MAX_LEVEL, gear=None):
        super().__init__(name, stats, level=level, race="human")

        if gear is None:
            gear = {}

        self.tag_prefix = "p"  # Used for coloring the main log, 'p' stands for player

        # Gear
        self.gear = {}
        self.gear_resists = {}
        self.gear_bonuses = {}
        self.gear_resists_uncapped = {}
        self.gear_bonuses_uncapped = {}
        self.default_weapon = None

        # Potions
        self.hp_potion_value = 100 + self.level * (hp_potion_level - 5) * constants.HP_POTION_SCALING_VALUE
        self.mp_potion_value = 100 + self.level * (mp_potion_level - 5) * constants.MP_POTION_SCALING_VALUE
        self.hp_potion_count = 5
        self.mp_potion_count = 5

        # Resists
        self.resist_cap = 99
        self.resists["immobility"] = self.stats.END // 5

        # Skills
        self.mana_cost = {}
        self.active_cooldowns = {}
        self.cooldowns = {}
        self.skills = {}
        self.skill_images = {}
        self.skill_names = {}

        # Some armors use an extra button (e.g. ChW for soulthreads)
        self.extra_window = None

        # Rollback data
        self.rollback_gear = [self.gear.copy()]
        self.rollback_cooldown = [self.active_cooldowns.copy()]
        self.rollback_hp_potion_count = [self.hp_potion_count]
        self.rollback_mp_potion_count = [self.mp_potion_count]
        self.rollback_resists = [self.resists.copy()]

        for slot in gear.keys():
            self.equip(slot, gear[slot], update_details=False)

        # If the default gear increased END/WIS, the current hp/mp would be smaller than the max hp/mp
        self.hp = self.max_hp
        self.mp = self.max_mp

    def recalculate_bonuses(self, old_stats):
        """
        Recalculates the bonuses from stats
        :param old_stats: The stats before they changed
        """

        super().recalculate_bonuses(old_stats)
        self.resists["immobility"] += -(old_stats.END // 5) + (self.stats.END // 5)

    def equip(self, slot, item, update_details=True):
        """
        Equips an item.

        :param slot: The item's slot
        :param item: The item
        :param update_details: Whether to update the detail windows or not.
        """

        if slot == constants.SLOT_PET and self.match.pet == item:
            return
        if slot == constants.SLOT_WEAPON_SPECIAL and self.on_hit_special == item.on_hit_special:
            return
        if self.gear.get(slot, None) == item:
            return
        self.unequip(slot, ignore_default_item=True, update_details=False)
        if slot == constants.SLOT_PET:
            self.match.pet = item
            self.match.pet.waking_up = True
            return
        self.gear[slot] = item

        if slot == constants.SLOT_WEAPON_SPECIAL:
            self.on_hit_special = item.on_hit_special
            return

        if slot == constants.SLOT_WEAPON:
            if item.dmg_type != 0:
                self.dmg_type = item.dmg_type
            else:
                self.dmg_type = utilities.determine_damage_type_by_stats(self)

            self.element = item.element
            self.damage = (item.damage[0], item.damage[1])

        for elem in item.resists.keys():
            cap = constants.PER_ELEM_RESIST_CAP
            if elem == "health":
                cap = math.inf
            old_gear_resist = self.gear_resists.get(elem, 0)
            utilities.add_value(self.gear_resists, elem, item.resists[elem], cap=cap)
            utilities.add_value(self.gear_resists_uncapped, elem, item.resists[elem])
            self.resists[elem] = self.resists.get(elem, 0) - old_gear_resist + self.gear_resists[elem]

        old_stats = self.stats.copy()
        stats_changed = False
        for bonus in item.bonuses.keys():
            if bonus.lower() != bonus:
                # the only bonuses written in uppercase are main stats
                stats_changed = True
                self.stats.add_by_str(bonus, item.bonuses[bonus])
                continue

            old_gear_bonus = self.gear_bonuses.get(bonus, 0)
            if bonus == "crit":  # crit has a cap of 100 from gear
                utilities.add_value(self.gear_bonuses, bonus, item.bonuses[bonus], cap=constants.CRIT_CAP)
            else:
                utilities.add_value(self.gear_bonuses, bonus, item.bonuses[bonus])
            utilities.add_value(self.gear_bonuses_uncapped, bonus, item.bonuses[bonus])

            self.bonuses[bonus] = self.bonuses.get(bonus, 0) - old_gear_bonus + self.gear_bonuses[bonus]

        if stats_changed:
            self.recalculate_bonuses(old_stats)
            if self.match is not None and self.match.pet.armor == "Kid Dragon":
                self.match.pet.update_cooldowns_by_cha()

        if update_details:
            self.match.update_detail_windows()

    def unequip(self, slot, ignore_default_item=False, update_details=True):
        """
        Unequips an item.

        :param slot: The item's slot
        :param ignore_default_item: Whether to equip the default weapon upon unequipping a weapon or not.
        :param update_details: Whether to update the detail window or not.
        """

        if slot == constants.SLOT_PET:
            self.match.pet = None
            return
        item = self.gear.pop(slot, None)
        if item is None:  # item isn't equipped
            return

        if slot == constants.SLOT_WEAPON_SPECIAL:
            self.on_hit_special = constants.DEFAULT_ON_HIT_SPECIAL

        for elem in item.resists.keys():
            old_gear_resist = self.gear_resists[elem]
            self.gear_resists_uncapped[elem] -= item.resists[elem]
            self.gear_resists[elem] = min(self.gear_resists_uncapped[elem], constants.PER_ELEM_RESIST_CAP)
            self.resists[elem] = self.resists.get(elem, 0) - old_gear_resist + self.gear_resists[elem]

        stats_changed = False
        old_stats = self.stats.copy()
        for bonus in item.bonuses.keys():
            if bonus.lower() != bonus:
                # the only bonuses written in uppercase are main stats
                stats_changed = True
                self.stats.add_by_str(bonus, -item.bonuses[bonus])
                continue

            old_gear_bonus = self.gear_bonuses[bonus]
            self.gear_bonuses_uncapped[bonus] -= item.bonuses[bonus]
            self.gear_bonuses[bonus] = min(self.gear_bonuses_uncapped[bonus],
                                           (constants.CRIT_CAP if bonus == "crit" else math.inf))
            self.bonuses[bonus] = self.bonuses.get(bonus, 0) - old_gear_bonus + self.gear_bonuses[bonus]

        if stats_changed:
            self.recalculate_bonuses(old_stats)

        if slot == constants.SLOT_WEAPON and not ignore_default_item:
            self.equip(constants.SLOT_WEAPON, self.default_weapon, update_details=False)

        if update_details:
            self.match.update_detail_windows()

    def hp_potion(self):
        """
        Use an HP potion.
        """

        self.attacked(self.hp_potion_value, "health")

    def mp_potion(self):
        """
        Use an MP potion.
        """

        self.attacked(-self.mp_potion_value, "mana")

    def next(self):
        """
        Prepares the player before its turn.

        :return: constants.PLAYER_STUNNED_STR if the player is stunned, else None
        """
        super().next()

        if self.stunned and utilities.chance(constants.PLAYER_STUN_CHANCE):
            self.match.update_main_log(f"{self.name} is not affected by stun.", f"{self.tag_prefix}_comment")
            return constants.PLAYER_STUNNED_STR

    def update_rollback_data(self):
        """
        Updates rollback data.
        """

        super().update_rollback_data()
        self.rollback_gear.append(self.gear.copy())
        self.rollback_cooldown.append(self.active_cooldowns.copy())
        self.rollback_hp_potion_count.append(self.hp_potion_count)
        self.rollback_mp_potion_count.append(self.mp_potion_count)

    def use_skill_button_onclick(self, event, attack_name=None):
        """
        Uses a skill based on a button onclick event

        :param event: The button onclick event.
        :param attack_name: The attack's name (will use the button's skill if not specified)
        :return:
        """

        if event.widget["state"] == "disabled":
            return
        if attack_name is None:
            attack_name = self.skill_names[event.widget.skill]
        self.spend_mp_on_skill(event.widget.skill)
        if event.widget.skill not in ("N", "M"):
            self.active_cooldowns[event.widget.skill] = self.cooldowns[event.widget.skill] + 1
        if self.skills[event.widget.skill]() != constants.SKILL_RETURN_CODE_DOUBLE_TURN:
            self.match.update_rotation_log(attack_name)
            self.match.pet_turn()
        else:
            self.match.update_rotation_log(attack_name, double_turn=True)
            self.match.update_match_after_double_turn()
        return event.widget.skill

    def check_mp_for_skill(self, skill):
        """
        Checks if the player has enough MP for a skill (or enough potions for an HP/MP potion).

        :param skill: The skill to check MP/potion count for
        """

        if skill == "N":
            return self.hp_potion_count > 0
        if skill == "M":
            return self.mp_potion_count > 0
        assert skill in self.mana_cost.keys()
        return self.mana_cost[skill] <= self.mp

    def spend_mp_on_skill(self, skill):
        """
        Spend MP on a skill (or reduce the potion count for an HP/MP potion)

        :param skill: The skill to spend MP/reduce potion count on
        """

        if skill == "N":
            self.hp_potion_count -= 1
        elif skill == "M":
            self.mp_potion_count -= 1
        else:
            self.mp = max(self.mp - self.mana_cost[skill], 0)

    def update_skill_images(self):
        """
        Updates the skill_images dict.
        """
        for skill in self.skills.keys():
            file_name = "images/"
            if skill == " ":
                file_name += "attack"
            elif skill == "N":
                file_name += "hp"
            elif skill == "M":
                file_name += "mp"
            else:
                file_name += f"{self.armor.lower()}/{skill}"
            self.skill_images[skill] = tkinter.PhotoImage(file=f"{file_name}.png")

    def rollback(self):
        """
        Rollbacks the player one turn back.
        """

        super().rollback()

        old_stats = self.stats.copy()
        to_unequip = []
        for slot in self.gear.keys():
            if self.gear[slot] == self.rollback_gear[-2].get(slot, None):
                continue
            to_unequip.append(slot)
        for slot in to_unequip:
            self.unequip(slot)
        to_equip = []
        for slot in self.rollback_gear[-2].keys():
            if self.rollback_gear[-2][slot] == self.gear.get(slot, None):
                continue
            to_equip.append((slot, self.rollback_gear[-2][slot]))
        for gear in to_equip:
            self.equip(gear[0], gear[1])

        self.rollback_gear.pop()
        self.recalculate_bonuses(old_stats)
        self.active_cooldowns = self.rollback_cooldown[-2].copy()
        self.rollback_cooldown.pop()
        self.hp_potion_count = self.rollback_hp_potion_count[-2]
        self.rollback_hp_potion_count.pop()
        self.mp_potion_count = self.rollback_mp_potion_count[-2]
        self.rollback_mp_potion_count.pop()


class Enemy(Entity):
    def __init__(self, name, stats, level=constants.MAX_LEVEL, race="???"):
        super().__init__(name, stats, level=level, race="???")

        self.tag_prefix = "e"  # Used for coloring the main log, 'e' stands for enemy

    def player_double_turn_reaction(self):
        pass

    def next(self):
        """
        Prepares the entity before its turn.

        :return: constants.ENEMY_STUNNED_STR if the player is stunned, else None
        """
        super().next()

        if self.stunned:
            return constants.ENEMY_STUNNED_STR

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False):
        if element == "health":
            cap = self.resist_cap
            resist = min(self.resists.get("all", 0) + self.resists.get(element, 0), cap)
            damage *= (100 - resist) / 100
            if resist > 100 and not dot:  # Enemies with 100+ health resist heal for 1 HP from sources that aren't HoTs.
                damage = 1
            damage = round(damage)
            self.hp = max(min(self.hp + damage, self.max_hp), 0)
            if dot:
                self.match.update_main_log(f"{self.name} heals {self.name} for {damage} HP.", f"{self.tag_prefix}_hot")
            else:
                self.match.update_main_log(f"{self.name} recovers {damage} HP.", f"{self.tag_prefix}_heal")
            return damage
        else:
            return super().attacked(damage, element, entity, dot, glancing, crit)
