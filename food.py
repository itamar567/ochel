import misc
import utilities

food_dict = {}

food_dict["seaweed"] = misc.Food("Seaweed", "seaweed", 6, use_function=utilities.player_full_heal, effect=misc.Effect("Seaweed", "food_seaweed", 3, {"bonus": 10}, {}), max_uses=1)
food_dict["rotten_hardtack"] = misc.Food("Rotten Hardtack", "rotten_hardtack", 6, use_function=utilities.player_full_heal, effect=misc.Effect("Rotten Hardtack", "food_rotten_hardtack", 3, {"bonus": -10}, {}), max_uses=1)
