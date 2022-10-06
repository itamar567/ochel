import random
import math


class Food:
    def __init__(self, name, identifier, stuffed_duration, use_function=None, effect=None, max_uses=math.inf):
        self.name = name
        self.identifier = identifier
        self.stuffed_duration = stuffed_duration
        self.use_function = use_function
        self.effect = effect
        self.max_uses = max_uses

    def use(self, match):
        if self.effect is not None:
            match.player.add_effect(self.effect)
        if self.use_function is not None:
            self.use_function(match)
        match.update_detail_windows()


class Retaliation:
    def __init__(self, dmg_min, dmg_max, multiplier, next_multiplier):
        """
        :param dmg_min: The minimum for the retaliation damage
        :param dmg_max: The maximum for the retaliation damage
        :param multiplier: The multiplier for the retaliation damage
        :param next_multiplier: A function that gets the current multiplier as an input and returns an updated multiplier after receiving a hit
        """
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max
        self.multiplier = multiplier
        self.next_multiplier = next_multiplier

    def get_damage(self):
        dmg = random.randint(self.dmg_min, self.dmg_max)
        dmg *= self.multiplier
        dmg = round(dmg)
        self.multiplier = self.next_multiplier(self.multiplier)  # Update the damage multiplier
        return dmg


class DoT:
    def __init__(self, dmg_min, dmg_max, element, entity, mana=False):
        """
        :param dmg_min: The minimum damage the DoT can do
        :param dmg_max: The maximum damage the DoT can do
        :param element: The element the DoT uses
        :param entity: The entity that inflicted the DoT
        """
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max
        self.element = element
        self.entity = entity
        self.mana = mana

    def get_damage(self):
        return random.randint(self.dmg_min, self.dmg_max)


class Regeneration:
    def __init__(self, get_health, use_health_resistance):
        """
        :param get_health: A function that gets the entity, whether the attack was a crit, whether the attack was a glance, and the damage dealt as an input and returns the amount of health to regenerate
        :param use_health_resistance: Whether to use the entity's health resistance when regenerating
        """
        self.get_health = get_health
        self.use_health_resistance = use_health_resistance


class DamageNegation:
    def __init__(self, direct_multiplier, dot_multiplier):
        """
        :param direct_multiplier: Multiplier for direct damage
        :param dot_multiplier: Multiplier for DoT
        """
        self.direct_multiplier = direct_multiplier
        self.dot_multiplier = dot_multiplier


class DamageReflection:
    def __init__(self, get_damage):
        """
        :param get_damage: A function that gets the damage, whether the attack was a direct attack, the number of times
        a direct attack has been reflected, the number of times a DoT has been reflected and the number of times any
        attack was reflected as an input, and returns the damage to return.
        """
        self._get_damage_function = get_damage
        self.direct_hit_reflect_count = 0
        self.dot_reflect_count = 0
        self.reflect_count = 0

    def get_damage(self, damage, direct):
        if direct:
            self.direct_hit_reflect_count += 1
        else:
            self.dot_reflect_count += 1
        self.reflect_count += 1
        return self._get_damage_function(damage, direct, self.direct_hit_reflect_count, self.dot_reflect_count, self.reflect_count)


class Effect:
    def __init__(self, name, identifier, duration, bonuses, resists, death_proof=False, dot=None, stun=False,
                 refreshable=False, retaliation=None, regeneration=None, damage_negation=None, damage_reflection=None, visible=True):
        self.name = name
        self.identifier = identifier
        self.duration = duration
        self.bonuses = bonuses
        self.resists = resists
        self.death_proof = death_proof
        self.refreshable = refreshable
        self.retaliation = retaliation
        self.regeneration = regeneration
        self.damage_negation = damage_negation
        self.damage_reflection = damage_reflection
        self.dot = dot
        self.stun = stun
        self.visible = visible

    def __eq__(self, other):
        return self.identifier == other.identifier
