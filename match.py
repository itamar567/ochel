import math
import time
import tkinter
from tkinter import ttk, scrolledtext

import classes
import constants
import match_constants
import misc
import pets
import player_values


class DetailWindow:
    def __init__(self, entity):
        self.entity = entity
        self.window = tkinter.Tk()
        self.window.title(entity.name)

        hp_progress_bar_style = ttk.Style(master=self.window)
        hp_progress_bar_style.configure("HP.Horizontal.TProgressbar", troughcolor="black", background="red")

        mp_progress_bar_style = ttk.Style(master=self.window)
        mp_progress_bar_style.configure("MP.Horizontal.TProgressbar", troughcolor="black", background="blue")

        self.hp_progress_bar = ttk.Progressbar(master=self.window, orient="horizontal", mode="determinate", length=constants.HP_MP_METER_LENGTH, maximum=1, style="HP.Horizontal.TProgressbar")
        self.hp_progress_bar.grid(row=0, column=0)
        self.hp_progress_label = tkinter.Label(master=self.window, foreground="red")
        self.hp_progress_label.grid(row=0, column=1)

        self.mp_progress_bar = ttk.Progressbar(master=self.window, orient="horizontal", mode="determinate", length=constants.HP_MP_METER_LENGTH, maximum=1, style="MP.Horizontal.TProgressbar")
        self.mp_progress_bar.grid(row=1)
        self.mp_progress_label = tkinter.Label(master=self.window, foreground="blue")
        self.mp_progress_label.grid(row=1, column=1)

        self.details_label = tkinter.Label(master=self.window, justify="left")
        self.details_label.grid(row=2)

        self.update()

    def update(self):
        self.hp_progress_bar["value"] = (self.entity.hp / self.entity.max_hp)
        self.hp_progress_label["text"] = f"{self.entity.hp} / {self.entity.max_hp} (~{math.ceil((self.entity.hp / self.entity.max_hp) * 100)}%)"
        self.mp_progress_bar["value"] = (self.entity.mp / self.entity.max_mp)
        self.mp_progress_label["text"] = f"{self.entity.mp} / {self.entity.max_mp} (~{math.ceil((self.entity.mp / self.entity.max_mp) * 100)}%)"
        self.details_label["text"] = self.entity.get_details()


class Match:
    def __init__(self):
        # Buttons
        self.buttons = {}
        self.pet_buttons = {}
        self.food_buttons = {}

        # Setup enemies and player
        self.window = tkinter.Tk()
        self.player_disabled_skills = False  # If True, all player skills (except rollback) will be disabled
        self.player = self.choose_armor()
        self.enemies = self.choose_enemies()
        self.enemies_alive = self.enemies.copy()
        self.targeted_enemy = self.enemies_alive[0]
        self.entities = self.enemies.copy()
        self.entities.append(self.player)
        for entity in self.entities:
            entity.match = self
        self.current_turn = 1

        # We need to keep a reference to the HP&MP button images, so they won't get garbage-collected by python
        self.hp_button_img = tkinter.PhotoImage(file="images/hp.png")
        self.mp_button_img = tkinter.PhotoImage(file="images/mp.png")
        self.skip_button_image = tkinter.PhotoImage(file="images/skip.png")

        # Setup main window and pet
        self.pet = pets.PetKidDragon(player_values.pet_dragon_name, self.player, classes.PetStats(player_values.pet_stats))
        self.setup_window_pet()
        self.softclear_window()
        self.setup_window_player()

        # Setup food window
        self.food_by_name = {}
        self.food_window = tkinter.Tk()
        self.food_window.title("Food")
        self.setup_window_food()

        # Setup log windows
        self.log_window = tkinter.Tk()
        self.log_window.title("Log")
        self.main_log_widget = tkinter.scrolledtext.ScrolledText(master=self.log_window)

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
        self.main_log_widget.tag_config("p_attacked", foreground="red")
        self.main_log_widget.tag_config("p_attacked_crit", foreground="red")
        self.main_log_widget.tag_config("p_attacked_glance", foreground="red")
        self.main_log_widget.tag_config("p_attacked_crit_glance", foreground="red")
        self.main_log_widget.tag_config("e_attacked", foreground="cyan")
        self.main_log_widget.tag_config("e_attacked_crit", foreground="cyan")
        self.main_log_widget.tag_config("e_attacked_glance", foreground="cyan")
        self.main_log_widget.tag_config("e_attacked_crit_glance", foreground="cyan")
        self.main_log_widget.tag_config("default", foreground="black")

        self.main_log_widget.configure(state="disabled")
        self.main_log_widget.pack()
        self.rotation_log_widget = tkinter.scrolledtext.ScrolledText(master=self.log_window)
        self.rotation_log_widget.configure(state="disabled")
        self.rotation_log_widget.pack()

        # Setup the window for choosing a targeted enemy
        self.choose_targeted_enemy_window = None
        if len(self.enemies) > 1:
            self.name_to_enemies_index = {self.enemies[i].name: i for i in range(len(self.enemies))}
            self.choose_targeted_enemy_window = tkinter.Tk()
            self.choose_targeted_enemy_buttons = []
            self.setup_choose_targeted_enemy_window()
            self.choose_targeted_enemy_buttons[0]["state"] = "disabled"

        # Setup builds window
        if len(player_values.gear_builds) > 0:
            self.gear_builds_window = tkinter.Tk()
            self.gear_builds_window.title("Builds")
            self.gear_builds_buttons = []
            for i in range(len(player_values.gear_builds)):
                button = tkinter.Button(master=self.gear_builds_window, text=f"Build {i + 1}")
                button.bind("<Button-1>", self.switch_to_gear_build_button_onclick)
                button.grid(column=0, row=i)
                self.gear_builds_buttons.append(button)

        # Setup entities windows
        self.entities_windows = []
        for entity in self.entities:
            self.entities_windows.append(DetailWindow(entity))
        self.update_player_skill_buttons()

        while True:
            self.window.update()
            for window in self.entities_windows:
                window.update()
            self.log_window.update()
            self.gear_builds_window.update()
            self.food_window.update()
            if self.player.extra_window is not None:
                self.player.extra_window.update()
            if self.choose_targeted_enemy_window is not None:
                self.choose_targeted_enemy_window.update()
            time.sleep(0.01)

    def switch_targeted_enemy_onclick(self, event):
        if event.widget["state"] == "disabled":
            return
        self.switch_targeted_enemy(event.widget)

    def switch_targeted_enemy(self, button, update_log=True):
        enemy_index = self.name_to_enemies_index[button["text"]]
        self.targeted_enemy = self.enemies[enemy_index]
        for btn in self.choose_targeted_enemy_buttons:
            btn["state"] = "normal"
        button["state"] = "disabled"
        self.update_rotation_log(f"Target {self.enemies[enemy_index].name}", double_turn=True)

    def setup_choose_targeted_enemy_window(self):
        """
        Setups the window for choosing a targeted enemy
        """

        for i in range(len(self.enemies)):
            button = tkinter.Button(master=self.choose_targeted_enemy_window, text=self.enemies[i].name)
            button.bind("<Button-1>", self.switch_targeted_enemy_onclick)
            self.choose_targeted_enemy_buttons.append(button)
            button.pack()

    def switch_to_gear_build_button_onclick(self, event):
        """
        Switches to a gear build based on a button click event

        :param event: The button click event
        """

        if event.widget["state"] == "disabled":
            return
        build_index = int(event.widget["text"].split(" ")[1]) - 1
        self.switch_to_gear_build(build_index)

    def switch_to_gear_build(self, build_index):
        """
        Switches to a gear build based on a build index

        :param build_index: The index of the build to switch to (starts at 0)
        """

        for slot in player_values.gear_builds[build_index].keys():
            self.player.equip(slot, player_values.gear_builds[build_index][slot])
        self.update_main_log(f"{self.player.name} switched to build {build_index + 1}", "p_comment")
        self.update_rotation_log(f"Switch to build {build_index + 1}", double_turn=True)

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
            widget.grid_remove()

    def choose_armor(self):
        """
        Prompts the user to choose an armor from match_constants.PLAYER_ARMOR_LIST.

        :return: An instance of the chosen armor class, using values from player_values
        """

        button_list = []
        armor_index = None

        def button_clicked(event):
            nonlocal armor_index
            for btn in button_list:
                if btn[0] == event.widget:
                    armor_index = btn[1]

        self.window.title("Choose Armor:")

        for i in range(len(match_constants.PLAYER_ARMOR_LIST)):
            button = tkinter.Button(master=self.window, text=match_constants.PLAYER_ARMOR_LIST[i][0])
            button.bind("<Button-1>", button_clicked)
            button_list.append((button, i))
            button.grid(row=0, column=i, padx=5, pady=5)

        while armor_index is None:
            self.window.update()
            time.sleep(0.01)

        self.clear_window()
        return match_constants.PLAYER_ARMOR_LIST[armor_index][1](player_values.name, classes.MainStats(player_values.stats), level=player_values.level, gear=player_values.gear_builds[0])

    def choose_enemies(self):
        """
        Prompts the user to choose the enemies from match_constants.ENEMIES_LIST.

        :return: A list of enemy instances based on the chosen enemy classes, using the player level from player_values.
        """

        button_list = []
        enemy_index = None

        def button_clicked(event):
            nonlocal enemy_index
            for btn in button_list:
                if btn[0] == event.widget:
                    enemy_index = btn[1]

        self.window.title("Choose Enemy:")

        for i in range(len(match_constants.ENEMIES_LIST)):
            button = tkinter.Button(master=self.window, text=match_constants.ENEMIES_LIST[i][0])
            button.bind("<Button-1>", button_clicked)
            button_list.append((button, i))
            button.grid(row=0, column=i, padx=5, pady=5)

        while enemy_index is None:
            self.window.update()
            time.sleep(0.01)

        enemies_list = []
        for enemy in match_constants.ENEMIES_LIST[enemy_index][1]:
            enemies_list.append(enemy(level=player_values.level))

        self.clear_window()
        return enemies_list

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

    def update_player_cooldowns(self, reduce_cooldowns=True):
        """
        Updates the player buttons based on their cooldown.

        :param reduce_cooldowns: If True, will reduce all player skill cooldowns by 1
        """
        to_pop = []
        for skill in self.player.active_cooldowns.keys():
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
        food = self.food_by_name[event.widget["text"]]
        self.player.add_effect(misc.Effect("Stuffed", "food_stuffed", food.stuffed_duration, {}, {}))
        food.use_function(self)
        self.disable_food_buttons()
        self.update_rotation_log(food.name, double_turn=True)
        self.update_detail_windows()

    def setup_window_food(self):
        """
        Setups the food window.
        """

        for food in player_values.food_list:
            self.food_by_name[food.name] = food
            button = tkinter.Button(master=self.food_window, text=food.name)
            button.bind("<Button-1>", self.use_food_button_onclick)
            button.pack()
            self.food_buttons[food.name] = button

    def disable_food_buttons(self):
        """
        Disables the food buttons.
        """

        for button in self.food_buttons.values():
            button["state"] = "disabled"

    def enable_food_buttons(self):
        """
        Enables the food buttons.
        """

        for button in self.food_buttons.values():
            button["state"] = "normal"

    def disable_build_buttons(self):
        """
        Disables the switch gear build buttons.
        """

        for button in self.gear_builds_buttons:
            button["state"] = "disabled"

    def enable_build_buttons(self):
        """
        Enables the switch gear build buttons.
        """

        for button in self.gear_builds_buttons:
            button["state"] = "normal"

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
                        or self.player.gear[constants.SLOT_TRINKET].abillity is None:
                    continue
                button_img = self.player.gear[constants.SLOT_TRINKET].abillity[0]
            else:
                button_img = self.player.skill_images[constants.KEYBOARD_CONTROLS[i]]
            button = tkinter.Label(master=self.window, image=button_img, compound=tkinter.TOP)
            button.skill = constants.KEYBOARD_CONTROLS[i]
            button.bind("<Button-1>", self.player.use_skill_button_onclick)
            button.grid(row=0, column=i)
            self.buttons[constants.KEYBOARD_CONTROLS[i]] = (button, button.grid_info())

        button = tkinter.Button(master=self.window, text="Back")
        button.bind("<Button-1>", self.rollback)
        button.grid(row=0, column=len(constants.KEYBOARD_CONTROLS), padx=5, pady=5)
        self.buttons["Back"] = (button, button.grid_info())
        self.buttons["Back"][0]["state"] = "disabled"

        button = tkinter.Button(master=self.window, text="Export")
        button.bind("<Button-1>", self.export_onclick)
        button.grid(row=0, column=len(constants.KEYBOARD_CONTROLS) + 1, padx=5, pady=5)
        self.buttons["Export"] = (button, button.grid_info())

    def show_window_player(self):
        """
        Shows the player window widgets after they were removed.
        Also enables the food buttons if the player doesn't have a 'Stuffed' effect.
        """

        self.window.title("Choose Skill:")

        for button in self.buttons.values():
            button[0].grid(**button[1])

        self.enable_build_buttons()
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
            return

        for skill in self.player.mana_cost.keys():
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
        self.disable_build_buttons()
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
        self.buttons["Back"][0]["state"] = "normal"
        self.show_window_player()
        self.update_player_skill_buttons()
        # player.next() Handles DoTs and armor-specific mechanics
        if self.player.next() == constants.PLAYER_STUNNED_STR:
            self.update_main_log(f"{self.player.name} is immobilized", "p_comment")
        for entity in self.entities:
            entity.update_rollback_data()
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
        self.choose_targeted_enemy_buttons[self.name_to_enemies_index[entity.name]]["state"] = "disabled"

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

        if self.buttons["Back"][0]["state"] == "disabled":
            return
        self.player_disabled_skills = False
        self.current_turn -= 1
        for entity in self.entities:
            entity.rollback()
        self.pet.rollback()

        self.update_player_cooldowns(reduce_cooldowns=False)
        self.update_pet_cooldowns(reduce_cooldowns=False)
        self.update_player_skill_buttons()
        self.update_pet_skill_buttons()
        self.update_detail_windows()
        if self.current_turn == 1:
            self.buttons["Back"][0]["state"] = "disabled"

        log = self.rotation_log_widget.get("1.0", "end")
        log = " -> ".join(log.split(" -> ")[:-2]) + " -> "
        if log == " -> ":
            log = ""
        self.rotation_log_widget.configure(state="normal")
        self.rotation_log_widget.delete("1.0", "end")
        self.rotation_log_widget.insert("1.0", log)
        self.rotation_log_widget.configure(state="disabled")
        self.rotation_log_widget.see("end")
        self.update_main_log(f"{self.player.name} undoes their last move", "p_comment")

    def export(self):
        text = ""
        stats = classes.MainStats(player_values.stats)
        if stats.__repr__() != "" or (isinstance(self.pet, pets.PetKidDragon) and self.pet.stats.__repr__() != ""):
            text = "== Stats =="
            if self.player.stats.__repr__() != "":
                text += f"\n{stats}"
            if isinstance(self.pet, pets.PetKidDragon) and self.pet.stats.__repr__() != "":
                text += f"\n{self.pet.stats}"
            text += "\n\n"
        text += "== Builds =="
        for index, build in enumerate(player_values.gear_builds):
            text += f"\n- Build {index}"
            for slot in constants.SLOTS:
                if slot in build.keys():
                    text += "\n"
                    if slot == constants.SLOT_WEAPON_SPECIAL:
                        text += "Slotted: "
                    text += build[slot].name
            text += "\n"
        hp_potions_used = 5 - self.player.hp_potion_count
        mp_potions_used = 5 - self.player.mp_potion_count
        text += "\n== Potions / Food =="
        text += f"\n{hp_potions_used}x HP, {mp_potions_used}x MP potion(s) used"
        return text

    def export_onclick(self, event):
        window = tkinter.Tk()
        window.title("Exported match")
        scrolled_text = tkinter.scrolledtext.ScrolledText(master=window)
        scrolled_text.insert("1.0", self.export())
        scrolled_text["state"] = "disabled"
        scrolled_text.pack()
