import misc
import utilities


def _cocoaberry_juice_use_func(match):
    dot_value = round(match.player.max_hp/10)
    match.player.attacked(dot_value, element="health", entity=match.player, dot=True)
    match.player.add_effect(misc.Effect("Cocoaberry Juice", "food_cocoaberry_juice", 9, {}, {}, dot=misc.DoT(dot_value, dot_value, "health", match.player)))


def _instant_pierogi_use_func(match):
    dot_value = round(match.player.max_mp/10)
    match.player.attacked(dot_value, element="health", entity=match.player, dot=True, mana_attack=True)
    match.player.add_effect(misc.Effect("Instant Pierogi", "food_instant_pierogi", 9, {}, {}, dot=misc.DoT(dot_value, dot_value, "health", match.player, mana=True)))


def _peculiar_pellets_use_func(match):
    for effect in match.player.effects.copy():
        if effect.dot is not None:
            match.player.remove_effect(effect)


food_dict = {}

food_dict["gorillaphant_knuckles"] = misc.Food("Gorillaphant Knuckles", "gorillaphant_knuckles", 11, effect=misc.Effect("Gorillaphant Knuckles", "food_gorillaphant_knuckles", 30, {"STR": 50}, {}))
food_dict["ravens_wings"] = misc.Food("Raven's Wings", "ravens_wings", 11, effect=misc.Effect("Raven's Wings", "food_ravens_wings", 30, {"DEX": 50}, {}))
food_dict["baked_basilisk"] = misc.Food("Baked Basilisk", "baked_basilisk", 11, effect=misc.Effect("Baked Basilisk", "food_baked_basilisk", 30, {"INT": 50}, {}))
food_dict["serene_bread"] = misc.Food("Serene Bread", "serene_bread", 6, effect=misc.Effect("Serene Bread", "food_serene_bread", 4, {"END": 25}, {}))
food_dict["sparkys_cookie"] = misc.Food("Sparky's Cookie", "sparkys_cookie", 6, effect=misc.Effect("Sparky's Cookie", "food_sparkys_cookie", 4, {"END": 25}, {}))
food_dict["zardcakes_plus"] = misc.Food("Zardcakes+", "zardcakes_plus", 11, effect=misc.Effect("Zardcakes+", "food_zardcakes_plus", 30, {"LUK": 40}, {}))
food_dict["zard_kebobs_plus"] = misc.Food("Zard-Kebobs+", "zard_kebobs_plus", 11, effect=misc.Effect("Zard-Kebobs+", "food_zard_kebobs_plus", 2, {"bonus": 100}, {}))
food_dict["fried_zard_legs_plus"] = misc.Food("Fried Zard Legs+", "fried_zard_legs_plus", 11, effect=misc.Effect("Fried Zard Legs+", "food_fried_zard_legs_plus", 5, {"crit": 50}, {}))
food_dict["zard_burgers_plus"] = misc.Food("Zard Burgers+", "zard_burgers_plus", 31, effect=misc.Effect("Zard Burgers+", "food_zard_burgers_plus", 4, {"bpd": 140}, {}))
food_dict["seaweed"] = misc.Food("Seaweed", "seaweed", 6, use_function=utilities.player_full_heal, effect=misc.Effect("Seaweed", "food_seaweed", 3, {"bonus": 10}, {}), max_uses=1)
food_dict["rotten_hardtack"] = misc.Food("Rotten Hardtack", "rotten_hardtack", 6, use_function=utilities.player_full_heal, effect=misc.Effect("Rotten Hardtack", "food_rotten_hardtack", 3, {"bonus": -10}, {}), max_uses=1)
food_dict["cocoaberry_juice"] = misc.Food("Cocoaberry Juice", "cocoaberry_juice", 31, use_function=_cocoaberry_juice_use_func, effect=misc.Effect("Cocoaberry Warmth", "food_cocoaberry_juice_cocoaberry_warmth", 10, {"crit": -50}, {}), max_uses=1)
food_dict["instant_pierogi"] = misc.Food("Instant Pierogi", "instant_pierogi", 6, use_function=_instant_pierogi_use_func, effect=misc.Effect("Pierogi Overload", "food_instant_pierogi_pierogi_overload", 10, {"boost": -10}, {}))
food_dict["peculiar_pellets"] = misc.Food("Peculiar Pellets", "peculiar_pellets", 4, use_function=_peculiar_pellets_use_func)
