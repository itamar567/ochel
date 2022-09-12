import constants


class Item:
    def __init__(self, bonuses, resists):
        self.bonuses = bonuses
        self.resists = resists


class Weapon(Item):
    def __init__(self, dmg_type, element, min_damage, max_damage, bonuses, resists,
                 on_hit_special=constants.DEFAULT_ON_HIT_SPECIAL):
        super().__init__(bonuses, resists)
        self.damage = (min_damage, max_damage)
        self.dmg_type = dmg_type
        self.element = element
        self.on_hit_special = on_hit_special


class Food:
    def __init__(self, name, stuffed_duration, use_function):
        self.name = name
        self.stuffed_duration = stuffed_duration
        self.use_function = use_function


class Effect:
    def __init__(self, name, duration, bonuses, resists, death_proof=False, dot=None, stun=False, refreshable=False):
        self.name = name
        self.duration = duration
        self.bonuses = bonuses
        self.resists = resists
        self.death_proof = death_proof
        self.refreshable = refreshable
        if dot is None:
            self.dot_elem = None
            self.dot_dpt_min = None
            self.dot_dpt_max = None
        else:
            self.dot_elem = dot[0]
            self.dot_dpt_min = dot[1]
            self.dot_dpt_max = dot[2]
        self.stun = stun
