import os

import match
from gear.gear import Gear

if not os.path.exists(Gear.path):
    os.mkdir(Gear.path)

game = match.Match()
