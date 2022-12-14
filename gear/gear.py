import json
import os.path
import glob
import sys

import constants
import utilities
from gear.weapon_specials import weapon_specials


class Item:
    def __init__(self, name, identifier, bonuses, resists, default=False):
        self.name = name
        self.identifier = identifier
        self.bonuses = bonuses
        self.resists = resists
        self.default = default


class Trinket(Item):
    def __init__(self, name, identifier, bonuses, resists, ability_func=None, ability_mana_cost=0, ability_cooldown=0, ability_name="", ability_img_name=None):
        """
        Creates a trinket
        :param name: The trinket's name
        :param identifier: The trinket's id
        :param bonuses: The trinket's bonuses
        :param resists: The trinket's resistances
        :param ability_func: The trinket's ability (defaults to None when the trinket doesn't have an ability). Receives the match as an input.
        """
        super().__init__(name, identifier, bonuses, resists)

        self.ability_func = ability_func
        self.ability_mana_cost = ability_mana_cost
        self.ability_cooldown = ability_cooldown
        self.ability_name = ability_name
        self.ability_img_path = "resources/images/trinkets/"
        if ability_img_name is None:
            self.ability_img_path += f"{identifier}.png"
        else:
            self.ability_img_path += f"{ability_img_name}.png"


class Weapon(Item):
    def __init__(self, name, identifier, dmg_type, element, min_damage, max_damage, bonuses, resists, default=False):
        super().__init__(name, identifier, bonuses, resists, default=default)
        self.damage = (min_damage, max_damage)
        self.dmg_type = dmg_type
        self.element = element


class Gear:
    path = ""
    all_items_in_resources_by_slot = {}
    all_items_in_resources_by_id = {}
    max_lvl_items_in_resources_by_slot = {}
    max_lvl_items_in_resources_by_id = {}
    only_max_lvl_items = True

    @staticmethod
    def setup():
        # Setup the app data path
        Gear.path = os.path.expanduser('~')  # Home directory
        if sys.platform == "win32":
            Gear.path += "/AppData/Roaming"
        elif sys.platform == "linux":
            Gear.path += "/.local/share"
        elif sys.platform == "darwin":
            Gear.path += "/Library/Application Support"
        else:
            Gear.path = os.path.dirname(os.path.abspath(sys.argv[0]))  # The directory the program was executed in
        Gear.path += "/OCHEL"

        # Setup items_in_resources_by_slot and items_in_resources_by_id
        for slot in constants.INVENTORY_SLOTS:
            if slot == constants.SLOT_WEAPON_SPECIAL:
                continue

            Gear.all_items_in_resources_by_slot[slot] = []
            Gear.max_lvl_items_in_resources_by_slot[slot] = []

            for item_dict in sorted(json.load(open(utilities.resource_path(f"resources/items/all/{slot}.json"), "r")), key=lambda item: item["name"]):
                item = Gear.dict_to_item(item_dict, slot)
                Gear.all_items_in_resources_by_slot[slot].append(item)
                Gear.all_items_in_resources_by_id[item_dict["id"]] = item

            for item_dict in sorted(json.load(open(utilities.resource_path(f"resources/items/max_lvl/{slot}.json"), "r")), key=lambda item: item["name"]):
                item = Gear.dict_to_item(item_dict, slot)
                Gear.max_lvl_items_in_resources_by_slot[slot].append(item)
                Gear.max_lvl_items_in_resources_by_id[item_dict["id"]] = item

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
        :return: A misc.Item/misc.Weapon/weapon_specials.WeaponSpecial object, depends on the item's slot
        """

        if slot == constants.SLOT_WEAPON_SPECIAL:
            return weapon_specials[identifier]

        if identifier in Gear.all_items_in_resources_by_id:
            item = Gear.all_items_in_resources_by_id[identifier]
        else:
            item = Gear.load_item_using_path(slot, f"{Gear.path}/{slot}/{identifier}.json")

        return item

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
        if slot == constants.SLOT_WEAPON_SPECIAL:
            return list(weapon_specials.values())
        if slot in (constants.SLOT_TRINKET, constants.SLOT_PET):
            return []

        gear_list = []
        for item_path in sorted(glob.glob(f"{Gear.path}/{slot}/*.json")):
            gear_list.append(Gear.load_item_using_path(slot, item_path))
        if Gear.only_max_lvl_items:
            gear_list.extend(Gear.max_lvl_items_in_resources_by_slot[slot])
        else:
            gear_list.extend(Gear.all_items_in_resources_by_slot[slot])

        return gear_list

    @staticmethod
    def get_build(build_index):
        if not os.path.exists(f"{Gear.path}/builds/{build_index}.json"):
            return {}

        build_string = json.load(open(f"{Gear.path}/builds/{build_index}.json", "r"))
        build = {}
        for slot in build_string.keys():
            if slot == constants.SLOT_WEAPON_SPECIAL:
                build[slot] = weapon_specials[build_string[slot]]
            build[slot] = Gear.load_item(slot, build_string[slot])
        return build

    @staticmethod
    def save_build(build, identifier):
        if not os.path.exists(f"{Gear.path}/builds/"):
            os.mkdir(f"{Gear.path}/builds/")

        json.dump(build, open(f"{Gear.path}/builds/{identifier}.json", "w"))


Gear.setup()
