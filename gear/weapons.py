import constants
from gear.gear import Weapon

weaver_blade = Weapon("Weaver Blade", "chaosweaver_default_weaver_blade", constants.DMG_TYPE_SCYTHE, "metal", 20, 40, {"bonus": 10, "crit": 5}, {})
laser_screwdriver = Weapon("Laser Screwdriver", "technomancer_default_laser_screwdriver", constants.DMG_TYPE_MELEE, "light", 5, 12, {"crit": 3, "bonus": 1}, {})
dragonblade = Weapon("DragonBlade", "bulwark_dragonlord_default_dragonblade", constants.DMG_TYPE_MELEE, "metal", 5, 10, {"bonus": 1}, {})
