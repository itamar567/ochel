import json
import math
import os.path
import time
import tkinter
from tkinter import ttk, scrolledtext, font

import classes
import constants
import match_constants
import misc
import pets
import player_values
import food
import utilities
from gear.gear import Gear, Item, Weapon
from gear.trinkets import trinkets


class DetailWindow:
    def __init__(self, entity):
        self.entity = entity
        self.window = tkinter.Toplevel()
        self.window.title(entity.name)

        progress_bars_frame = tkinter.Frame(master=self.window)
        progress_bars_frame.grid(row=0, column=0, sticky=tkinter.W)

        hp_progress_bar_style = ttk.Style(master=progress_bars_frame)
        hp_progress_bar_style.configure("HP.Horizontal.TProgressbar", troughcolor="black", background="red")

        mp_progress_bar_style = ttk.Style(master=progress_bars_frame)
        mp_progress_bar_style.configure("MP.Horizontal.TProgressbar", troughcolor="black", background="blue")

        self.hp_progress_bar = ttk.Progressbar(master=progress_bars_frame, orient="horizontal", mode="determinate", length=constants.HP_MP_METER_LENGTH, maximum=1, style="HP.Horizontal.TProgressbar")
        self.hp_progress_bar.grid(row=0, column=0, padx=5)
        self.hp_progress_label = tkinter.Label(master=progress_bars_frame, foreground="red")
        self.hp_progress_label.grid(row=0, column=1, padx=5, sticky=tkinter.W)

        self.mp_progress_bar = ttk.Progressbar(master=progress_bars_frame, orient="horizontal", mode="determinate", length=constants.HP_MP_METER_LENGTH, maximum=1, style="MP.Horizontal.TProgressbar")
        self.mp_progress_bar.grid(row=1, column=0, padx=5)
        self.mp_progress_label = tkinter.Label(master=progress_bars_frame, foreground="blue")
        self.mp_progress_label.grid(row=1, column=1, padx=5, sticky=tkinter.W)

        self.details_label = tkinter.Label(master=self.window, justify="left")
        self.details_label.grid(row=2, column=0, sticky=tkinter.W)

        self.update()

    def update(self):
        self.hp_progress_bar["value"] = (self.entity.hp / self.entity.max_hp)
        self.hp_progress_label["text"] = f"{self.entity.hp} / {self.entity.max_hp} (~{math.ceil((self.entity.hp / self.entity.max_hp) * 100)}%)"
        self.mp_progress_bar["value"] = (self.entity.mp / self.entity.max_mp)
        self.mp_progress_label["text"] = f"{self.entity.mp} / {self.entity.max_mp} (~{math.ceil((self.entity.mp / self.entity.max_mp) * 100)}%)"
        self.details_label["text"] = self.entity.get_details()


class AddItemWindow:
    def __init__(self, match):
        self.match = match
        self.window = tkinter.Toplevel()
        self.window.title("Choose Item Type")

        self.dmg_type = None
        self.slot = None
        self.name_entry = None
        self.id_entry = None
        self.elem_entry = None
        self.dmg_min_entry = None
        self.dmg_max_entry = None
        self.bonuses_entry = None
        self.resists_entry = None

        for index, slot in enumerate(constants.INVENTORY_SLOTS):
            if slot == constants.SLOT_WEAPON_SPECIAL:
                continue
            button_img = tkinter.PhotoImage(master=self.window, file=utilities.resource_path(
                f"resources/images/inv_icons/{slot}.png"))
            button = tkinter.Button(master=self.window, image=button_img)
            button.img = button_img  # We need to keep a reference to the button image, so it won't get garbage-collected by python
            button.slot = slot
            button.bind("<Button-1>", self.update_window_after_slot_selection)
            button.grid(column=index, row=0)

    def clear_window(self):
        for widget in self.window.children.values():
            widget.grid_remove()

    def update_window_after_slot_selection(self, event):
        self.slot = event.widget.slot
        if self.slot == constants.SLOT_WEAPON:
            self.update_window_to_select_dmg_type()
        else:
            self.update_window_to_insert_item_stats()

    def update_window_to_select_dmg_type(self):
        self.clear_window()
        self.window.title("Choose Damage Type")
        for index, dmg_type in enumerate(constants.DMG_TYPES):
            button = tkinter.Button(master=self.window, text=constants.DMG_TYPE_NAMES[dmg_type])
            button.grid(column=index, row=0)
            button.dmg_type = dmg_type
            button.bind("<Button-1>", self.update_window_to_insert_weapon_stats)

    def update_window_to_insert_item_stats(self):
        self.clear_window()
        self.window.title("Stats")

        # Row 1: name
        name_label = tkinter.Label(master=self.window, text="Item name: ")
        self.name_entry = tkinter.Entry(master=self.window)
        name_label.grid(row=1, column=0)
        self.name_entry.grid(row=1, column=1)

        # Row 2: ID
        id_label = tkinter.Label(master=self.window, text="Item ID: ")
        self.id_entry = tkinter.Entry(master=self.window)
        id_label.grid(row=2, column=0)
        self.id_entry.grid(row=2, column=1)

        # Row 3: Bonuses
        bonuses_label = tkinter.Label(master=self.window, text="Bonuses: ")
        self.bonuses_entry = tkinter.Entry(master=self.window)
        bonuses_label.grid(row=3, column=0)
        self.bonuses_entry.grid(row=3, column=1)

        # Row 4: Resists
        resists_label = tkinter.Label(master=self.window, text="Resistances: ")
        self.resists_entry = tkinter.Entry(master=self.window)
        resists_label.grid(row=4, column=0)
        self.resists_entry.grid(row=4, column=1)

        finish_button = tkinter.Button(master=self.window, text="Add")
        finish_button.bind("<Button-1>", self.add_item)
        finish_button.grid(row=5, column=0)

    def update_window_to_insert_weapon_stats(self, event):
        self.clear_window()
        self.window.title("Stats")
        self.dmg_type = event.widget.dmg_type

        # Row 1: name
        name_label = tkinter.Label(master=self.window, text="Weapon name: ")
        self.name_entry = tkinter.Entry(master=self.window)
        name_label.grid(row=1, column=0)
        self.name_entry.grid(row=1, column=1)

        # Row 2: ID
        id_label = tkinter.Label(master=self.window, text="Weapon ID: ")
        self.id_entry = tkinter.Entry(master=self.window)
        id_label.grid(row=2, column=0)
        self.id_entry.grid(row=2, column=1)

        # Row 3: element
        elem_label = tkinter.Label(master=self.window, text="Weapon Element: ")
        self.elem_entry = tkinter.Entry(master=self.window)
        elem_label.grid(row=3, column=0)
        self.elem_entry.grid(row=3, column=1)

        # Row 4: damage
        dmg_label_1 = tkinter.Label(master=self.window, text="Weapon Damage: ")
        self.dmg_min_entry = tkinter.Entry(master=self.window)
        dmg_label_2 = tkinter.Label(master=self.window, text=" - ")
        self.dmg_max_entry = tkinter.Entry(master=self.window)
        dmg_label_1.grid(row=4, column=0)
        self.dmg_min_entry.grid(row=4, column=1)
        dmg_label_2.grid(row=4, column=2)
        self.dmg_max_entry.grid(row=4, column=3)

        # Row 5: Bonuses
        bonuses_label = tkinter.Label(master=self.window, text="Bonuses: ")
        self.bonuses_entry = tkinter.Entry(master=self.window)
        bonuses_label.grid(row=5, column=0)
        self.bonuses_entry.grid(row=5, column=1)

        # Row 6: Resists
        resists_label = tkinter.Label(master=self.window, text="Resistances: ")
        self.resists_entry = tkinter.Entry(master=self.window)
        resists_label.grid(row=6, column=0)
        self.resists_entry.grid(row=6, column=1)

        finish_button = tkinter.Button(master=self.window, text="Add")
        finish_button.bind("<Button-1>", self.add_item)
        finish_button.grid(row=7, column=0)

    def add_item(self, event):
        name = self.name_entry.get()
        identifier = self.id_entry.get()
        bonuses_str = self.bonuses_entry.get()
        resists_str = self.resists_entry.get()

        bonuses = {}
        if bonuses_str.strip() != "":
            for bonus in bonuses_str.split(", "):
                if bonus.upper() != bonus:  # Not a stat bonus
                    bonus = bonus.lower()  # Non-stat bonuses are lowercase
                bonus = bonus.replace("melee def", "melee_def")
                bonus = bonus.replace("pierce def", "pierce_def")
                bonus = bonus.replace("magic def", "magic_def")
                bonus_name = bonus.split(" ")[0]
                bonus_value = int(bonus.split(" ")[1])
                bonuses[bonus_name] = bonus_value

            bpd = ("block", "parry", "dodge")
            # If all bpd values are the same, use bpd instead of block, parry and dodge
            if all(x in bonuses for x in bpd) and bonuses[bpd[0]] == bonuses[bpd[1]] == bonuses[bpd[2]]:
                value = bonuses[bpd[0]]
                for bonus in bpd:
                    bonuses.pop(bonus)
                bonuses["bpd"] = value

            mpm = ("melee_def", "pierce_def", "magic_def")
            # If all mpm values are the same, use mpm instead of melee_def, pierce_def and magic_def
            if all(x in bonuses for x in mpm) and bonuses[mpm[0]] == bonuses[mpm[1]] == bonuses[mpm[2]]:
                value = bonuses[mpm[0]]
                for bonus in mpm:
                    bonuses.pop(bonus)
                bonuses["mpm"] = value

        resists = {}
        if resists_str.strip() != "":
            for elem in resists_str.split(", "):
                elem = elem.lower()  # All resistances are lowercase
                elem_name = elem.split(" ")[0]
                elem_value = int(elem.split(" ")[1])
                resists[elem_name] = elem_value

        if self.slot != constants.SLOT_WEAPON:
            item = Item(name, identifier, bonuses, resists)
        else:
            element = self.elem_entry.get().lower()
            min_dmg = int(self.dmg_min_entry.get())
            max_dmg = int(self.dmg_max_entry.get())
            item = Weapon(name, identifier, self.dmg_type, element, min_dmg, max_dmg, bonuses, resists)
        Gear.save_item(item, self.slot)
        self.match.update_inv_window_by_slot(self.slot)
        self.window.destroy()


class Match:
    def __init__(self):
        self.is_running = True

        # Buttons
        self.buttons = {}
        self.pet_buttons = {}
        self.food_buttons = {}
        self.extra_buttons_frame = None
        self.extra_buttons = {}

        # Setup window
        self.window = tkinter.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_closed)
        self.style = ttk.Style()
        self.style.theme_use(constants.THEME)
        font.nametofont("TkDefaultFont").configure(family=constants.FONT_FAMILY, size=constants.FONT_SIZE)
        font.nametofont("TkTextFont").configure(family=constants.FONT_FAMILY, size=constants.FONT_SIZE)
        font.nametofont("TkFixedFont").configure(family=constants.FONT_FAMILY, size=constants.FONT_SIZE)

        # Setup enemies and player
        self.player_disabled_skills = False  # If True, all player skills (except rollback) will be disabled
        self.stats, self.pet_stats, self.trinket, self.player, self.enemies = self.choose_match_data()
        if not self.is_running:
            return
        self.enemies_alive = self.enemies.copy()
        self.rollback_enemies_alive = [self.enemies_alive.copy()]
        self.targeted_enemy = self.enemies_alive[0]
        self.rollback_targeted_enemy = [self.targeted_enemy]
        self.entities = self.enemies.copy()
        self.entities.append(self.player)
        self.current_turn = 1
        for entity in self.entities:
            entity.match = self
            entity.setup()

        # We need to keep a reference to the HP, MP, Skip and Trinket button images, so they won't get garbage-collected by python
        self.hp_button_img = tkinter.PhotoImage(file=utilities.resource_path("resources/images/hp.png"))
        self.mp_button_img = tkinter.PhotoImage(file=utilities.resource_path("resources/images/mp.png"))
        self.skip_button_image = tkinter.PhotoImage(file=utilities.resource_path("resources/images/skip.png"))
        self.trinket_img = None

        # Setup inventory window variables
        self.inv_window = None
        self.inv_buttons = {}
        self.inv_build_load_button = None
        self.inv_gear_list = None
        self.inv_search_entry_var = tkinter.StringVar()
        self.inv_search_entry_var.trace_add("write", self.search_inv_on_entry_update)
        self.inv_build_entry_var = tkinter.StringVar()
        self.inv_buttons_disabled = False
        self.current_inv_item_list = Gear.get_gear_list(constants.INVENTORY_SLOTS[0])
        self.current_inv_slot_list = [constants.INVENTORY_SLOTS[0]] * len(self.current_inv_item_list)
        self.items_loaded_in_inv = 0
        self.only_max_lvl_items_variable = tkinter.BooleanVar()
        self.only_max_lvl_items_variable.set(True)
        self.only_max_lvl_items_variable.trace_add("write", self.update_inv_items_on_checkbox_update)

        # Setup food window variables
        self.food_window = None
        self.food_buttons_disabled = False

        # Setup dragon element window variables
        self.pet_dragon_element_window = None

        # Setup main window and pet
        self.pet = pets.PetKidDragon(player_values.pet_dragon_name, self.player, self.pet_stats)
        self.setup_window_pet()
        self.softclear_window()
        self.setup_window_player()

        # Setup log window
        self.log_window = tkinter.Toplevel()
        self.log_window.title("Log")

        self.main_log_widget = tkinter.scrolledtext.ScrolledText(master=self.log_window, state="disabled", width=50, height=25)
        self.main_log_widget.pack()

        self.rotation_log_widget = tkinter.scrolledtext.ScrolledText(master=self.log_window, state="disabled", width=50, height=10)
        self.rotation_log_widget.pack()

        # Log color config
        # if the tag stats with 'p_', the tag is related to the player
        # if the tag stats with 'e_', the tag is related to the enemies
        self.main_log_widget.tag_config("p_heal", foreground="magenta")
        self.main_log_widget.tag_config("e_heal", foreground="magenta")
        self.main_log_widget.tag_config("p_hot", foreground="magenta")
        self.main_log_widget.tag_config("e_hot", foreground="magenta")
        self.main_log_widget.tag_config("p_mana_heal", foreground="blue")
        self.main_log_widget.tag_config("e_mana_heal", foreground="blue")
        self.main_log_widget.tag_config("p_mana_heal_dot", foreground="blue")
        self.main_log_widget.tag_config("e_mana_heal_dot", foreground="blue")
        self.main_log_widget.tag_config("p_mana_attacked", foreground="blue")
        self.main_log_widget.tag_config("e_mana_attacked", foreground="blue")
        self.main_log_widget.tag_config("p_mana_dot", foreground="blue")
        self.main_log_widget.tag_config("e_mana_dot", foreground="blue")
        self.main_log_widget.tag_config("p_dot", foreground="yellow")
        self.main_log_widget.tag_config("e_dot", foreground="yellow")
        self.main_log_widget.tag_config("p_comment", foreground="green")
        self.main_log_widget.tag_config("e_comment", foreground="green")
        self.main_log_widget.tag_config("pet_comment", foreground="green")
        self.main_log_widget.tag_config("p_attacked", foreground="red")
        self.main_log_widget.tag_config("p_attacked_crit", foreground="red")
        self.main_log_widget.tag_config("p_attacked_glance", foreground="red")
        self.main_log_widget.tag_config("p_attacked_crit_glance", foreground="red")
        self.main_log_widget.tag_config("e_attacked", foreground="cyan")
        self.main_log_widget.tag_config("e_attacked_crit", foreground="cyan")
        self.main_log_widget.tag_config("e_attacked_glance", foreground="cyan")
        self.main_log_widget.tag_config("e_attacked_crit_glance", foreground="cyan")
        self.main_log_widget.tag_config("default", foreground="black")

        # Setup the window for choosing a targeted enemy
        self.choose_targeted_enemy_window = None
        if len(self.enemies) > 1:
            self.name_to_enemies_index = {self.enemies[i].name: i for i in range(len(self.enemies))}
            self.choose_targeted_enemy_window = tkinter.Toplevel()
            self.choose_targeted_enemy_buttons = []
            self.setup_choose_targeted_enemy_window()
            self.update_targeted_enemy_buttons()

        # Setup entities windows
        self.entities_windows = []
        for entity in self.entities:
            self.entities_windows.append(DetailWindow(entity))
        self.update_player_skill_buttons()

        self.on_hit_data = {}  # Data for on-hit specials
        self.rollback_on_hit_data = [self.on_hit_data.copy()]

        self.window_list = [self.window, self.log_window]
        for detail_window in self.entities_windows:
            self.window_list.append(detail_window.window)
        if self.player.extra_window is not None:
            self.window_list.append(self.player.extra_window)
        if self.choose_targeted_enemy_window is not None:
            self.window_list.append(self.choose_targeted_enemy_window)

        for window in self.window_list:
            window.protocol("WM_DELETE_WINDOW", self.on_window_closed)
        # Mainloop
        while self.is_running:
            for window in self.window_list:
                window.update()
            time.sleep(player_values.REFRESH_RATE)

    def on_window_closed(self):
        self.is_running = False

    def choose_match_data(self):
        self.softclear_window()
        self.window.title("Insert Stats")
        player_stats = None
        pet_stats = None
        trinket = None
        armor = None
        enemies = []
        data_dir_path = f"{Gear.path}/data"
        autofill_file_path = f"{data_dir_path}/autofill.json"

        def button_clicked(event):
            nonlocal player_stats
            nonlocal pet_stats
            nonlocal trinket
            nonlocal armor
            nonlocal enemies
            nonlocal finished

            finished = True

            player_stats_list = [int(stat_entry.get()) for stat_entry in player_stats_entries]
            player_stats = classes.MainStats(player_stats_list)

            pet_stats_list = [int(stat_entry.get()) for stat_entry in pet_stats_entries]
            pet_stats = classes.PetStats(pet_stats_list)

            trinket = trinkets[trinket_id_var.get()]

            player_gear = Gear.get_build(player_values.default_build_id)
            player_gear[constants.SLOT_TRINKET] = trinket
            armor_index = armor_index_var.get()
            armor = match_constants.PLAYER_ARMOR_LIST[armor_index][1](player_values.name, player_stats.copy(), level=player_values.level, gear=player_gear)

            challenge_index = challenge_index_var.get()
            for enemy in match_constants.ENEMIES_LIST[challenge_index][1]:
                enemies.append(enemy(level=player_values.level))

            # Save data for autofill
            autofill_dict = {"player": player_stats_list, "pet": pet_stats_list, "trinket": trinket.identifier, "armor": armor_index, "enemies": challenge_index}
            if not os.path.exists(data_dir_path):
                os.mkdir(data_dir_path)
            json.dump(autofill_dict, open(autofill_file_path, "w"))

        if os.path.exists(autofill_file_path):
            saved_autofill_dict = json.load(open(autofill_file_path, "r"))
            saved_player_stats_list = saved_autofill_dict["player"]
            saved_pet_stats_list = saved_autofill_dict["pet"]
            saved_trinket_id = saved_autofill_dict["trinket"]
            saved_armor_index = saved_autofill_dict["armor"]
            saved_enemies_index = saved_autofill_dict["enemies"]
        else:
            saved_player_stats_list = [0] * 7
            saved_pet_stats_list = [0] * 5
            saved_trinket_id = "empty_trinket"
            saved_armor_index = 0
            saved_enemies_index = 0

        # Stats
        stats_frame = tkinter.Frame(self.window)
        stats_frame.grid(row=0, column=0, sticky=tkinter.W)
        current_row_index = 0

        player_stats_label = tkinter.Label(master=stats_frame, text="Player stats:")
        player_stats_label.grid(row=current_row_index, column=0, sticky=tkinter.W)
        current_row_index += 1
        player_stats_entries = []

        for index, stat in enumerate(("STR", "DEX", "INT", "CHA", "LUK", "END", "WIS")):
            current_stat_label = tkinter.Label(master=stats_frame, text=f"{stat}:")
            current_stat_label.grid(row=current_row_index, column=0, padx=5, sticky=tkinter.W)
            current_stat_entry = tkinter.Entry(master=stats_frame)
            current_stat_entry.insert("end", str(saved_player_stats_list[index]))
            current_stat_entry.grid(row=current_row_index, column=1, padx=5)
            player_stats_entries.append(current_stat_entry)
            current_row_index += 1

        # Newline
        tkinter.Label(master=stats_frame).grid(row=current_row_index, column=0)
        current_row_index += 1

        pet_stats_label = tkinter.Label(master=stats_frame, text="Pet stats:")
        pet_stats_label.grid(row=current_row_index, column=0, sticky=tkinter.W)
        current_row_index += 1
        pet_stats_entries = []

        for index, stat in enumerate(("protection", "magic", "fighting", "assistance", "mischief")):
            current_stat_label = tkinter.Label(master=stats_frame, text=f"{stat}:")
            current_stat_label.grid(row=current_row_index, column=0, padx=5, sticky=tkinter.W)
            current_stat_entry = tkinter.Entry(master=stats_frame)
            current_stat_entry.insert("end", str(saved_pet_stats_list[index]))
            current_stat_entry.grid(row=current_row_index, column=1, padx=5)
            pet_stats_entries.append(current_stat_entry)
            current_row_index += 1

        # Newline
        tkinter.Label(master=stats_frame).grid(row=current_row_index, column=0)

        # Trinkets
        trinkets_frame = tkinter.Frame(master=self.window)
        trinkets_frame.grid(row=1, column=0)
        trinket_id_var = tkinter.StringVar(master=trinkets_frame, value=saved_trinket_id)

        trinkets_label = tkinter.Label(master=trinkets_frame, text="Trinket:")
        trinkets_label.grid(row=0, column=0, sticky=tkinter.W)

        for index, trinket in enumerate(trinkets.values()):
            button = tkinter.Radiobutton(master=trinkets_frame, text=trinket.name, variable=trinket_id_var, value=trinket.identifier, indicatoron=False)
            button.grid(row=1, column=index, padx=5, sticky=tkinter.W)

        # Newline
        tkinter.Label(master=trinkets_frame).grid(row=len(trinkets), column=0)

        # Armors
        armors_frame = tkinter.Frame(master=self.window)
        armors_frame.grid(row=2, column=0, sticky=tkinter.W)
        armor_index_var = tkinter.IntVar(master=armors_frame, value=saved_armor_index)
        armors_label = tkinter.Label(master=armors_frame, text="Armor:")
        armors_label.grid(row=0, column=0, sticky=tkinter.W)

        for i in range(len(match_constants.PLAYER_ARMOR_LIST)):
            button = tkinter.Radiobutton(master=armors_frame, text=match_constants.PLAYER_ARMOR_LIST[i][0], variable=armor_index_var, value=i, indicatoron=False)
            button.grid(row=1, column=i, padx=5, sticky=tkinter.W)

        # Newline
        tkinter.Label(master=armors_frame).grid(row=len(match_constants.PLAYER_ARMOR_LIST), column=0)

        # Enemies
        challenges_frame = tkinter.Frame(master=self.window)
        challenges_frame.grid(row=3, column=0, sticky=tkinter.W)
        challenge_index_var = tkinter.IntVar(master=challenges_frame, value=saved_enemies_index)
        challenges_label = tkinter.Label(master=challenges_frame, text="Challenge:")
        challenges_label.grid(row=0, column=0, sticky=tkinter.W)

        for i in range(len(match_constants.ENEMIES_LIST)):
            button = tkinter.Radiobutton(master=challenges_frame, text=match_constants.ENEMIES_LIST[i][0], variable=challenge_index_var, value=i, indicatoron=False)
            button.grid(row=1, column=i, padx=5, sticky=tkinter.W)

        # Newline
        tkinter.Label(master=challenges_frame).grid(row=len(match_constants.ENEMIES_LIST), column=0)

        # Finish button
        finish_button = tkinter.Button(master=self.window, text="Finish")
        finish_button.bind("<Button-1>", button_clicked)
        finish_button.grid(row=4, column=0)

        finished = False

        while not finished and self.is_running:
            self.window.update()
            time.sleep(player_values.REFRESH_RATE)

        # If the user closed the window, we will return the empty values and exit __init__ afterwards
        if self.is_running:
            self.clear_window()
        return player_stats, pet_stats, trinket, armor, enemies

    def equip_item_onclick(self, event):
        if event.widget["state"] == "disabled":
            return
        if event.widget.equipped:
            self.player.unequip(event.widget.slot)
            event.widget.equipped = False
            event.widget["text"] = "Equip"
        else:
            old_item = self.player.gear.get(event.widget.slot, None)
            if old_item is not None:
                old_item_button = self.inv_buttons.get(old_item.identifier, None)
                if old_item_button is not None:
                    old_item_button["text"] = "Equip"
                    old_item_button.equipped = False

            self.player.equip(event.widget.slot, event.widget.item)
            event.widget.equipped = True
            event.widget["text"] = "Unequip"

    def search_inv(self):
        text = self.inv_search_entry_var.get().lower()
        only_equipped = False
        if ">equip" in text:
            only_equipped = True
            text = text.replace(">equip ", "").replace(">equip", "")
        item_list = []
        slot_list = []
        for slot in constants.INVENTORY_SLOTS:
            if only_equipped:
                if slot in self.player.gear.keys():
                    gear_list = [self.player.gear[slot]]
                else:
                    gear_list = []
            else:
                gear_list = Gear.get_gear_list(slot)
            for item in gear_list:
                if text in item.name.lower():
                    item_list.append(item)
                    slot_list.append(slot)
        self.update_inv_window_by_item_list(item_list, slot_list)

    def search_inv_on_entry_update(self, var, index, mode):
        self.search_inv()

    def update_inv_items_on_checkbox_update(self, var, index, mode):
        Gear.only_max_lvl_items = self.only_max_lvl_items_variable.get()
        self.search_inv()

    def setup_inv_window(self):
        self.inv_window.title("Inventory")
        upper_frame = tkinter.Frame(master=self.inv_window)
        upper_frame.pack(side=tkinter.TOP)
        self.inv_gear_list = tkinter.scrolledtext.ScrolledText(master=upper_frame, width=50, height=20, cursor="left_ptr")
        self.inv_gear_list.pack(side=tkinter.TOP)

        # Disable text selection
        self.inv_gear_list.bind("<ButtonPress-1>", lambda event: "break")
        self.inv_gear_list.bind("<Motion>", lambda event: "break")

        self.update_inv_window_by_item_list(self.current_inv_item_list, self.current_inv_slot_list)
        for slot in constants.INVENTORY_SLOTS:
            button_img = tkinter.PhotoImage(master=upper_frame, file=utilities.resource_path(f"resources/images/inv_icons/{slot}.png"))
            button = tkinter.Button(master=upper_frame, image=button_img)
            button.img = button_img  # We need to keep a reference to the button image, so it won't get garbage-collected by python
            button.slot = slot
            button.bind("<Button-1>", self.update_inv_window_onclick)
            button.pack(side=tkinter.LEFT)
        add_item_button = tkinter.Button(master=upper_frame, text="+")
        add_item_button.bind("<Button-1>", self.add_item_onclick)
        add_item_button.pack(side=tkinter.LEFT)
        only_max_lvl_items_checkbox = tkinter.Checkbutton(master=upper_frame, text="Max Level Only", variable=self.only_max_lvl_items_variable)
        only_max_lvl_items_checkbox.pack(side=tkinter.RIGHT)

        lower_frame = tkinter.Frame(master=self.inv_window)
        lower_frame.pack(side=tkinter.BOTTOM, anchor=tkinter.W)

        # Search
        search_label = tkinter.Label(master=lower_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=1, sticky=tkinter.W)
        search_entry = tkinter.Entry(master=lower_frame, textvariable=self.inv_search_entry_var)
        search_entry.grid(row=0, column=1, padx=5)
        search_entry.bind("<Control-a>", utilities.select_all)

        # Builds
        build_label = tkinter.Label(master=lower_frame, text="Build ID:")
        build_label.grid(row=1, column=0, padx=1, sticky=tkinter.W)
        inv_build_entry = tkinter.Entry(master=lower_frame, textvariable=self.inv_build_entry_var)
        inv_build_entry.grid(row=1, column=1, padx=5)
        inv_build_entry.bind("<Control-a>", utilities.select_all)

        build_save_button = tkinter.Button(master=lower_frame, text="Save")
        build_save_button.bind("<Button-1>", self.save_build_onclick)
        build_save_button.grid(row=1, column=2, padx=5)

        self.inv_build_load_button = tkinter.Button(master=lower_frame, text="Load")
        self.inv_build_load_button.bind("<Button-1>", self.load_build_onclick)
        self.inv_build_load_button.grid(row=1, column=3, padx=5)

        build_show_button = tkinter.Button(master=lower_frame, text="Show")
        build_show_button.bind("<Button-1>", self.show_build_onclick)
        build_show_button.grid(row=1, column=4, padx=5)

    def save_build_onclick(self, event):
        build = {}
        for slot in self.player.gear.keys():
            if slot not in constants.INVENTORY_SLOTS or self.player.gear[slot].default is True:
                continue
            build[slot] = self.player.gear[slot].identifier

        Gear.save_build(build, self.inv_build_entry_var.get())

    def load_build_onclick(self, event):
        if event.widget["state"] == "disabled":
            return
        build_id = self.inv_build_entry_var.get()
        self.player.builds_used.append(build_id)
        build = Gear.get_build(build_id)
        for slot in build.keys():
            self.player.equip(slot, build[slot])
        self.refresh_inv_window()
        self.update_main_log(f"{self.player.name} switched to build {build_id}", "p_comment")
        self.update_rotation_log(f"Switch to build {build_id}", double_turn=True)

    def show_build_onclick(self, event):
        build = Gear.get_build(self.inv_build_entry_var.get())
        item_list = []
        slot_list = []
        for slot in build.keys():
            slot_list.append(slot)
            item_list.append(build[slot])
        self.update_inv_window_by_item_list(item_list, slot_list)

    def refresh_inv_window(self):
        if self.inv_window is None:
            return

        self.update_inv_window_by_item_list(self.current_inv_item_list, self.current_inv_slot_list)

    def update_inv_window_by_slot(self, slot):
        if self.inv_window is None:
            return

        item_list = Gear.get_gear_list(slot)
        self.update_inv_window_by_item_list(item_list, [slot] * len(item_list))

    def inv_load_more_items(self, event):
        # Remove the button from the scrolled text widget
        self.inv_gear_list["state"] = "normal"
        self.inv_gear_list.delete("end-2c", "end")
        self.inv_gear_list.insert("end", "\n")
        self.inv_gear_list["state"] = "disabled"

        self.update_inv_window_by_item_list(self.current_inv_item_list, self.current_inv_slot_list, item_limit=self.items_loaded_in_inv + constants.DEFAULT_INV_ITEM_LIMIT, items_already_loaded=self.items_loaded_in_inv, delete_old_items=False)

    def update_inv_window_by_item_list(self, item_list, slot_list, item_limit=constants.DEFAULT_INV_ITEM_LIMIT, items_already_loaded=0, delete_old_items=True):
        """
        Updates the inventory window using an item list and a slot list
        :param item_list: The list of items to show
        :param slot_list: A list of slots, slot_list[i] = slot of item_list[i]
        :param item_limit: A limit on how many items to display, defaults to constants.DEFAULT_INV_ITEM_LIMIT
        :param items_already_loaded: How many items are already loaded. Used for updating the item limit, defaults to 0
        :param delete_old_items: Whether to delete items that were previously loaded or not.
        """

        if self.inv_window is None:
            return

        self.current_inv_item_list = item_list
        self.current_inv_slot_list = slot_list
        self.items_loaded_in_inv = min(len(item_list), item_limit)
        self.inv_gear_list.configure(state="normal")
        if delete_old_items:
            self.inv_gear_list.delete("1.0", "end")
            self.inv_buttons = {}
        for index in range(items_already_loaded, self.items_loaded_in_inv):
            if item_list[index].identifier in self.player.gear_identifiers:
                text = "Unequip"
                equipped = True
            else:
                text = "Equip"
                equipped = False
            button = tkinter.Button(master=self.inv_gear_list, text=text)
            button.slot = slot_list[index]
            button.item = item_list[index]
            button.equipped = equipped
            button.bind("<Button-1>", self.equip_item_onclick)
            if self.inv_buttons_disabled:
                button["state"] = "disabled"
            self.inv_buttons[item_list[index].identifier] = button
            self.inv_gear_list.insert("end", f"{item_list[index].name} ")
            self.inv_gear_list.window_create("end", window=button)
            if index + 1 < self.items_loaded_in_inv:
                self.inv_gear_list.insert("end", "\n")

        if len(item_list) > item_limit:
            self.inv_gear_list.insert("end", "\n")
            load_more_items_button = tkinter.Button(master=self.inv_gear_list, text="Load More...")
            load_more_items_button.bind("<Button-1>", self.inv_load_more_items)
            self.inv_gear_list.window_create("end", window=load_more_items_button)

        self.inv_gear_list.configure(state="disabled")

    def update_inv_window_onclick(self, event):
        self.update_inv_window_by_slot(event.widget.slot)

    def add_item_onclick(self, event):
        AddItemWindow(self)

    def disable_inventory_buttons(self):
        self.inv_buttons_disabled = True
        if self.inv_window is None:
            return
        for button in self.inv_buttons.values():
            button["state"] = "disabled"
        self.inv_build_load_button["state"] = "disabled"

    def enable_inventory_buttons(self):
        self.inv_buttons_disabled = False
        if self.inv_window is None:
            return
        for button in self.inv_buttons.values():
            button["state"] = "normal"
        self.inv_build_load_button["state"] = "normal"

    def switch_targeted_enemy_onclick(self, event):
        if event.widget["state"] == "disabled":
            return
        self.switch_targeted_enemy(event.widget)

    def switch_targeted_enemy(self, button, update_log=True):
        enemy_index = self.name_to_enemies_index[button["text"]]
        self.targeted_enemy = self.enemies[enemy_index]
        self.update_targeted_enemy_buttons()
        self.update_rotation_log(f"Target {self.enemies[enemy_index].name}", double_turn=True)

    def update_targeted_enemy_buttons(self):
        if len(self.enemies) == 1:
            return

        for index, btn in enumerate(self.choose_targeted_enemy_buttons):
            if self.enemies[index].hp == 0:
                btn["state"] = "disabled"
            else:
                btn["state"] = "normal"
            if self.enemies[index] is self.targeted_enemy and self.enemies[index].hp > 0:
                btn["bg"] = "blue"
                btn["fg"] = "white"
            else:
                btn["bg"] = "white"
                btn["fg"] = "black"

    def setup_choose_targeted_enemy_window(self):
        """
        Setups the window for choosing a targeted enemy
        """

        for i in range(len(self.enemies)):
            button = tkinter.Button(master=self.choose_targeted_enemy_window, text=self.enemies[i].name)
            button.bind("<Button-1>", self.switch_targeted_enemy_onclick)
            self.choose_targeted_enemy_buttons.append(button)
            button.pack()

    def update_rotation_log(self, attack_name, double_turn=False, add_to_last_attack=False):
        """
        Updates the rotation logs.

        :param attack_name: Name of the attack
        :param bool double_turn: If True, the next attack will be added to the log using '+' instead of '->'
        :param bool add_to_last_attack: If True, the attack will be added to the log using '+' instead of '->'
        """

        self.rotation_log_widget.configure(state="normal")
        if add_to_last_attack:
            log = self.rotation_log_widget.get("1.0", "end")
            log = " + ".join(log.rsplit(" -> ", 1)[:-1] + [""])
            self.rotation_log_widget.delete("1.0", "end")
            self.rotation_log_widget.insert("end", log)
        if double_turn:
            self.rotation_log_widget.insert("end", f"{attack_name} + ")
        else:
            self.rotation_log_widget.insert("end", f"{attack_name} -> ")
        self.rotation_log_widget.see("end")
        self.rotation_log_widget.configure(state="disabled")

    def update_main_log(self, log, tag="default"):
        """
        Updates the main log

        :param tag: The text tag (e.g. heal, damage, dot), defaults to 'default'. Used to color the text.
        :param log: Text to insert
        """

        self.update_main_log_without_turn_prefix(f"\n[{self.current_turn}] {log}", tag=tag)

    def update_main_log_without_turn_prefix(self, log, tag="default"):
        """
        Updates the main log without a turn prefix and without a newline

        :param tag: The text tag (e.g. heal, damage, dot), defaults to 'default'. Used to color the text.
        :param log: Text to insert
        """

        self.main_log_widget.configure(state="normal")
        self.main_log_widget.insert("end", log, tag)
        self.main_log_widget.see("end")
        self.main_log_widget.configure(state="disabled")

    def clear_window(self):
        """
        Clears the main window, destroying all the widgets in it.
        """

        to_destroy = []
        for widget in self.window.children.values():
            to_destroy.append(widget)
        for widget in to_destroy:
            widget.destroy()

    def softclear_window(self):
        """
        Removes all widgets from the window.
        """

        for widget in self.window.children.values():
            if isinstance(widget, tkinter.Toplevel):
                continue
            widget.grid_remove()

    def update_effects(self):
        """
        Removes effects that expired this turn.
        """

        for entity in self.entities:
            for effect in entity.effects_fade_turn.get(self.current_turn, []).copy():
                entity.remove_effect(effect)
                self.update_main_log(f"{effect.name} fades from {entity.name}", f"{entity.tag_prefix}_comment")
                if effect.identifier == "food_stuffed" and entity is self.player:
                    self.enable_food_buttons()

    def update_player_cooldowns(self, reduce_cooldowns=True, trinket=True):
        """
        Updates the player buttons based on their cooldown.
        :param trinket: Whether to update the trinket cooldown
        :param reduce_cooldowns: If True, will reduce all player skill cooldowns by 1
        """
        to_pop = []
        for skill in self.player.active_cooldowns.keys():
            if not trinket and skill == "B":
                continue
            if self.player.active_cooldowns[skill] == 1 and reduce_cooldowns:
                to_pop.append(skill)
                continue
            if reduce_cooldowns:
                self.player.active_cooldowns[skill] -= 1
            self.buttons[skill][0]["text"] = self.player.active_cooldowns[skill]
            self.buttons[skill][0]["state"] = "disabled"
        for skill in to_pop:
            self.player.active_cooldowns.pop(skill)

    def update_pet_cooldowns(self, reduce_cooldowns=True):
        """
        Updates the pet buttons based on their cooldown.

        :param reduce_cooldowns: If True, will reduce all pet skill cooldowns by 1
        """

        to_pop = []
        for skill in self.pet.active_cooldowns.keys():
            if self.pet.active_cooldowns[skill] == 1 and reduce_cooldowns:
                to_pop.append(skill)
                continue
            if reduce_cooldowns:
                self.pet.active_cooldowns[skill] -= 1
            self.pet_buttons[skill][0]["state"] = "disabled"
            self.pet_buttons[skill][0]["text"] = self.pet.active_cooldowns[skill]
        for skill in to_pop:
            self.pet.active_cooldowns.pop(skill)

    def use_food_button_onclick(self, event):
        """
        Uses food based on a button click event.

        :param event: The button click event
        """

        if event.widget["state"] == "disabled":
            return
        self.player.add_effect(misc.Effect("Stuffed", "food_stuffed", event.widget.food.stuffed_duration, {}, {}))
        event.widget.food.use(self)
        self.player.food_used_list.append(event.widget.food.name)
        utilities.add_value(self.player.food_used_dict, event.widget.food.identifier, 1)
        if event.widget.food.max_uses - self.player.food_used_dict[event.widget.food.identifier] == 0:
            event.widget["state"] = "disabled"
        self.disable_food_buttons()
        self.update_rotation_log(event.widget.food.name, double_turn=True)
        self.update_detail_windows()

    def setup_window_food(self):
        """
        Setups the food window.
        """

        self.food_window.title("Food")

        if self.food_buttons_disabled:
            state = "disabled"
        else:
            state = "normal"

        for current_food in food.food_dict.values():
            button = tkinter.Button(master=self.food_window, text=current_food.name)
            button.food = current_food
            button.bind("<Button-1>", self.use_food_button_onclick)
            button["state"] = state
            button.pack()
            self.food_buttons[current_food.identifier] = button

    def disable_food_buttons(self):
        """
        Disables the food buttons.
        """

        self.food_buttons_disabled = True

        if self.food_window is None:
            return

        for button in self.food_buttons.values():
            button["state"] = "disabled"

    def enable_food_buttons(self):
        """
        Enables the food buttons.
        """

        self.food_buttons_disabled = False

        if self.food_window is None:
            return

        for button in self.food_buttons.values():
            if button.food.max_uses - self.player.food_used_dict.get(button.food.identifier, 0) == 0:
                button["state"] = "disabled"
            else:
                button["state"] = "normal"

    def on_dragon_element_window_closed(self):
        self.pet_dragon_element_window.destroy()
        self.pet_dragon_element_window = None

    def change_dragon_element_onclick(self, event):
        if not isinstance(self.pet, pets.PetKidDragon):
            return
        self.pet.element = event.widget.element
        file = open(pets.PetKidDragon.ELEMENT_FILE_PATH, "w")
        file.write(event.widget.element)
        file.close()
        self.update_main_log(f"{self.pet.name}'s element changed to {event.widget.element}")
        self.update_rotation_log(f"Change dragon element to {event.widget.element}", double_turn=True)

    def open_dragon_element_window_onclick(self, event):
        if self.pet_dragon_element_window is not None:
            return
        self.pet_dragon_element_window = tkinter.Toplevel()
        self.pet_dragon_element_window.protocol("WM_DELETE_WINDOW", self.on_dragon_element_window_closed)
        self.pet_dragon_element_window.title("Dragon Element")
        for index, element in enumerate(constants.DRAGON_ELEMENTS_LIST):
            button = tkinter.Button(master=self.pet_dragon_element_window, text=element)
            button.element = element.lower()
            button.bind("<Button-1>", self.change_dragon_element_onclick)
            button.grid(row=index, column=0)

    def on_inv_window_closed(self):
        self.inv_window.destroy()
        self.inv_window = None

    def open_inv_window_onclick(self, event):
        if self.inv_window is not None:
            return
        self.inv_window = tkinter.Toplevel()
        self.inv_window.protocol("WM_DELETE_WINDOW", self.on_inv_window_closed)
        self.setup_inv_window()

    def on_food_window_closed(self):
        self.food_window.destroy()
        self.food_window = None

    def open_food_window_onclick(self, event):
        if self.food_window is not None:
            return
        self.food_window = tkinter.Toplevel()
        self.food_window.protocol("WM_DELETE_WINDOW", self.on_food_window_closed)
        self.setup_window_food()

    def setup_window_player(self):
        """
        Setups the player window.
        """

        self.window.title("Choose Skill:")

        for i in range(len(constants.KEYBOARD_CONTROLS)):
            if constants.KEYBOARD_CONTROLS[i] == "N":
                button_img = self.hp_button_img
            elif constants.KEYBOARD_CONTROLS[i] == "M":
                button_img = self.mp_button_img
            elif constants.KEYBOARD_CONTROLS[i] == "B":
                if constants.SLOT_TRINKET not in self.player.gear.keys() \
                        or self.player.gear[constants.SLOT_TRINKET].ability_func is None:
                    continue
                button_img = tkinter.PhotoImage(file=utilities.resource_path(self.player.gear[constants.SLOT_TRINKET].ability_img_path), master=self.window)
                self.trinket_img = button_img  # We need to keep a reference to the button image, so it won't get garbage-collected by python
            else:
                button_img = self.player.skill_images[constants.KEYBOARD_CONTROLS[i]]
            button = tkinter.Label(master=self.window, image=button_img, compound=tkinter.TOP)
            button.skill = constants.KEYBOARD_CONTROLS[i]
            button.bind("<Button-1>", self.player.use_skill_button_onclick)
            button.grid(row=0, column=i)
            self.buttons[constants.KEYBOARD_CONTROLS[i]] = (button, button.grid_info())

        self.extra_buttons_frame = tkinter.Frame(master=self.window)
        self.extra_buttons_frame.grid(row=0, column=len(constants.KEYBOARD_CONTROLS))

        back_button = tkinter.Button(master=self.extra_buttons_frame, text="Back")
        back_button.bind("<Button-1>", self.rollback)
        back_button.grid(row=0, column=0, padx=5, pady=2)
        self.extra_buttons["Back"] = (back_button, back_button.grid_info())
        self.extra_buttons["Back"][0]["state"] = "disabled"

        export_button = tkinter.Button(master=self.extra_buttons_frame, text="Export")
        export_button.bind("<Button-1>", self.export_onclick)
        export_button.grid(row=2, column=0, padx=5, pady=2)
        self.extra_buttons["Export"] = (export_button, export_button.grid_info())

        dragon_element_button = tkinter.Button(master=self.extra_buttons_frame, text="Dragon Element")
        dragon_element_button.bind("<Button-1>", self.open_dragon_element_window_onclick)
        dragon_element_button.grid(row=0, column=1, padx=5, pady=2)
        self.extra_buttons["Dragon_Element"] = (dragon_element_button, dragon_element_button.grid_info())

        open_inv_button = tkinter.Button(master=self.extra_buttons_frame, text="Inventory")
        open_inv_button.bind("<Button-1>", self.open_inv_window_onclick)
        open_inv_button.grid(row=1, column=1, padx=5, pady=2)
        self.extra_buttons["Inventory"] = (open_inv_button, open_inv_button.grid_info())

        open_food_window_button = tkinter.Button(master=self.extra_buttons_frame, text="Food")
        open_food_window_button.bind("<Button-1>", self.open_food_window_onclick)
        open_food_window_button.grid(row=2, column=1, padx=5, pady=2)
        self.extra_buttons["Inventory"] = (open_food_window_button, open_food_window_button.grid_info())

    def show_window_player(self):
        """
        Shows the player window widgets after they were removed.
        Also enables the food buttons if the player doesn't have a 'Stuffed' effect.
        """

        self.window.title("Choose Skill:")

        for button in self.buttons.values():
            button[0].grid(**button[1])
        self.extra_buttons_frame.grid(row=0, column=len(self.buttons))
        for extra_button in self.extra_buttons.values():
            extra_button[0].grid(**extra_button[1])

        self.enable_inventory_buttons()
        stuffed = False
        for effect in self.player.effects:
            if effect.identifier == "food_stuffed":
                stuffed = True
        if not stuffed:
            self.enable_food_buttons()

    def setup_window_pet(self):
        """
        Setups the pet window.
        """

        self.window.title("Choose Pet Skill:")

        for i in range(len(constants.KEYBOARD_CONTROLS)):
            if constants.KEYBOARD_CONTROLS[i] == "M":
                button_img = self.skip_button_image
            elif constants.KEYBOARD_CONTROLS[i] not in self.pet.skills:
                continue
            else:
                button_img = self.pet.skill_images[constants.KEYBOARD_CONTROLS[i]]
            button = tkinter.Label(master=self.window, image=button_img, compound=tkinter.TOP)
            button.skill = constants.KEYBOARD_CONTROLS[i]
            button.bind("<Button-1>", self.pet.use_skill)
            button.grid(row=0, column=i)
            self.pet_buttons[constants.KEYBOARD_CONTROLS[i]] = (button, button.grid_info())

        dragon_element_button = tkinter.Button(master=self.window, text="Element")
        dragon_element_button.bind("<Button-1>", self.open_dragon_element_window_onclick)
        dragon_element_button.grid(row=0, column=len(constants.KEYBOARD_CONTROLS), padx=5, pady=5)
        self.pet_buttons["Element"] = (dragon_element_button, dragon_element_button.grid_info())

    def show_window_pet(self):
        """
        Shows the pet window widgets after they were removed.
        """

        self.window.title("Choose Pet Skill:")

        for button in self.pet_buttons.values():
            button[0].grid(**button[1])

    def update_detail_windows(self):
        """
        Updates the detail window for all entities.
        """

        for window in self.entities_windows:
            window.update()

    def update_player_skill_buttons(self):
        """
        Updates the player skill buttons' state based on cooldown/potion count.
        """

        if self.player_disabled_skills:
            for skill in self.player.skills:
                self.buttons[skill][0]["state"] = "disabled"
            if constants.SLOT_TRINKET in self.player.gear and self.player.gear[constants.SLOT_TRINKET].ability_func is not None:
                self.buttons["B"][0]["state"] = "disabled"
            return

        skills = list(self.player.mana_cost.keys())
        if constants.SLOT_TRINKET in self.player.gear and self.player.gear[constants.SLOT_TRINKET].ability_func is not None:
            skills.append("B")

        for skill in skills:
            if not self.player.check_mp_for_skill(skill):
                self.buttons[skill][0]["state"] = "disabled"
            elif skill not in self.player.active_cooldowns.keys():
                self.buttons[skill][0]["state"] = "normal"
                self.buttons[skill][0]["text"] = ""

        if self.player.hp_potion_count <= 0:
            self.buttons["N"][0]["state"] = "disabled"
            self.buttons["N"][0]["text"] = ""
        else:
            self.buttons["N"][0]["state"] = "normal"
            self.buttons["N"][0]["text"] = self.player.hp_potion_count

        if self.player.mp_potion_count <= 0:
            self.buttons["M"][0]["state"] = "disabled"
            self.buttons["M"][0]["text"] = ""
        else:
            self.buttons["M"][0]["state"] = "normal"
            self.buttons["M"][0]["text"] = self.player.mp_potion_count

    def update_pet_skill_buttons(self):
        """
        Updates the pet skill buttons' state based on cooldown.
        """

        for skill in self.pet.skills.keys():
            if skill not in self.pet.active_cooldowns.keys():
                self.pet_buttons[skill][0]["state"] = "normal"
                self.pet_buttons[skill][0]["text"] = ""

    def pet_turn(self):
        """
        Prompts the user to choose a pet skill.

        If the only skill the pet has (except Skip) is Attack, automatically attacks without prompting the user.
        If the user doesn't have a pet equipped/the pet is waking up, automatically skips the pet turn.
        """

        self.update_detail_windows()
        if self.pet is None:
            self.next()
        if self.pet.waking_up:
            self.pet.waking_up = False
            self.next()

        # Check if enemies died on the player turn
        for enemy in self.enemies_alive.copy():
            if enemy.hp == 0:
                self.on_death(enemy)

        self.disable_food_buttons()
        self.disable_inventory_buttons()
        if len(self.pet.skills.keys()) > len(["Attack", "Skip"]):
            self.softclear_window()
            self.update_pet_skill_buttons()
            self.show_window_pet()
        else:
            self.pet.skills[" "][1]()  # use attack skill
            self.next()

    def next(self):
        """
        Do enemies attack and start a new turn
        """

        for enemy in self.enemies_alive.copy():
            if enemy.hp == 0:
                self.on_death(enemy)
                continue
            # Handles DoTs, enemy-specific mechanics and attacks
            if enemy.next() == constants.ENEMY_STUNNED_STR:
                self.update_main_log(f"{enemy.name} is immobilized", "e_comment")

        if self.player.hp == 0:
            self.on_death(self.player)

        # Add newline at the start of each turn
        self.update_main_log_without_turn_prefix("\n")

        # Current turn ended, new turn started
        self.current_turn += 1
        self.update_effects()
        self.update_player_cooldowns()
        self.update_pet_cooldowns()

        self.softclear_window()
        self.extra_buttons["Back"][0]["state"] = "normal"
        self.show_window_player()
        self.update_player_skill_buttons()
        # player.next() Handles DoTs and armor-specific mechanics
        if self.player.next() == constants.PLAYER_STUNNED_STR:
            self.update_main_log(f"{self.player.name} is immobilized", "p_comment")
        for entity in self.entities:
            entity.update_rollback_data()
        self.rollback_on_hit_data.append(self.on_hit_data.copy())
        self.rollback_targeted_enemy.append(self.targeted_enemy)
        self.rollback_enemies_alive.append(self.enemies_alive)
        self.update_targeted_enemy_buttons()
        self.update_detail_windows()

    def end_match(self):
        pass

    def on_death(self, entity):
        if entity == self.player:
            self.player_disabled_skills = True
            self.update_player_skill_buttons()
            return

        self.enemies_alive.remove(entity)
        if len(self.enemies_alive) == 0:
            self.end_match()
            return
        self.switch_targeted_enemy(self.choose_targeted_enemy_buttons[self.name_to_enemies_index[self.enemies_alive[0].name]], update_log=False)

    def update_match_after_double_turn(self):
        """
        Updates the match after a double turn has been made.
        """

        for enemy in self.enemies:
            if enemy.player_double_turn_reaction is not None:
                enemy.player_double_turn_reaction()
        self.update_player_cooldowns()
        self.update_player_skill_buttons()
        self.update_detail_windows()

    def rollback(self, event):
        """
        Rollbacks the match one turn back.

        :param event: Not used for anything, only exists for binding this function to a button.
        """

        if self.extra_buttons["Back"][0]["state"] == "disabled":
            return
        self.player_disabled_skills = False
        self.current_turn -= 1
        for entity in self.entities:
            entity.rollback()
        self.pet.rollback()

        self.on_hit_data = self.rollback_on_hit_data[-2].copy()
        self.rollback_on_hit_data.pop()
        self.targeted_enemy = self.rollback_targeted_enemy[-2]
        self.rollback_targeted_enemy.pop()
        self.enemies_alive = self.rollback_enemies_alive[-2].copy()
        self.rollback_enemies_alive.pop()
        self.update_targeted_enemy_buttons()
        self.update_player_cooldowns(reduce_cooldowns=False)
        self.update_pet_cooldowns(reduce_cooldowns=False)
        self.update_player_skill_buttons()
        self.update_pet_skill_buttons()
        self.update_inv_window_by_item_list(self.current_inv_item_list, self.current_inv_slot_list)
        self.update_detail_windows()
        if self.current_turn == 1:
            self.extra_buttons["Back"][0]["state"] = "disabled"

        log = self.rotation_log_widget.get("1.0", "end")
        log = " -> ".join(log.split(" -> ")[:-2]) + " -> "
        if log == " -> ":
            log = ""
        self.rotation_log_widget.configure(state="normal")
        self.rotation_log_widget.delete("1.0", "end")
        self.rotation_log_widget.insert("1.0", log)
        self.rotation_log_widget.configure(state="disabled")
        self.rotation_log_widget.see("end")
        if utilities.stuffed(self.player):
            self.disable_food_buttons()
        else:
            self.enable_food_buttons()
        self.update_main_log(f"{self.player.name} undoes their last move", "p_comment")

    def export(self):
        text = ""
        if self.stats.__repr__() != "" or (isinstance(self.pet, pets.PetKidDragon) and self.pet.stats.__repr__() != ""):
            text = "== Stats =="
            if self.stats.__repr__() != "":
                text += f"\n{self.stats}"
            if isinstance(self.pet, pets.PetKidDragon) and self.pet.stats.__repr__() != "":
                text += f"\n{self.pet.stats}"
            text += "\n\n"
        text += "== Builds =="
        for build_identifier in self.player.builds_used:
            text += f"\n- {build_identifier}"
            build = Gear.get_build(build_identifier)
            for slot in constants.INVENTORY_SLOTS:
                if slot in build.keys():
                    text += "\n    "
                    if slot == constants.SLOT_WEAPON_SPECIAL:
                        text += f"Slotted: {build[slot].original_name}"
                    else:
                        text += build[slot].name
            text += "\n"
        text += "\n== Gear ==\n"
        for slot in constants.INVENTORY_SLOTS:
            if slot in self.player.gear_used:
                if slot == constants.SLOT_WEAPON_SPECIAL:
                    text += "Slotted: "
                for item in self.player.gear_used[slot]:
                    text += f"{item} / "
                text = text[:-3]
            text += "\n"
        text += "\n== Potions / Food =="
        hp_potions_used = 5 - self.player.hp_potion_count
        mp_potions_used = 5 - self.player.mp_potion_count
        text += f"\nPotions: {hp_potions_used}x HP, {mp_potions_used}x MP"
        if len(self.player.food_used_list) > 0:
            text += f"\nFood:"
            for food_name in self.player.food_used_list:
                text += f" {food_name},"
            text = text[:-1]
        return text

    def export_onclick(self, event):
        window = tkinter.Toplevel()
        window.title("Exported match")
        scrolled_text = tkinter.scrolledtext.ScrolledText(master=window)
        scrolled_text.insert("1.0", self.export())
        scrolled_text["state"] = "disabled"
        scrolled_text.pack()
