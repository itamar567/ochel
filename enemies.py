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
        self.rollback_resists = [self.resists.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False):
        damage_taken = super().attacked(damage, element, entity, dot, glancing, crit)
        if not dot and effects.holy_shield in self.effects and entity == self.match.player:
            damage = round(self.damage[0] * self.skill_1_multiplier)
            self.match.update_main_log(f"{entity.name} takes {damage} damage.", "p_attacked")
            entity.hp -= damage
            self.skill_1_multiplier /= 2

        return damage_taken

    def reduce_cooldowns(self):
        to_pop = []
        for skill in self.active_cooldowns.keys():
            self.active_cooldowns[skill] -= 1
            if self.active_cooldowns[skill] <= 0:
                to_pop.append(skill)
        for skill in to_pop:
            self.active_cooldowns.pop(skill)

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
