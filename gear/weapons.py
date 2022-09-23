import misc
import constants

weaver_blade = misc.Weapon("Weaver Blade", constants.DMG_TYPE_SCYTHE, "metal", 20, 40, {"bonus": 10, "crit": 5}, {})
laser_screwdriver = misc.Weapon("Laser Screwdriver", constants.DMG_TYPE_MELEE, "light", 5, 12, {"crit": 3, "bonus": 1}, {})
frostscythe_iii = misc.Weapon("Frostscythe III", constants.DMG_TYPE_SCYTHE, "ice", 92, 100, {"bpd": 5, "crit": 12, "mpm": 5, "WIS": 5, "END": 5, "CHA": 10, "LUK": 15, "INT": 20, "DEX": 20, "STR": 20, "bonus": 12}, {"all": 10, "health": -20})
