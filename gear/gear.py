import json
import os.path
import glob
import sys

import constants


class Item:
    def __init__(self, name, identifier, bonuses, resists):
        self.name = name
        self.identifier = identifier
        self.bonuses = bonuses
        self.resists = resists


class Weapon(Item):
    def __init__(self, name, identifier, dmg_type, element, min_damage, max_damage, bonuses, resists,
                 on_hit_special=constants.DEFAULT_ON_HIT_SPECIAL,
                 on_attack_special=None, on_attack_special_chance=0):
        super().__init__(name, identifier, bonuses, resists)
        self.damage = (min_damage, max_damage)
        self.dmg_type = dmg_type
        self.element = element
        self.on_hit_special = on_hit_special
        self.on_attack_special = on_attack_special
        self.on_attack_special_chance = on_attack_special_chance


class Gear:
    path = f"{os.path.dirname(os.path.abspath(sys.argv[0]))}/gear"

    @staticmethod
    def dict_to_item(item_dict, slot):
        if slot == constants.SLOT_WEAPON:
            return Weapon(item_dict["name"], item_dict["id"], item_dict["dmg_type"], item_dict["element"],
                          item_dict["min_dmg"], item_dict["max_dmg"], item_dict["bonuses"], item_dict["resists"])

        return Item(item_dict["name"], item_dict["id"], item_dict["bonuses"], item_dict["resists"])

    @staticmethod
    def item_to_dict(item, slot):
        if slot == constants.SLOT_WEAPON:
            return {"name": item.name, "id": item.identifier, "dmg_type": item.dmg_type, "element": item.element,
                    "min_dmg": item.damage[0], "max_dmg": item.damage[1], "bonuses": item.bonuses, "resists": item.resists}

        return {"name": item.name, "id": item.identifier, "bonuses": item.bonuses, "resists": item.resists}

    @staticmethod
    def load_item(slot, identifier):
        """
        Loads an item using its slot and identifier
        :param slot: The item's slot
        :param identifier: The item's identifier
        :return: A misc.Item/misc.Weapon object, depends on the item's slot
        """

        return Gear.load_item_using_path(slot, f"{Gear.path}/{slot}/{identifier}.json")

    @staticmethod
    def load_item_using_path(slot, path):
        """
        Loads an item using its slot and path
        :param slot: The item's slot
        :param path: The item's path
        :return: A misc.Item/misc.Weapon object, depends on the item's slot
        """
        item_dict = json.load(open(path, "r"))
        return Gear.dict_to_item(item_dict, slot)

    @staticmethod
    def save_item(item, slot):
        """
        Saves an item to storage
        :param item: The item to save
        :param slot: The item's slot
        """

        item_json = Gear.item_to_dict(item, slot)
        if not os.path.exists(f"{Gear.path}/{slot}"):
            os.mkdir(f"{Gear.path}/{slot}")
        json.dump(item_json, open(f"{Gear.path}/{slot}/{item.identifier}.json", "w"))

    @staticmethod
    def get_gear_list(slot):
        gear_list = []

        for item_path in sorted(glob.glob(f"{Gear.path}/{slot}/*.json")):
            gear_list.append(Gear.load_item_using_path(slot, item_path))

        return gear_list

    @staticmethod
    def get_build(build_index):
        if not os.path.exists(f"{Gear.path}/builds/{build_index}.json"):
            return {}

        build_string = json.load(open(f"{Gear.path}/builds/{build_index}.json", "r"))
        build = {}
        for slot in build_string.keys():
            build[slot] = Gear.load_item(slot, build_string[slot])
        return build

    @staticmethod
    def save_build(build, identifier):
        if not os.path.exists(f"{Gear.path}/builds/"):
            os.mkdir(f"{Gear.path}/builds/")

        json.dump(build, open(f"{Gear.path}/builds/{identifier}.json", "w"))

    @staticmethod
    def get_all_builds():
        if not os.path.exists(f"{Gear.path}/builds/"):
            return {}

        builds = {}
        for build_path in glob.glob(f"{Gear.path}/builds/*.json"):
            build_id = build_path.split("/")[-1].replace(".json", "")
            builds[build_id] = Gear.get_build(build_id)
        return builds