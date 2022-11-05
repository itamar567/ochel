import enemies
import armors
import pets
import food
import classes
import player_values

PLAYER_ARMOR_LIST = (("Chaosweaver", armors.Chaosweaver), ("Technomancer", armors.Technomancer))
ENEMIES_LIST = [("Dummy", [enemies.Dummy]), ("Oratath", [enemies.Oratath]), ("Oratath and Dummy", [enemies.Oratath, enemies.Dummy])]
PETS_LIST = (classes.PetItem(player_values.pet_dragon_name, "pet_kid_dragon", pets.PetKidDragon), classes.PetItem("Baby Chimera", "pet_baby_chimera", pets.BabyChimera))
