import classes
import constants
import misc
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
        super().__init__("Oratath", stats, level=level, race="dragon")

        self.general_bonuses["mpm"] = 3
        self.general_bonuses["parry"] = 1
        self.general_bonuses["dodge"] = 2
        self.general_bonuses["bonus"] = 23
        self.general_bonuses["crit"] = 5

        self.general_resists["immobility"] = 75

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

        self.rollback_general_bonuses = [self.general_bonuses.copy()]
        self.rollback_general_resists = [self.general_resists.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]
        self.rollback_active_cooldowns = [self.active_cooldowns.copy()]

        # Effects
        self.available_effects.holy_shield = lambda: misc.Effect("Holy Shield", "oratath_holy_shield", 3, {"bpd": 180}, {}, retaliation=misc.Retaliation(self.damage[0], self.damage[1], 0.75, lambda multiplier: multiplier/2))
        self.available_effects.blind = lambda: misc.Effect("Blind", "oratath_blind", 4, {"bonus": -40}, {})

    def reduce_cooldowns(self):
        to_pop = []
        for skill in self.active_cooldowns.keys():
            self.active_cooldowns[skill] -= 1
            if self.active_cooldowns[skill] <= 0:
                to_pop.append(skill)
        for skill in to_pop:
            self.active_cooldowns.pop(skill)

    def update_rollback_data(self):
        super().update_rollback_data()

        self.rollback_active_cooldowns.append(self.active_cooldowns.copy())

    def rollback(self):
        super().rollback()

        self.active_cooldowns = self.rollback_active_cooldowns[-2].copy()
        self.rollback_active_cooldowns.pop()

    def next(self):
        if super().next() == constants.ENEMY_STUNNED_STR:
            return constants.ENEMY_STUNNED_STR

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
        self.add_effect(self.available_effects.holy_shield())
        self.skill_1_multiplier = 0.75
        for i in range(4):
            self.attack(self.match.player)

    def skill_2(self):
        for i in range(4):
            self.attack(self.match.player)

    def skill_3(self):
        self.match.update_main_log("Blinded by Oratath's light!", "e_comment")
        for i in range(4):
            self.attack(self.match.player, inflicts=[self.available_effects.blind()])

    def skill_4(self):
        self.match.update_main_log("Oratath regenerates!", "e_comment")
        self.attacked(self.max_hp / 2, "health")
        self.attack(self.match.player)

    def skill_5(self):
        self.attack(self.match.player, damage_multiplier=3)
