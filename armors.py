import math
import random
import tkinter

import classes
import constants
import utilities
import effects
from gear import weapons


class Chaosweaver(classes.Player):
    def __init__(self, name, stats, level=constants.MAX_LEVEL, hp_potion_level=constants.HP_POTION_MAX_LEVEL,
                 mp_potion_level=constants.MP_POTION_MAX_LEVEL, gear=None):
        super().__init__(name, stats, level=level, hp_potion_level=hp_potion_level, mp_potion_level=mp_potion_level, gear=gear)

        self.armor = "Chaosweaver"
        self.default_weapon = weapons.weaver_blade
        if constants.SLOT_WEAPON not in gear.keys():
            self.equip(constants.SLOT_WEAPON, self.default_weapon, update_details=False)
        self.empowered = True
        self.soulthreads = 2
        self.skill_names = {"V": "Untangle", "C": "Snap", "0": "Rebuke", "9": "Venge", "8": "Rip",
                            "7": "Dominance", "6": "Siphon", " ": "Attack", "5": "Aegis", "4": "Gambit", "3": "Slice",
                            "2": "Hexing", "1": "Aggro", "X": "Shred", "Z": "Assault", "M": "MP", "N": "HP"}
        self.skills = {"V": self.skill_untangle, "C": self.skill_obliterate, "0": self.skill_rebuke,
                       "9": self.skill_vengeance, "8": self.skill_soul_rip, "7": self.skill_dominance,
                       "6": self.skill_soul_siphon, " ": self.skill_attack, "5": self.skill_soul_aegis,
                       "4": self.skill_soul_gambit, "3": self.skill_soul_slice, "2": self.skill_hexing_wheel,
                       "1": self.skill_aggression, "X": self.skill_soul_shred, "Z": self.skill_soul_assault,
                       "N": self.hp_potion, "M": self.mp_potion}
        self.empowered_skills = {"9", "6", "5", "4", "1", "X"}
        self.mana_cost = {"V": 35, "C": 35, "0": 20, "9": 45, "8": 25, "7": 30, "6": 35, " ": 0,
                          "5": 15, "4": 30, "3": 5, "2": 20, "1": 45, "X": 27, "Z": 20}
        self.cooldowns = {"V": 16, "C": 7, "0": 9, "9": 9, "8": 19, "7": 3, "6": 9, " ": 0,
                          "5": 8, "4": 4, "3": 4, "2": 4, "1": 4, "X": 14, "Z": 10}
        self.update_skill_images()
        self.bonuses["mpm"] = 5
        self.bonuses["crit"] += 5
        self.bonuses["bpd"] = 5
        self.bonuses["crit_multiplier"] = 1.85

        self.extra_window = tkinter.Tk()
        self.extra_window.title("Soulthreads")
        self.extra_button = tkinter.Button(master=self.extra_window, text=f"Empowered, {self.soulthreads} soulthreads left", bg="red")
        self.extra_button.bind("<Button-1>", self.toggle_empowered_button_onclick)
        self.extra_button.pack()

        self.rollback_soulthreads = [self.soulthreads]
        self.rollback_bonuses = [self.bonuses.copy()]

    def use_skill_button_onclick(self, event, attack_name=None):
        if event.widget["state"] == "disabled":
            return
        attack_name = self.skill_names[event.widget.skill]
        if self.empowered and event.widget.skill in self.empowered_skills:
            attack_name = "e" + attack_name
        super().use_skill_button_onclick(event, attack_name=attack_name)

    def rollback(self):
        super().rollback()
        self.soulthreads = self.rollback_soulthreads[-2]
        self.rollback_soulthreads.pop()
        self.update_extra_button()

    def update_extra_button(self):
        if self.empowered:
            self.extra_button["text"] = f"Empowered, {self.soulthreads} soulthreads left"
            self.extra_button["bg"] = "red"
        else:
            self.extra_button["text"] = f"Unempowered, {self.soulthreads} soulthreads left"
            self.extra_button["bg"] = "white"

    def update_rollback_data(self):
        super().update_rollback_data()
        self.rollback_soulthreads.append(self.soulthreads)

    def toggle_empowered_button_onclick(self, event):
        if self.soulthreads == 0 or self.empowered:
            self.empowered = False
        else:
            self.empowered = True
        self.update_extra_button()

    def add_soulthread(self):
        self.soulthreads = min(self.soulthreads + 1, 2)
        self.update_extra_button()

    def use_soulthread(self):
        self.soulthreads -= 1
        if self.soulthreads == 0:
            self.empowered = False
        self.update_extra_button()

    def skill_attack(self):
        for i in range(2):
            self.attack(self.match.targeted_enemy, damage_multiplier=0.625)

    def skill_soul_aegis(self):
        if self.empowered:
            self.add_effect(effects.empowered_soul_aegis)
            self.use_soulthread()
            return
        self.add_effect(effects.soul_aegis)

    def skill_soul_gambit(self):
        self.add_effect(effects.soul_gambit)
        if self.empowered:
            self.add_effect(effects.empowered_soul_boost)
            self.use_soulthread()
            return constants.SKILL_RETURN_CODE_DOUBLE_TURN
        self.add_effect(effects.soul_boost)

    def skill_soul_slice(self):
        self.add_effect(effects.soul_hunter)
        self.attack(self.match.targeted_enemy)
        self.attack(self.match.targeted_enemy)

    def skill_hexing_wheel(self):
        self.match.update_player_cooldowns()
        for i in range(8):
            self.attack(self.match.targeted_enemy, damage_multiplier=0.25)

    def skill_aggression(self):
        hit = False
        for i in range(8):
            if self.attack(self.match.targeted_enemy, damage_multiplier=0.28125) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            dot_dpt = utilities.dot_dpt(self, 0.5)
            if self.empowered:
                self.match.targeted_enemy.add_effect(effects.empowered_mothbitten(self.element, dot_dpt[0], dot_dpt[1]))
            else:
                self.match.targeted_enemy.add_effect(effects.mothbitten(self.element, dot_dpt[0], dot_dpt[1]))
        if self.empowered:
            self.use_soulthread()

    def skill_soul_shred(self):
        even_hit = False
        odd_hit = False
        for i in range(1, 8):
            if self.attack(self.match.targeted_enemy, damage_multiplier=0.2857) == constants.ATTACK_CODE_SUCCESS:
                if i % 2 == 0:
                    even_hit = True
                else:
                    odd_hit = True
        if self.empowered:
            self.use_soulthread()
            if even_hit:
                self.match.targeted_enemy.add_effect(effects.soul_damage)
            if odd_hit:
                self.match.targeted_enemy.add_effect(effects.shredded_soul)
            return
        if even_hit or odd_hit:
            self.match.targeted_enemy.add_effect(effects.shredded_soul)

    def skill_soul_assault(self):
        self.add_soulthread()
        for i in range(12):
            self.attack(self.match.targeted_enemy, damage_multiplier=0.1875)

    def skill_soul_siphon(self):
        if self.empowered:
            self.use_soulthread()
            for effect in self.effects:
                if effect.dot_dpt_min is not None:
                    self.remove_effect(effect)
        for i in range(2):
            old_enemy_hp = self.match.targeted_enemy.hp
            self.attack(self.match.targeted_enemy, damage_multiplier=0.875)
            damage_dealt = old_enemy_hp - self.match.targeted_enemy.hp
            missing_hp_percent = (1 - (self.hp / self.max_hp)) / 100
            self.attacked((100 + missing_hp_percent)/100 * damage_dealt, "health")

    def skill_dominance(self):
        for entity in self.match.enemies:
            self.attack(entity, damage_multiplier=1.6)

    def skill_soul_rip(self):
        for entity in self.match.enemies:
            if self.attack(entity) == constants.ATTACK_CODE_SUCCESS:
                entity.add_effect(effects.rippen_soul)

    def skill_vengeance(self):
        for i in range(19):
            if self.attack(self.match.targeted_enemy, damage_multiplier=0.092) == constants.ATTACK_CODE_SUCCESS:
                if self.empowered:
                    self.match.targeted_enemy.add_effect(effects.empowered_overwhelmed)
                    self.use_soulthread()
                else:
                    self.match.targeted_enemy.add_effect(effects.overwhelmed)

    def skill_rebuke(self):
        damage_multiplier = 1.667
        if self.hp == self.max_hp:
            damage_multiplier = 0.333
        elif self.hp >= 0.71 * self.max_hp:
            damage_multiplier = 0.667
        elif self.hp >= 0.41 * self.max_hp:
            damage_multiplier = 1
        elif self.hp >= 0.11 * self.max_hp:
            damage_multiplier = 1.333

        for i in range(3):
            self.attack(self.match.targeted_enemy, damage_multiplier=damage_multiplier)

    def skill_obliterate(self):
        if self.attack(self.match.targeted_enemy, damage_multiplier=2) == constants.ATTACK_CODE_UNSUCCESSFUL:
            return
        if (self.match.targeted_enemy.max_hp <= 0.5 * self.max_hp
                and self.match.targeted_enemy.hp <= 0.7 * self.match.targeted_enemy.max_hp) \
                or (0.5 * self.max_hp <= self.match.targeted_enemy.max_hp <= self.max_hp
                    and self.match.targeted_enemy.hp <= 0.5 * self.match.targeted_enemy.max_hp) \
                or (self.max_hp <= self.match.targeted_enemy.max_hp <= 2 * self.max_hp
                    and self.match.targeted_enemy.hp <= 0.2 * self.match.targeted_enemy.max_hp) \
                or (2 * self.max_hp <= self.match.targeted_enemy.max_hp <= 3 * self.max_hp
                    and self.match.targeted_enemy.hp <= 0.15 * self.match.targeted_enemy.max_hp) \
                or (3 * self.max_hp <= self.match.targeted_enemy.max_hp <= 5 * self.max_hp
                    and self.match.targeted_enemy.hp <= 0.1 * self.match.targeted_enemy.max_hp) \
                or (self.match.targeted_enemy.max_hp >= 5 * self.max_hp
                    and self.match.targeted_enemy.hp <= 0.05 * self.match.targeted_enemy.max_hp):
            self.match.targeted_enemy.add_effect(
                effects.soul_annihilation(self.match.targeted_enemy.hp * self.dot_multiplier))
        else:
            dot_dpt = utilities.dot_dpt(self, 3)
            self.match.targeted_enemy.add_effect(effects.soul_torn(dot_dpt[0], dot_dpt[1]))

    def skill_untangle(self):
        self.add_soulthread()
        for i in range(5):
            self.attack_with_bonus({"crit": 200}, self.match.targeted_enemy, 0.6)


class Technomancer(classes.Player):
    def __init__(self, name, stats, level=constants.MAX_LEVEL, hp_potion_level=constants.HP_POTION_MAX_LEVEL,
                 mp_potion_level=constants.MP_POTION_MAX_LEVEL, gear=None):
        super().__init__(name, stats, level=level, hp_potion_level=hp_potion_level, mp_potion_level=mp_potion_level, gear=gear)

        self.armor = "Technomancer"
        self.heat_level = 0
        self.wis_threshold = self.level // 5
        self.old_mp = self.mp  # Will be used to check if the player had enough MP to use a skill before heat level reduced MP.
        self.drive_boost = lambda: math.floor((1 - (self.mp / self.max_mp)) * 100) * 2
        self.drive_boost_enabled = True
        self.turns_until_drive_boost_enabled = 0
        self.start_wis = self.stats.WIS
        self.default_weapon = weapons.laser_screwdriver
        if constants.SLOT_WEAPON not in gear.keys():
            self.equip(constants.SLOT_WEAPON, self.default_weapon, update_details=False)
        self.skills = {"V": self.skill_force_sword, "C": self.skill_photon_bow, "0": self.skill_static_overload_blast,
                       "9": self.skill_mana_burst_grenades, "8": self.skill_enhanced_metallic_aging,
                       "7": self.skill_drillbit, "6": self.skill_event_horizon, " ": self.skill_attack,
                       "5": self.skill_reactive_barrier, "4": self.skill_overclock, "3": self.skill_mana_eruption,
                       "2": self.skill_magnetic_resonance_protocol, "1": self.skill_sonic_boom_blaster,
                       "X": self.skill_tog_drone_tracking, "Z": self.skill_vent_heat, "M": self.mp_potion,
                       "N": self.hp_potion}
        self.skill_names = {"V": "Force", "C": "Bow", "0": "Static", "9": "Grenade", "8": "Aging", "7": "Drill",
                            "6": "Horizon", " ": "Attack", "5": "Barrier", "4": "Over", "3": "Mana", "2": "Repair",
                            "1": "Sonic", "X": "Tog", "Z": "Vent", "M": "MP", "N": "HP"}
        self.mana_cost = {"V": 35, "C": 35, "0": 40, "9": 35, "8": 30, "7": 35, "6": 45, " ": 0,
                          "5": 25, "4": 30, "3": 0, "2": 40, "1": 35, "X": 35, "Z": 0}
        self.cooldowns = {"V": 8, "C": 1, "0": 2, "9": 4, "8": 7, "7": 9, "6": 6, " ": 0,
                          "5": 5, "4": 13, "3": 18, "2": 9, "1": 14, "X": 11, "Z": 0}
        self.bonuses["mpm"] = 5
        self.bonuses["crit"] += 5

        self.rollback_heat_level = [self.heat_level]
        self.rollback_old_mp = [self.old_mp]

        self.update_skill_images()

    def rollback(self):
        super().rollback()
        self.heat_level = self.rollback_heat_level[-2]
        self.rollback_heat_level.pop()
        self.old_mp = self.rollback_old_mp[-2]
        self.rollback_old_mp.pop()

    def equip(self, slot, item, update_details=True):
        super().equip(slot, item, update_details=update_details)

        self.old_mp = self.mp
        # The match class only sets self.match after the initialization, so when equipping the default weapon, match might be None
        if self.match is not None:
            self.match.update_player_skill_buttons()

    def unequip(self, slot, ignore_default_item=False, update_details=True):
        super().unequip(slot, ignore_default_item=ignore_default_item, update_details=update_details)

        self.old_mp = self.mp
        # The match class only sets self.match after the initialization, so when equipping the default weapon, match might be None
        if self.match is not None:
            self.match.update_player_skill_buttons()

    def use_skill_button_onclick(self, event, attack_name=None):
        super().use_skill_button_onclick(event, attack_name)

        if abs(self.stats.WIS - self.start_wis) > self.wis_threshold:
            self.drive_boost_enabled = False
            self.turns_until_drive_boost_enabled = 3
            self.start_wis = self.stats.WIS
            self.match.update_main_log(f"WIS deviation of greater than {self.wis_threshold} detected. Drive Core Mismatch Error: Drive Boost recalibrating.")

    def next(self):
        return_value = super().next()
        if return_value == constants.PLAYER_STUNNED_STR:
            return return_value

        self.heat_level = min(self.heat_level + 1, 20)
        self.old_mp = self.mp
        self.attacked(self.heat_level, "mana", entity=self)
        self.match.update_player_skill_buttons()
        self.match.update_detail_windows()

        if self.drive_boost_enabled is False:
            if self.turns_until_drive_boost_enabled == 0:
                self.drive_boost_enabled = True
            else:
                self.turns_until_drive_boost_enabled -= 1

        if self.drive_boost_enabled:
            self.match.update_main_log(f"Heat Level: {self.heat_level} Drive Boost: {self.drive_boost()}", "p_comment")
        else:
            self.match.update_main_log(f"Heat Level: {self.heat_level} Drive Boost: Recalibrating for {self.turns_until_drive_boost_enabled + 1} turn(s)")

        self.rollback_heat_level.append(self.heat_level)
        self.rollback_old_mp.append(self.old_mp)
        # Replace the old mana rollback with the one updated with the heat level
        self.rollback_mp[-1] = self.mp

        return return_value

    def check_mp_for_skill(self, skill):
        if skill == "N":
            return self.hp_potion_count > 0
        if skill == "M":
            return self.mp_potion_count > 0
        assert skill in self.mana_cost.keys()
        return self.mana_cost[skill] <= self.old_mp

    def attack(self, entity, damage_multiplier=1.0, damage_additive=0.0, multiply_first=False, element=None, can_miss=True, return_damage=False):
        return super().attack(entity, damage_multiplier=damage_multiplier * (1 + self.drive_boost()/100),
                              damage_additive=damage_additive, multiply_first=multiply_first, element=element, can_miss=can_miss, return_damage=return_damage)

    def skill_vent_heat(self):
        if self.attack(self.match.targeted_enemy,
                       damage_multiplier=0.1 * self.heat_level) == constants.ATTACK_CODE_SUCCESS:
            self.match.targeted_enemy.add_effect(effects.vent_heat(self.heat_level))
        self.heat_level = -1

    def skill_tog_drone_tracking(self):
        self.attack(self.match.targeted_enemy, damage_multiplier=0.25)
        self.add_effect(effects.tog_drone)

    def skill_sonic_boom_blaster(self):
        self.match.targeted_enemy.add_effect(effects.booming_noise)
        if self.attack(self.match.targeted_enemy) == constants.ATTACK_CODE_SUCCESS:
            self.match.targeted_enemy.add_effect(effects.sonic_blasted)

    def skill_magnetic_resonance_protocol(self):
        self.attacked(0.2 * self.max_hp, "health")
        self.add_effect(effects.magnetic_personality(0.05 * self.max_hp))

    def skill_mana_eruption(self):
        self.attacked(-0.2 * self.max_mp, "mana")
        mp_percent = (self.mp / self.max_mp) * 100
        self.attack(self.match.targeted_enemy, damage_additive=1.5 * mp_percent)

    def skill_overclock(self):
        for i in range(3):
            self.match.update_player_cooldowns()

    def skill_reactive_barrier(self):
        self.add_effect(effects.barrier)

    def skill_attack(self):
        self.attack(self.match.targeted_enemy)

    def skill_event_horizon(self):
        for i in range(2):
            if self.attack(self.match.targeted_enemy, damage_multiplier=0.55) == constants.ATTACK_CODE_SUCCESS:
                self.match.targeted_enemy.add_effect(effects.crushed)

    def skill_drillbit(self):
        hit = False
        for i in range(3):
            if self.attack(self.match.targeted_enemy, damage_multiplier=0.25) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            self.match.targeted_enemy.add_effect(effects.stunned)

    def skill_enhanced_metallic_aging(self):
        if self.attack(self.match.targeted_enemy) == constants.ATTACK_CODE_SUCCESS:
            dpt = utilities.dot_dpt(self, 1)
            self.match.targeted_enemy.add_effect(effects.rusting(dpt[0], dpt[1]))

    def skill_mana_burst_grenades(self):
        for i in range(3):
            self.attack(self.match.targeted_enemy, damage_multiplier=0.33,
                        damage_additive=max(round(self.stats.WIS / 3), 5))

    def skill_static_overload_blast(self):
        for entity in self.match.enemies:
            self.attack_with_bonus({"bonus": 200}, entity, damage_multiplier=random.randint(115, 125) / 100)

    def skill_photon_bow(self):
        for i in range(3):
            self.attack(self.match.targeted_enemy, damage_multiplier=0.4)

    def skill_force_sword(self):
        for i in range(2):
            self.attack_with_bonus({"crit": 200}, self.match.targeted_enemy, damage_multiplier=0.65)
