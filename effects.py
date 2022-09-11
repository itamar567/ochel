import misc

# Chaosweaver:
soul_gambit = misc.Effect("Soul Gambit", 8, {"mpm": -200, "bpd": -200}, {"all": -60, "health": +60})
empowered_soul_boost = misc.Effect("Soul Boost", 4, {"boost": 175, "bonus": 200}, {})
soul_boost = misc.Effect("Soul Boost", 5, {"boost": 175, "bonus": 200}, {})
empowered_soul_aegis = misc.Effect("Empowered Soul Aegis", 3, {}, {"immobility": 100}, death_proof=True)
soul_aegis = misc.Effect("Soul Aegis", 2, {}, {}, death_proof=True)
soul_hunter = misc.Effect("Soul Hunter", 3, {"crit": 50}, {})
mothbitten = lambda elem, dpt_min, dpt_max: misc.Effect("Mothbitten", 4, {}, {}, dot=(elem, dpt_min, dpt_max))
empowered_mothbitten = lambda elem, dpt_min, dpt_max: \
    misc.Effect("Mothbitten", 10, {}, {}, dot=(elem, dpt_min, dpt_max))
shredded_soul = misc.Effect("Shredded Soul", 1, {}, {}, stun=True)
soul_damage = misc.Effect("Soul Damage", 2, {"bonus": -75}, {})
rippen_soul = misc.Effect("Rippen Soul", 1, {}, {}, stun=True)
empowered_overwhelmed = misc.Effect("Overwhelmed", 4, {}, {"all": -20, "health": 50})
overwhelmed = misc.Effect("Overwhelmed", 4, {}, {"all": -20, "health": 20})
soul_annihilation = lambda damage: misc.Effect("Soul Annihilation", 1, {}, {}, dot=("nan", damage, damage))
soul_torn = lambda dpt_min, dpt_max: misc.Effect("Soul Torn", 1, {}, {}, dot=("nan", dpt_min, dpt_max))

# Technomancer:
vent_heat = lambda heat_level: misc.Effect("Vent Heat", 4, {}, {"health": 5 * heat_level})
tog_drone = misc.Effect("Tog-Drone", 6, {"boost": 50, "bonus": 100, "crit": 50}, {})
booming_noise = misc.Effect("Blooming Noise", 1, {}, {"immobility": -50})
sonic_blasted = misc.Effect("Sonic Blasted", 1, {}, {}, stun=True)
magnetic_personality = lambda hot_value: misc.Effect("Magnetic Personality", 3, {}, {},
                                                        dot=("health", hot_value, hot_value))
barrier = misc.Effect("Barrier", 2, {"mpm": 200}, {})
crushed = misc.Effect("Crushed", 4, {}, {"all": -50, "health": 50})
stunned = misc.Effect("Stunned", 2, {}, {})
rusting = lambda dpt_min, dpt_max: misc.Effect("Rusting", 6, {}, {}, dot=("metal", dpt_min, dpt_max))

# Kid Dragon:
noxious_fumes = lambda mischief: misc.Effect("Noxious Fumes", 1, {}, {"immobility": -mischief//2})
dragon_fumes = misc.Effect("Dragon Fumes", 1, {}, {}, stun=True)
dragon_scout = lambda assistance: misc.Effect("Dragon Scout", 5, {"bonus": assistance//2}, {})
tail_lash = lambda fighting, elem: misc.Effect("Tail Lash", 3, {}, {}, dot=(elem, 5 + fighting//4, 15 + fighting//4))
dragons_scales = lambda protection: misc.Effect("Dragon's Scales", 2, {"mpm": protection}, {})
outrage = lambda fighting, elem: misc.Effect("Outrage", 3, {}, {}, dot=(elem, 5 + fighting // 2, 15 + fighting // 2))
power_boost = lambda assistance: misc.Effect("Power Boost", 3, {"boost": 5 + assistance // 10}, {})
tickles = lambda mischief: misc.Effect("Tickles", 3, {"boost": -mischief // 10}, {"all": -mischief // 20, "health": mischief // 20})

# Oratath:
holy_shield = misc.Effect("Holy Shield", 3, {"bpd": 180}, {})
blind = misc.Effect("Blind", 4, {"bonus": -40}, {})

# Suki:
ritual_charge_30 = misc.Effect("Ritual Charge", 99, {"bonus": 30, "boost": 30}, {"all": 30, "health": -30})
ritual_charge_60 = misc.Effect("Ritual Charge", 99, {"bonus": 60, "boost": 60}, {"all": 60, "health": -60})
ritual_charge_90 = misc.Effect("Ritual Charge", 99, {"bonus": 90, "boost": 90}, {"all": 90, "health": -90})
piercing_blade = misc.Effect("Piercing Blade", 2, {}, {"all": -50, "health": 50})
piercing_lance = misc.Effect("Piercing Lance", 4, {"mpm": -90}, {})
radiant_crush = misc.Effect("Radiant Crush", 4, {}, {"health": 100})
radiant_afterburn = lambda dmg_min, dmg_max, x, y: misc.Effect("Radiant Afterburn", 4, {}, {}, dot=("energy", dmg_min*(x+y)/4, dmg_max*(x+y)/4))
self_repair_mechanism = lambda max_hp: misc.Effect("Self-Repair Mechanism", 3, {}, {}, dot=("health", 0.05*max_hp, 0.05*max_hp))
amplified_reactions = misc.Effect("Amplified Reactions", 1, {}, {})

# Misc:
stuffed = lambda duration: misc.Effect("Stuffed", duration, {}, {})
