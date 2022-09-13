import math

import classes
import constants
import effects
import utilities


class Dummy(classes.Enemy):
    def __init__(self, level=constants.MAX_LEVEL):
        super().__init__("Dummy", classes.MainStats([0] * 7), level=level)
        self.max_hp = 100000
        self.max_mp = 50
        self.hp = 100000
        self.mp = 50
        self.element = "none"

        self.rollback_mp = [self.mp]
        self.rollback_hp = [self.hp]


class Oratath(classes.Enemy):
    def __init__(self, level):
        stats = classes.MainStats([16, 16, 16, 0, 0, 22, 0])
        super().__init__("Oratath", stats, level=level)

        self.bonuses["mpm"] = 3
        self.bonuses["parry"] = 1
        self.bonuses["dodge"] = 2
        self.bonuses["bonus"] = 23
        self.bonuses["crit"] = 5

        self.resists["immobility"] = 75

        self.element = "good"
        self.damage = (76, 76)
        self.dmg_type = constants.DMG_TYPE_MELEE

        self.max_hp = 12467
        self.hp = self.max_hp
        self.max_mp = 6179
        self.mp = self.max_mp

        self.cooldowns = {"1": 6, "2": 0, "3": 10, "4": 20}
        self.active_cooldowns = {}
        self.skills = {"1": self.skill_1, "2": self.skill_2, "3": self.skill_3, "4": self.skill_4, "5": self.skill_5}

        self.skill_1_multiplier = 0.75  # Oratath's attack 1's damage halves each time

        self.rollback_bonuses = [self.bonuses.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False):
        super().attacked(damage, element, entity, dot, glancing, crit)
        if not dot and effects.holy_shield in self.effects and entity == self.match.player:
            damage = round(self.damage[0] * self.skill_1_multiplier)
            self.match.update_main_log(f"{entity.name} takes {damage} damage.", f"p_attacked")
            entity.hp -= damage
            self.skill_1_multiplier /= 2

    def reduce_cooldowns(self):
        to_pop = []
        for skill in self.active_cooldowns.keys():
            self.active_cooldowns[skill] -= 1
            if self.active_cooldowns[skill] <= 0:
                to_pop.append(skill)
        for skill in to_pop:
            self.active_cooldowns.pop(skill)

    def next(self):
        super().next()

        attacked = False
        for attack in ("1", "2", "3", "4"):
            if self.active_cooldowns.get(attack, 0) == 0:
                if attack == "2" and utilities.chance(0.5):  # Attack 2 has a 50% chance to be used
                    continue
                self.match.update_main_log(f"Oratath uses attack {attack}.", "e_comment")
                self.skills[attack]()
                self.reduce_cooldowns()
                self.active_cooldowns[attack] = self.cooldowns[attack]
                attacked = True
                break
        if not attacked:
            self.match.update_main_log(f"Oratath uses attack 5", "e_comment")
            self.skills["5"]()

    def skill_1(self):
        self.match.update_main_log("Mystical energies surround Oratath!", "e_comment")
        self.add_effect(effects.holy_shield)
        self.skill_1_multiplier = 0.75
        for i in range(4):
            self.attack(self.match.player)

    def skill_2(self):
        for i in range(4):
            self.attack(self.match.player)

    def skill_3(self):
        self.match.update_main_log("Blinded by Oratath's light!", "e_comment")
        hit = False
        for i in range(4):
            if self.attack(self.match.player) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            self.match.player.add_effect(effects.blind)

    def skill_4(self):
        self.match.update_main_log("Oratath regenerates!", "e_comment")
        self.attacked(self.max_hp / 2, "health")
        self.attack(self.match.player)

    def skill_5(self):
        self.attack(self.match.player, damage_multiplier=3)


class Suki(classes.Enemy):
    def __init__(self, level):
        stats = classes.MainStats([225, 225, 225, 200, 140, 225, 0])
        super().__init__("Suki", stats, level=level)

        self.element = "light"
        self.damage = (136, 136)
        self.dmg_type = constants.DMG_TYPE_MELEE

        self.bonuses["mpm"] = 32
        self.bonuses["bpd"] = 25
        self.bonuses["crit"] = 34
        self.bonuses["bonus"] = 38

        self.resists["immobility"] = 300

        self.max_hp = 13532
        self.hp = self.max_hp
        self.max_mp = 6204
        self.mp = self.max_mp

        self.skills = {"1": self.skill_1, "2": self.skill_2, "3": self.skill_3, "4": self.skill_4, "5": self.skill_5,
                       "6": self.skill_6, "7": self.skill_7, "8": self.skill_8, "9": self.skill_9, "10": self.skill_10}
        self.skill_1_use_count = 0  # Used for attack 9
        self.skill_8_use_count = 0  # Used for attack 9
        self.last_attack = 1
        self.turn = 0  # Using a different turn variable will allow to only update it when Suki is not stunned

        self.rollback_bonuses = [self.bonuses.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]
        self.rollback_last_attack = [self.last_attack]
        self.rollback_turn = [self.turn]
        self.rollback_skill_1_use_count = [self.skill_1_use_count]
        self.rollback_skill_8_use_count = [self.skill_8_use_count]

    def update_rollback_data(self):
        super().update_rollback_data()
        self.rollback_last_attack.append(self.last_attack)
        self.rollback_turn.append(self.turn)
        self.rollback_skill_1_use_count.append(self.skill_1_use_count)
        self.rollback_skill_8_use_count.append(self.skill_8_use_count)

    def rollback(self):
        super().rollback()
        self.last_attack = self.rollback_last_attack[-2]
        self.rollback_last_attack.pop()
        self.turn = self.rollback_turn[-2]
        self.rollback_turn.pop()
        self.skill_1_use_count = self.rollback_skill_1_use_count[-2]
        self.rollback_skill_1_use_count.pop()
        self.skill_8_use_count = self.rollback_skill_8_use_count[-2]
        self.rollback_skill_8_use_count.pop()

    def player_double_turn_reaction(self):
        super().player_double_turn_reaction()
        self.match.update_main_log("Suki's armor sparks in anticipation of your next attack!", "e_comment")
        self.add_effect(effects.amplified_reactions)

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False):
        super().attacked(damage, element, entity, dot, glancing, crit)
        if not dot and effects.amplified_reactions in self.effects and entity == self.match.player:
            damage *= 0.5
            damage = math.ceil(damage)
            self.match.update_main_log(f"{entity.name} takes {damage} damage.", f"p_attacked")
            entity.hp -= damage

    def next(self):
        if super().next() == constants.ENEMY_STUNNED_STR:
            return constants.ENEMY_STUNNED_STR
        self.turn += 1
        if self.turn == 1 or (self.turn - 50) % 37 == 0:
            self.match.update_main_log("Suki uses attack 1.", "e_comment")
            self.skill_1()
            return
        self.last_attack = 2 if self.last_attack == 10 else self.last_attack + 1
        self.match.update_main_log(f"Suki uses attack {self.last_attack}.", "e_comment")
        self.skills[str(self.last_attack)]()

    def skill_1(self):
        self.skill_1_use_count += 1
        old_damage = self.damage
        self.damage = (0, 0)
        for i in range(3):
            self.attack(self.match.player, can_miss=False)
        self.damage = old_damage
        self.match.player.hp = max(self.match.player.hp - self.match.player.max_hp // 2, 1)
        self.match.update_main_log("So you still stand? Impressive...", "e_comment")

    def skill_2(self):
        self.add_effect(effects.ritual_charge_30)
        self.attack(self.match.player, element="energy")

    def skill_3(self):
        if self.attack(self.match.player, element="energy") == constants.ATTACK_CODE_SUCCESS:
            self.match.player.add_effect(effects.piercing_blade)

    def skill_4(self):
        self.attack(self.match.player, damage_multiplier=2)

    def skill_5(self):
        self.add_effect(effects.ritual_charge_60)
        for i in range(2):
            self.attack(self.match.player, element="energy")

    def skill_6(self):
        hit = False
        for i in range(2):
            if self.attack(self.match.player) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            self.match.player.add_effect(effects.piercing_lance)

    def skill_7(self):
        hit = False
        for i in range(3):
            if self.attack(self.match.player) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            self.match.player.add_effect(effects.radiant_crush)

    def skill_8(self):
        self.skill_8_use_count += 1
        self.add_effect(effects.ritual_charge_90)
        self.attack(self.match.player, element="energy")

    def skill_9(self):
        hit = False
        for i in range(4):
            if self.attack(self.match.player) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            self.match.player.add_effect(effects.radiant_afterburn(self.damage[0], self.damage[1],
                                                                   self.skill_8_use_count, self.skill_1_use_count))
            for effect in [eff for eff in self.effects if eff.name == "Ritual Charge"]:
                self.remove_effect(effect)

    def skill_10(self):
        self.add_effect(effects.self_repair_mechanism(self.max_hp))
        for i in range(2):
            self.attack(self.match.player, element="energy")
