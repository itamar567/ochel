# OCHEL
OCHEL is a Python program that imitates DragonFable fights and provides an easier and faster way to create boss fights strategies and calculations.

## Installation

### Windows
Download the [latest release](https://github.com/itamar567/ochel/releases/latest) and run the executable.

### Mac and Linux
Make sure you have Python 3 installed.
Click the green Code button above the file list, then click Download ZIP and unzip the downloaded file.
Double-click `main.py` to run the program.

## Features
OCHEL currently supports all game mechanics except for pet switching.

## Classes
Currently implemented classes:

- Technomancer
- Chaosweaver

## Enemies
Currently implemented enemies:

- Dummy (100k HP)
- Oratath

## Gear
All the in-game gear (except trinkets/special weapons/pets) is included and can be equipped from the inventory.

If the gear isn't updated to the latest release, you can always add the gear manually (except trinkets/special weapons/pets) using the inventory after starting a match.
The gear you added will be saved, and you will be able to use it in future matches.

Currently, the only supported pet is the kid dragon.


### Weapon Specials:
Currently implemented weapon specials:

- Dragon Blade
- DragonBlaser
- Escelense Blade
- ZardSlayer Blade
- Light of Destiny
- Spider's Embrace
- Vile Infused Rose Weapons
- Lucky Hammer
- Pandora's Scythe
- Ruby Spike
- Thorn Replica
- Light of Ebil Dread
- Rolith's Backup Hammer
- Destiny Weapons
- Doom Weapons
- Fourth of July Weapons
- Amulet Weapons
- Ancient Frost Moglin Weapons
- Doom Blade of Sorrows
- Blade of Destiny (Level 80)
- Blade of Destiny (Level 90)
- Heart's Whisper
- Ice Scythe
- Blade of Awe
- Frostval Weapons
- The Quadstaff
- Twilly's Staff
- Warlic's Gift
- Aww Weapons
- Creatioux Claw
- Frozen Weapons
- Necrotic Sword of Doom
- Vanilla Ice Katana

### Trinkets:
Currently implemented trinkets:

- The Corrupted Seven
- Elemental Unity Defender XV

## Compiling
OCHEL uses PyInstaller to compile the python files to a windows executable.
To compile the program, run the following command:
`pyinstaller --noconsole --onefile --add-data "resources;resources" main.py`