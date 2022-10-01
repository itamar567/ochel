import constants
import food
from gear import weapons, capes, helmets

name = "Player"
stats = [0, 0, 0, 0, 0, 0, 0]  # By the following order: STR, DEX, INT, CHA, LUK, END, WIS
level = constants.MAX_LEVEL
pet_dragon_name = "Draco"
pet_dragon_element = "fire"
pet_stats = [0, 0, 0, 0, 0]  # By the following order: protection, magic, fighting, assistance, mischief
gear_builds = [{constants.SLOT_WEAPON: weapons.weaver_blade}, {constants.SLOT_WEAPON: weapons.frostscythe_iii, constants.SLOT_BACK: capes.nicks_toasty_cape_viii, constants.SLOT_HEAD: helmets.ancient_dragonlord_helm_iii}]
food_list = [food.seaweed, food.rotten_hardtack_ruby]
