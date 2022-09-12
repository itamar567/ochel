import math

import effects
import classes
import constants
import utilities


class PetKidDragon(classes.Pet):
    def __init__(self, name, player, stats):
        super().__init__(name, player)
        self.targeted_enemy = player.match.targeted_enemy
        self.enemies = player.match.enemies
        self.stats = stats
        self.bonuses = {"crit_multiplier": 1.75, "bonus": math.floor(20 + self.level * 0.5), "crit": 10}
        self.damage = (self.damage[0] + math.ceil((self.level * 0.85 - self.level / 9) * 1.1),
                       self.damage[1] + math.ceil((self.level * 0.85 + self.level / 9) * 1.1))
        self.skills = {"Z": self.skill_primal_fury, " ": self.skill_attack, "M": lambda: None}
        self.skill_names = {"Z": "Fury", " ": "Attack", "M": "Skip"}
        self.cooldowns = {"Z": 19, " ": 0}
        self.armor = "Kid Dragon"
        self.cha_cooldown_reduce = 0

        if self.stats.mischief >= 1:
            self.skills["1"] = self.skill_noxious_fumes
            self.skill_names["1"] = "Stun"
            self.cooldowns["1"] = 19
            if self.stats.mischief >= 100:
                self.skills["0"] = self.skill_tickles
                self.skill_names["0"] = "Tickles"
                self.cooldowns["0"] = 19

        if self.stats.assistance >= 1:
            self.skills["2"] = self.skill_dragon_scout
            self.skill_names["2"] = "Scout"
            self.cooldowns["2"] = 8
            if self.stats.assistance >= 100:
                self.skills["9"] = self.skill_overcharge
                self.skill_names["9"] = "Boost"
                self.cooldowns["9"] = 19

        if self.stats.fighting >= 1:
            self.skills["3"] = self.skill_tail_lash
            self.skill_names["3"] = "Lash"
            self.cooldowns["3"] = 4
            if self.stats.fighting >= 100:
                self.skills["8"] = self.skill_outrage
                self.skill_names["8"] = "Outrage"
                self.cooldowns["8"] = 19

        if self.stats.magic >= 1:
            self.skills["4"] = self.skill_magic_beam
            self.skill_names["4"] = "Blast"
            self.cooldowns["4"] = 4
            if self.stats.magic >= 100:
                self.skills["7"] = self.skill_elemental_supernova
                self.skill_names["7"] = "Nova"
                self.cooldowns["7"] = 19

        if self.stats.protection >= 1:
            self.skills["5"] = self.skill_heal_ally
            self.skill_names["5"] = "Heal"
            self.cooldowns["5"] = 14
            if self.stats.protection >= 100:
                self.skills["6"] = self.skill_dragons_scales
                self.skill_names["6"] = "Scale"
                self.cooldowns["6"] = 19

        self.update_cooldowns_by_cha()
        self.update_skill_images()

    def update_cooldowns_by_cha(self):
        old_cha_cooldown_reduce = self.cha_cooldown_reduce
        self.cha_cooldown_reduce = self.match.player.stats.CHA // 50
        for skill in self.cooldowns.keys():
            self.cooldowns[skill] = max(self.cooldowns[skill] - self.cha_cooldown_reduce + old_cha_cooldown_reduce, 0)

    def skill_attack(self):
        if utilities.chance(self.stats.magic // 400):
            self.attack(self.targeted_enemy, damage_multiplier=(1 + self.stats.magic / 500))
        elif utilities.chance(self.stats.fighting // 400, out_of=1 - self.stats.magic // 400):
            self.attack(self.targeted_enemy, damage_multiplier=(1 + self.stats.fighting / 500),
                        dmg_type=constants.DMG_TYPE_MELEE)
        else:
            self.attack(self.targeted_enemy)

    def skill_primal_fury(self):
        for i in range(3):
            self.attack_with_bonus({"crit": 200}, self.targeted_enemy, damage_multiplier=0.5)

    def skill_noxious_fumes(self):
        self.targeted_enemy.add_effect(effects.noxious_fumes(self.stats.mischief))
        if self.attack(self.targeted_enemy) == constants.ATTACK_CODE_SUCCESS:
            self.targeted_enemy.add_effect(effects.dragon_fumes)

    def skill_dragon_scout(self):
        self.match.player.add_effect(effects.dragon_scout(self.stats.assistance))

    def skill_tail_lash(self):
        if self.attack(self.targeted_enemy, damage_multiplier=(1 + self.stats.fighting // 400),
                       dmg_type=constants.DMG_TYPE_MELEE) == constants.ATTACK_CODE_SUCCESS:
            self.targeted_enemy.add_effect(effects.tail_lash(self.stats.fighting, self.element))

    def skill_magic_beam(self):
        self.attack(self.targeted_enemy, damage_multiplier=(1 + self.stats.magic // 200))

    def skill_heal_ally(self):
        self.match.player.attacked(self.match.player.max_hp * (4 + (2 + self.stats.protection) // 25) / 100, "health", self)

    def skill_dragons_scales(self):
        self.match.player.add_effect(effects.dragons_scales(self.stats.protection))

    def skill_elemental_supernova(self):
        self.attack_with_bonus({"crit": self.stats.magic}, self.targeted_enemy,
                               damage_multiplier=(1 + self.stats.magic / 100))

    def skill_outrage(self):
        hit = False
        for i in range(4):
            if self.attack(self.targeted_enemy,
                           damage_multiplier=(40 + self.stats.fighting / 10) // 100) == constants.ATTACK_CODE_SUCCESS:
                hit = True
        if hit:
            self.targeted_enemy.add_effect(effects.outrage(self.stats.fighting, self.element))

    def skill_overcharge(self):
        self.match.player.add_effect(effects.power_boost(self.stats.assistance))

    def skill_tickles(self):
        self.targeted_enemy.add_effect(effects.tickles(self.stats.mischief))
