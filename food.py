import misc
import utilities

_seaweed_effect = misc.Effect("Seaweed", "food_seaweed", 3, {"bonus": 10}, {})
def _use_seaweed(match):
    utilities.player_full_heal(match)
    match.player.add_effect(_seaweed_effect)
seaweed = misc.Food("Seaweed", 6, _use_seaweed)

_rotten_hardtack_ruby_effect = misc.Effect("Rotten Hardtack (Ruby)", "food_rotten_hardtack_ruby", 11, {"bonus": -10}, {})
_rotten_hardtack_fortress_effect = misc.Effect("Rotten Hardtack (Drowned Fortress)", "food_rotten_hardtack_drowned_fortress", 3, {"bonus": -10}, {})
def _use_rotten_hardtack_ruby(match):
    utilities.player_full_heal(match)
    match.player.add_effect(_rotten_hardtack_ruby_effect)
def _use_rotten_hardtack_fortress(match):
    utilities.player_full_heal(match)
    match.player.add_effect(_rotten_hardtack_fortress_effect)
rotten_hardtack_ruby = misc.Food("Rotten Hardtack (Ruby)", 6, _use_rotten_hardtack_ruby)
rotten_hardtack_fortress = misc.Food("Rotten Hardtack (Drowned Fortress)", 6, _use_rotten_hardtack_fortress)