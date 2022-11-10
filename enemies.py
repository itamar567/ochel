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


class RedDragon(classes.Enemy):
    def __init__(self, level):
        stats = classes.MainStats([236, 135, 135, 120, 33, 135, 0])
        super().__init__("Red Dragon", stats, level=level, race="???")

        self.general_bonuses["mpm"] = 21
        self.general_bonuses["bpd"] = 20
        self.general_bonuses["bonus"] = 33
        self.general_bonuses["crit"] = 13

        self.general_resists["nature"] = 25
        self.general_resists["stone"] = 25
        self.general_resists["shrink"] = 300
        self.general_resists["immobility"] = 300

        self.element = "stone"
        self.damage = (85, 85)
        self.dmg_type = constants.DMG_TYPE_MELEE

        self.max_hp = 15059
        self.hp = self.max_hp
        self.max_mp = 7192
        self.mp = self.max_mp

        self.skills = {1: self.skill_1, 2: self.skill_2, 3: self.skill_3, 4: self.skill_4, 5: self.skill_5,
                       6: self.skill_6, 7: self.skill_7, 8: self.skill_8, 9: self.skill_9, 10: self.skill_10,
                       11: self.skill_11, 12: self.skill_12, 13: self.skill_13, 14: self.skill_14, 15: self.skill_15}
        self.nature_rotation = [1, 2, 3, 1, 4, 5]
        self.stone_rotation = [6, 7, 8, 6, 9, 10]
        self.nature_frenzied_rotation = [1, 12, 3, 1, 4, 13]
        self.stone_frenzied_rotation = [6, 14, 8, 6, 9, 15]

        # Nature stack is clamp(stacks, 0, 5)
        # Stone stack is clamp(-stacks, 0, 5)
        self.stacks = 0
        self.skill_11_use_count = 0
        self.rage = 0
        self.phase = "nature"
        self.shifted = "none"
        self.frenzied = False
        self.rotation_index = -1
        self.got_hit_of_nature_or_stone_element = False

        # Effects
        self.available_effects.natures_decay = lambda: misc.Effect("Nature's Decay", "red_dragon_natures_decay", 4, {}, {"all": -30, "health": 60})
        self.available_effects.quicken = lambda dpt: misc.Effect("Quicken", "red_dragon_quicken", 4, {}, {}, dot=misc.DoT(dpt[0], dpt[1], "nature", self))
        self.available_effects.solidification = lambda: misc.Effect("Solidification", "red_dragon_solidification", 3, {"crit": -100}, {})
        self.available_effects.stones_throw = lambda: misc.Effect("Stone's Throw", "red_dragon_stones_throw", 4, {"mpm": -125}, {})
        self.available_effects.rocked = lambda: misc.Effect("Rocked", "red_dragon_rocked", 3, {"boost": -30}, {})
        self.available_effects.ride_the_wind = lambda: misc.Effect("Ride the Wind", "red_dragon_ride_the_wind", 3, {"boost": -30}, {})
        self.available_effects.unburdened = lambda use_count: misc.Effect("Unburdened", "red_dragon_unburdened", 6, {"boost": 100 * use_count, "bonus": 50 * use_count}, {})
        self.available_effects.natures_decomposition = lambda: misc.Effect("Nature's Decomposition", "red_dragon_natures_decomposition", 5, {}, {"all": -30, "health": 60})
        self.available_effects.outsped = lambda: misc.Effect("Outsped", "red_dragon_outsped", 3, {"bonus": -40}, {})
        self.available_effects.stones_crush = lambda: misc.Effect("Stone's Crush", "red_dragon_stones_crush", 4, {"mpm": -125}, {})
        self.available_effects.petrification = lambda: misc.Effect("Petrification", "red_dragon_petrification", 3, {"crit": -150}, {})
        self.available_effects.earthen_body = lambda rage: misc.Effect("Earthen Body", "red_dragon_earthen_body", 100, {}, {}, message=f"{rage}/30 rage")
        self.available_effects.earthen_frenzy = lambda stacks: misc.Effect("Earthen Frenzy", "red_dragon_earthen_frenzy", 100, {"boost": 20 * stacks, "mpm": 30 * stacks}, {"all": -2 * stacks, "health": 2 * stacks})
        self.available_effects.earthen_weight = lambda stacks: misc.Effect("Earthen Weight", "red_dragon_earthen_weight", 100, {"boost": 20 * stacks, "mpm": -10 * stacks}, {"all": 15 * stacks, "health": -15 * stacks})

        self.rollback_stacks = [self.stacks]
        self.rollback_skill_11_use_count = [self.skill_11_use_count]
        self.rollback_rage = [self.rage]
        self.rollback_phase = [self.phase]
        self.rollback_shifted = [self.shifted]
        self.rollback_frenzied = [self.frenzied]
        self.rollback_rotation_index = [self.rotation_index]
        self.rollback_general_bonuses = [self.general_bonuses.copy()]
        self.rollback_general_resists = [self.general_resists.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]

    def setup(self):
        super().setup()
        self.add_effect(self.available_effects.earthen_body(self.rage))
        self.rollback_effects = [self.effects.copy()]
        self.rollback_effect_fade_turn = [utilities.copy_dict(self.effects_fade_turn)]

    def update_rollback_data(self):
        super().update_rollback_data()

        self.rollback_stacks.append(self.stacks)
        self.rollback_skill_11_use_count.append(self.skill_11_use_count)
        self.rollback_rage.append(self.rage)
        self.rollback_phase.append(self.phase)
        self.rollback_shifted.append(self.shifted)
        self.rollback_rotation_index.append(self.rotation_index)
        self.rollback_frenzied.append(self.frenzied)

    def rollback(self):
        super().rollback()

        self.stacks = self.rollback_stacks[-2]
        self.rollback_stacks.pop()
        self.skill_11_use_count = self.rollback_skill_11_use_count[-2]
        self.rollback_skill_11_use_count.pop()
        self.rage = self.rollback_rage[-2]
        self.rollback_rage.pop()
        self.phase = self.rollback_phase[-2]
        self.rollback_phase.pop()
        self.rotation_index = self.rollback_rotation_index[-2]
        self.rollback_rotation_index.pop()
        self.shifted = self.rollback_shifted[-2]
        self.rollback_shifted.pop()
        self.frenzied = self.rollback_frenzied[-2]
        self.rollback_frenzied.pop()

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False, inflicts=[], mana_attack=False):
        super().attacked(damage, element, entity=entity, dot=dot, glancing=glancing, crit=crit, inflicts=inflicts, mana_attack=mana_attack)
        if self.hp / self.max_hp <= 1/3:
            self.match.update_main_log("The Red Dragon becomes irrevocably frenzied in it's desperation!", "e_comment")
            self.match.update_main_log("Red Dragon: 'FOOD! FOOD CONSUME!'", "e_comment")
            self.frenzied = True
            self.phase = self.phase + "_frenzied"
            for effect in self.effects:
                if effect.identifier == "red_dragon_earthen_frenzy":
                    self.stacks = 5
                    break
                elif effect.identifier == "red_dragon_earthen_weight":
                    self.stacks = -5
                    break
        if not self.frenzied and not self.got_hit_of_nature_or_stone_element:
            earthen_body, earthen_weight, earthen_frenzy = self.get_earthen_effects()
            if element == "nature":
                self.got_hit_of_nature_or_stone_element = True
                self.shifted = "nature"
                if earthen_body is not None:
                    self.remove_effect(earthen_body)
                if earthen_weight is not None:
                    self.replace_effect(earthen_weight, self.available_effects.earthen_weight(self.stacks))
                else:
                    self.add_effect(self.available_effects.earthen_weight(-self.stacks))
                self.match.update_main_log("The Red Dragon grows more frenzied and more active after absorbing the Nature element attack.", "e_comment")
                self.stacks = min(self.stacks + 1, 5)
            elif element == "stone":
                self.got_hit_of_nature_or_stone_element = True
                self.shifted = "stone"
                if earthen_body is not None:
                    self.remove_effect(earthen_body)
                if earthen_frenzy is not None:
                    self.replace_effect(earthen_frenzy, self.available_effects.earthen_frenzy(-self.stacks))
                else:
                    self.add_effect(self.available_effects.earthen_frenzy(-self.stacks))
                self.match.update_main_log("The Red Dragon becomes more solid after absorbing the Stone element attack.", "e_comment")
                self.stacks = max(self.stacks - 1, -5)
            if self.stacks >= 0:
                self.phase = "nature"
            else:
                self.phase = "stone"

    def use_skill(self, skill_index):
        self.skills[skill_index]()

    def get_earthen_effects(self):
        earthen_body = None
        earthen_weight = None
        earthen_frenzy = None
        for effect in self.effects:
            if effect.identifier == "red_dragon_earthen_body":
                earthen_body = effect
                break
            if effect.identifier == "red_dragon_earthen_weight":
                earthen_weight = effect
                break
            if effect.identifier == "red_dragon_earthen_frenzy":
                earthen_frenzy = effect
                break
        return earthen_body, earthen_weight, earthen_frenzy

    def next(self):
        self.got_hit_of_nature_or_stone_element = False

        # Get the Earthen Body effect
        earthen_body, earthen_weight, earthen_frenzy = self.get_earthen_effects()

        if earthen_body is not None:
            self.rage += 10
        if earthen_frenzy is not None:
            self.rage += 6 - self.stacks
        if earthen_weight is not None:
            self.rage += 6 + self.stacks
        if self.rage < 30:
            self.match.update_main_log(f"Red Dragon's Rage at {self.rage}/30", "e_comment")

        if self.shifted == "nature":
            stacks = self.stacks
            if stacks < 0:
                stacks = 0
            self.add_effect(self.available_effects.earthen_frenzy(stacks))
        elif self.shifted == "stone":
            stacks = -self.stacks
            if stacks < 0:
                stacks = 0
            self.add_effect(self.available_effects.earthen_weight(stacks))

        if self.shifted == "none":
            self.replace_effect(earthen_body, self.available_effects.earthen_body(self.rage))

        if super().next() == constants.ENEMY_STUNNED_STR:
            return constants.ENEMY_STUNNED_STR

        if self.rage >= 30:
            self.use_skill(11)
            return

        self.rotation_index = (self.rotation_index + 1) % 6

        if self.phase == "nature":
            self.use_skill(self.nature_rotation[self.rotation_index])
        elif self.phase == "stone":
            self.use_skill(self.stone_rotation[self.rotation_index])
        elif self.phase == "nature_frenzied":
            self.use_skill(self.nature_frenzied_rotation[self.rotation_index])
        elif self.phase == "stone_frenzied":
            self.use_skill(self.stone_frenzied_rotation[self.rotation_index])

    def skill_1(self):
        for i in range(3):
            self.attack(self.match.player, damage_multiplier=1/3, element="nature")

    def skill_2(self):
        for i in range(3):
            self.attack(self.match.player, damage_multiplier=1/3, element="nature", inflicts=[self.available_effects.natures_decay()])

    def skill_3(self):
        for i in range(2):
            self.attack(self.match.player, damage_multiplier=0.5, element="nature")

    def skill_4(self):
        dpt = utilities.dot_dpt(self, 0.5)
        for i in range(6):
            self.attack(self.match.player, damage_multiplier=0.5, element="nature", inflicts=[self.available_effects.quicken(dpt)])

    def skill_5(self):
        self.match.update_main_log("The Red Dragon inverts its frenzy and solidifies!", "e_comment")
        earthen_frenzy = None
        for effect in self.effects:
            if effect.identifier == "red_dragon_earthen_frenzy":
                earthen_frenzy = effect
        self.replace_effect(earthen_frenzy, self.available_effects.earthen_weight())
        self.attack(self.match.player, inflicts=[self.available_effects.solidification()])

    def skill_6(self):
        self.attack(self.match.player)

    def skill_7(self):
        self.attack(self.match.player, inflicts=[self.available_effects.stones_throw()])

    def skill_8(self):
        self.attack(self.match.player)

    def skill_9(self):
        self.attack(self.match.player, damage_multiplier=3, inflicts=[self.available_effects.rocked()])

    def skill_10(self):
        self.match.update_main_log("The Red Dragon inverts its solidification and becomes frenzied!", "e_comment")
        earthen_weight = None
        for effect in self.effects:
            if effect.identifier == "red_dragon_earthen_weight":
                earthen_weight = effect
        self.replace_effect(earthen_weight, self.available_effects.ride_the_wind())
        self.attack(self.match.player, inflicts=[self.available_effects.solidification()])

    def skill_11(self):
        self.skill_11_use_count += 1
        self.add_effect(self.available_effects.unburdened(self.skill_11_use_count))
        self.match.update_main_log("Red Dragon: 'THE HUNGER CONSUMES ME! I MUST FEED!", "e_comment")
        self.rage = 0

        earthen_body, earthen_weight, earthen_frenzy = self.get_earthen_effects()

        if earthen_body is not None:
            self.replace_effect(earthen_body, self.available_effects.earthen_body(self.rage))
        elif earthen_weight is not None:
            self.replace_effect(earthen_weight, self.available_effects.earthen_body(self.rage))
        elif earthen_frenzy is not None:
            self.replace_effect(earthen_frenzy, self.available_effects.earthen_body(self.rage))

        for i in range(6):
            self.attack(self.match.player, damage_multiplier=10/6)

    def skill_12(self):
        for i in range(3):
            self.attack(self.match.player, element="nature", inflicts=[self.available_effects.natures_decomposition()])

    def skill_13(self):
        for i in range(6):
            self.attack(self.match.player, inflicts=[self.available_effects.outsped()])

    def skill_14(self):
        self.attack(self.match.player, inflicts=[self.available_effects.stones_crush()])

    def skill_15(self):
        for i in range(6):
            self.attack(self.match.player, inflicts=[self.available_effects.petrification()])


class Rolith(classes.Enemy):
    def __init__(self, level):
        stats = classes.MainStats([225, 112, 140, 200, 112, 112, 0])
        super().__init__("Rolith", stats, level=level, race="Human")

        self.general_bonuses["mpm"] = 20
        self.general_bonuses["bpd"] = 30
        self.general_bonuses["bonus"] = 33
        self.general_bonuses["crit"] = 13

        self.general_resists["metal"] = -10
        self.general_resists["light"] = 50
        self.general_resists["nature"] = 20
        self.general_resists["darkness"] = 50

        self.element = "silver"
        self.damage = (98, 98)
        self.dmg_type = constants.DMG_TYPE_MELEE

        self.max_hp = 15883
        self.hp = self.max_hp
        self.max_mp = 7662
        self.mp = self.max_mp

        self.skills = {1: self.skill_1, 2: self.skill_2, 3: self.skill_3, 4: self.skill_4, 5: self.skill_5,
                       6: self.skill_6, 7: self.skill_7, 8: self.skill_8, 9: self.skill_9, 10: self.skill_10,
                       11: self.skill_11}

        self.phase_1_rotation = [1, 2, 3, 4]
        self.phase_2_rotation = [5, 2, 6, 7, 8, 9, 10]
        self.phase = 1
        self.rotation_index = -1

        self.tog_shaken = 0
        self.tog_shaken_count = 0
        self.got_stunned_this_turn = False

        self.tog_queued = 0
        self.tog_order = 0
        self.tog_colors = ["Green", "Yellow", "Red"]

        # Effects
        self.available_effects.tog_shaken = lambda: misc.Effect("Tog Shaken", "rolith_tog_shaken", 1, {}, {}, stun=True)
        self.available_effects.durability = lambda tog_shaken_count: misc.Effect("Durability", "rolith_durability", 99, {"boost": 10 * tog_shaken_count}, {"immobility": 50 * tog_shaken_count})
        self.available_effects.tog_order_even = lambda duration: misc.Effect("Tog Order Even", "rolith_tog_order_even", duration + 1, {}, {}, message="Target's HP should be Even when resolved")
        self.available_effects.tog_order_odd = lambda duration: misc.Effect("Tog Order Odd", "rolith_tog_order_odd", duration + 1, {}, {}, message="Target's HP should be Odd when resolved")
        self.available_effects.tog_queued = lambda color: misc.Effect("Tog Queued", "rolith_tog_queued", 100, {}, {}, message=f"{color} Tog Queued")
        self.available_effects.green_tog_reward = lambda: misc.Effect("Green Tog Reward", "rolith_green_tog_reward", 2, {"bonus": 30}, {})
        self.available_effects.yellow_tog_reward = lambda: misc.Effect("Yellow Tog Reward", "rolith_yellow_tog_reward", 2, {"boost": 15}, {})
        self.available_effects.red_tog_reward = lambda: misc.Effect("Red Tog Reward", "rolith_red_tog_reward", 2, {"boost": 10, "bonus": 10}, {})
        self.available_effects.punisher = lambda: misc.Effect("Punisher", "rolith_punisher", 2, {"boost": 200, "bonus": 200}, {})
        self.available_effects.field_goal = lambda boost_value: misc.Effect("Field Goal", "rolith_field_goal", 1, {"boost": -boost_value}, {})
        self.available_effects.hammer_up = lambda: misc.Effect("Hammer UP", "rolith_hammer_up", 5, {"bonus": 50, "crit": 100}, {})
        self.available_effects.green_potion = lambda: misc.Effect("Green Potion", "rolith_green_potion", 4, {"mpm": 80}, {})
        self.available_effects.yellow_potion = lambda: misc.Effect("Yellow Tog Reward", "rolith_yellow_potion", 4, {"boost": 50}, {})
        self.available_effects.red_potion = lambda: misc.Effect("Red Tog Reward", "rolith_red_potion", 4, {"bonus": 50}, {})

        self.rollback_phase = [self.phase]
        self.rollback_phase_2_rotation = [self.phase_2_rotation.copy()]
        self.rollback_rotation_index = [self.rotation_index]
        self.rollback_tog_shaken = [self.tog_shaken]
        self.rollback_tog_shaken_count = [self.tog_shaken_count]
        self.rollback_tog_queued = [self.tog_queued]
        self.rollback_tog_order = [self.tog_order]

        self.rollback_general_bonuses = [self.general_bonuses.copy()]
        self.rollback_general_resists = [self.general_resists.copy()]
        self.rollback_hp = [self.hp]
        self.rollback_mp = [self.mp]

    def get_tog_order(self):
        for effect in self.effects:
            if effect.identifier == "rolith_tog_order_even":
                return 0
            elif effect.identifier == "rolith_tog_order_odd":
                return 1

    def add_effect(self, effect):
        if effect.stun:
            if self.got_stunned_this_turn:
                return

            self.match.update_main_log("Rolith manages to shake off some of your stun.", "e_comment")
            self.tog_shaken_count += 1
            self.add_effect(self.available_effects.durability(self.tog_shaken_count))
            self.got_stunned_this_turn = True

            if self.tog_shaken > 0:
                return

            effect = self.available_effects.tog_shaken()
            self.tog_shaken = 2

        super().add_effect(effect)

    def update_rollback_data(self):
        super().update_rollback_data()

        self.rollback_phase.append(self.phase)
        self.rollback_phase_2_rotation.append(self.phase_2_rotation.copy())
        self.rollback_rotation_index.append(self.rotation_index)
        self.rollback_tog_shaken.append(self.tog_shaken)
        self.rollback_tog_shaken_count.append(self.tog_shaken_count)
        self.rollback_tog_queued.append(self.tog_queued)
        self.rollback_tog_order.append(self.tog_order)

    def rollback(self):
        super().rollback()

        self.phase = self.rollback_phase[-2]
        self.rollback_phase.pop()
        self.phase_2_rotation = self.rollback_phase_2_rotation[-2].copy()
        self.rollback_phase_2_rotation.pop()
        self.rotation_index = self.rollback_rotation_index[-2]
        self.rollback_rotation_index.pop()
        self.tog_shaken = self.rollback_tog_shaken[-2]
        self.rollback_tog_shaken.pop()
        self.tog_shaken_count = self.rollback_tog_shaken_count[-2]
        self.rollback_tog_shaken_count.pop()
        self.tog_queued = self.rollback_tog_queued[-2]
        self.rollback_tog_queued.pop()
        self.tog_order = self.rollback_tog_order[-2]
        self.rollback_tog_order.pop()

    def attacked(self, damage, element, entity=None, dot=False, glancing=False, crit=False, inflicts=[], mana_attack=False, increase_tog_queued=True):
        result = super().attacked(damage, element, entity=entity, dot=dot, glancing=glancing, crit=crit, inflicts=inflicts, mana_attack=mana_attack)

        if increase_tog_queued and not dot and not glancing:
            self.tog_queued = (self.tog_queued + 1) % len(self.tog_colors)

            old_tog_queued_effect = None
            tog_order_effect = None
            for effect in self.effects:
                if effect.identifier == "rolith_tog_queued":
                    old_tog_queued_effect = effect
                elif effect.identifier in ("rolith_tog_order_even", "rolith_tog_order_odd"):
                    tog_order_effect = effect

            if tog_order_effect is None:
                return result

            new_tog_queued_effect = self.available_effects.tog_queued(self.tog_colors[self.tog_queued])
            if old_tog_queued_effect is None:
                self.add_effect(new_tog_queued_effect)
            else:
                self.replace_effect(old_tog_queued_effect, new_tog_queued_effect)
        return result

    def use_skill(self, skill_index):
        self.skills[skill_index]()

    def next(self):
        self.got_stunned_this_turn = False

        if self.tog_shaken > 0:
            self.tog_shaken -= 1

        if super().next() == constants.ENEMY_STUNNED_STR:
            return constants.ENEMY_STUNNED_STR

        self.rotation_index += 1

        if self.phase == 1:
            if self.rotation_index > len(self.phase_1_rotation) - 1:
                self.phase = 2
                self.rotation_index = 0
            else:
                self.use_skill(self.phase_1_rotation[self.rotation_index])
        if self.phase == 2:
            self.rotation_index %= len(self.phase_2_rotation)
            self.use_skill(self.phase_2_rotation[self.rotation_index])

    def check_tog_order(self):
        self.match.update_main_log("Rolith: 'Let's check the results!'", "e_comment")
        self.match.player.attacked(self.tog_queued + 1, element="null", entity=self)

        if self.match.player.hp % 2 == self.get_tog_order():
            self.match.update_main_log("Rolith: 'Well done! The togs shall reward you!'", "e_comment")
            if self.tog_queued == 0:
                self.match.player.add_effect(self.available_effects.green_tog_reward())
            elif self.tog_queued == 1:
                self.match.player.add_effect(self.available_effects.yellow_tog_reward())
            else:
                self.match.player.add_effect(self.available_effects.red_tog_reward())
            return True

        self.match.update_main_log("Rolith: 'Incorrect! It's pummeling time!'", "e_comment")
        self.add_effect(self.available_effects.punisher())
        return False

    def skill_1(self):
        self.match.update_main_log("Rolith: 'Unleash the togs!'", "e_comment")

        for effect in self.effects:
            if effect.identifier in ("rolith_tog_order_even", "rolith_tog_order_odd"):
                self.remove_effect(effect)

        if utilities.chance(0.5):
            effect = self.available_effects.tog_order_even(3)
        else:
            effect = self.available_effects.tog_order_odd(3)

        self.add_effect(effect)

        for i in range(1, 4):
            self.match.player.attacked(i, "null", entity=self)

        self.attack(self.match.player, damage_multiplier=3, element="metal")

    def skill_2(self):
        for i in range(2):
            self.attack(self.match.player)

    def skill_3(self):
        self.match.update_main_log("Rolith: 'Are you ready?'", "e_comment")
        self.attack(self.match.player, inflicts=[self.available_effects.field_goal(10)])

    def skill_4(self):
        self.check_tog_order()

        self.attack(self.match.player, damage_multiplier=3)

    def skill_5(self):
        self.match.update_main_log("Rolith: 'Let's keep this tog rolling!'", "e_comment")

        for effect in self.effects:
            if effect.identifier in ("rolith_tog_order_even", "rolith_tog_order_odd"):
                self.remove_effect(effect)

        if utilities.chance(0.5):
            effect = self.available_effects.tog_order_even(5)
        else:
            effect = self.available_effects.tog_order_odd(5)

        self.add_effect(effect)

        self.attack(self.match.player, damage_multiplier=3)

    def skill_6(self):
        self.add_effect(self.available_effects.hammer_up())

        for i in range(2):
            self.attack(self.match.player)

    def skill_7(self):
        self.match.update_main_log("Rolith 'I need some help! Alina, toss me a potion, please!'", "e_comment")
        if self.tog_queued == 0:
            self.add_effect(self.available_effects.green_potion())
        elif self.tog_queued == 1:
            self.add_effect(self.available_effects.yellow_potion())
        else:
            self.add_effect(self.available_effects.red_potion())

        self.attacked(self.max_hp / 10, element="health", entity=self, increase_tog_queued=False)
        self.attack(self.match.player, damage_multiplier=2)

    def skill_8(self):
        self.match.update_main_log("Rolith: 'Are you ready?'", "e_comment")
        self.attack(self.match.player, damage_multiplier=2, inflicts=[self.available_effects.field_goal(25)])

    def skill_9(self):
        if not self.check_tog_order():
            self.phase_2_rotation[6] = 11

        for i in range(2):
            self.attack(self.match.player, damage_multiplier=1.5)

    def skill_10(self):
        self.match.update_main_log("Rolith: 'The togs love you! Wait, no! They can't keep themselves back!'", "e_comment")
        for i in range(5):
            self.attack(self.match.player)

    def skill_11(self):
        self.match.update_main_log("Rolith: 'Looks like I'm going to have to knock some sense into you!'", "e_comment")
        for i in range(9):
            self.attack(self.match.player)
