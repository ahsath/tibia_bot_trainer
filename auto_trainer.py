import random
import time

import dearpygui.dearpygui as dpg
import pyautogui
import schedule
from pynput.keyboard import Key, Controller

keyboard = Controller()

weapons = { 'Small Stones': 'assets/images/small_stones.png' }

class AutoTrainer:
  def __init__(self):
    self.window = None

    self.focus_area = 'assets/images/focus_area.png'
    self.weapon_slot = 'assets/images/weapon_slot.png'
    self.arrow_keys = ['up', 'right', 'down', 'left']

    self.enable_character_awake_checkbox = dpg.generate_uuid()
    self.enable_auto_equip_checkbox = dpg.generate_uuid()
    self.countdown_text = dpg.generate_uuid()
    self.trainer_status_text = dpg.generate_uuid()
    self.start_btn = dpg.generate_uuid()
    self.stop_btn = dpg.generate_uuid()

    self.next_awake_in_minutes = 1
    self.started = False
    self.enable_character_awake = True
    self.enable_auto_equip = True
    self.start_btn_theme = None
    self.character_awake_job_tag = 'character_awake'
    self.auto_equip_job_tag = 'auto_equip'
    self.selected_weapon = 'Small Stones'
    self.auto_equip_timeout = 10 / 60

    self.define_component()

  def awake_character(self):
    """ Focus the client, if found awakes the character """

    if self.focus_client():
      with pyautogui.hold('command'):
        random.shuffle(self.arrow_keys)
        pyautogui.press(self.arrow_keys)
  
  def equip_weapon(self):
    try:
      weapon_slot_x, weapon_slot_y = pyautogui.locateCenterOnScreen(self.weapon_slot)
      selected_weapon_x, selected_weapon_y = pyautogui.locateCenterOnScreen(weapons[self.selected_weapon])

      pyautogui.moveTo(selected_weapon_x // 2, selected_weapon_y // 2)
      pyautogui.dragTo(weapon_slot_x // 2, weapon_slot_y // 2, button='left')
    except:
      pass

  def focus_client(self):
    """ Search focus area, if found returns True otherwise False is returned """

    try:
      x, y = pyautogui.locateCenterOnScreen(self.focus_area)
      pyautogui.click(x // 2, y // 2)
      return True
    except:
      return False

  def update_countdown(self, seconds: int):
    dpg.configure_item(self.countdown_text, default_value=self.format_countdown(seconds))

  def run_job(self, minutes: int, do, tag: str):
    schedule.every(minutes).minutes.do(do).tag(tag)

  def clear_job(self, tag):
    schedule.clear(tag)
  
  def add_start_btn(self):
    dpg.add_button(label='START', tag=self.start_btn, width=-1, height=32, callback=self.on_start, parent=self.window)
    dpg.bind_item_theme(self.start_btn, self.start_btn_theme)

  def format_countdown(self, seconds):
    return time.strftime("%M:%S", time.gmtime(seconds))

  def heal(self):
    keyboard.press(Key.f1)
    keyboard.release(Key.f1)
  
  def on_start(self):
    if self.enable_character_awake:
      self.awake_character()
      self.run_job(self.next_awake_in_minutes, self.awake_character, self.character_awake_job_tag)

    if self.enable_auto_equip:
      self.equip_weapon()
      self.run_job(self.auto_equip_timeout, self.equip_weapon, self.auto_equip_job_tag)

    dpg.delete_item(self.start_btn)
    dpg.add_button(label='STOP', tag=self.stop_btn, width=-1, height=32, callback=self.on_stop, parent=self.window)
    dpg.configure_item(self.trainer_status_text, default_value='Started', color=(0, 193, 0))

    self.started = True

    self.run_job(3, self.heal, 'auto_heal')
  
  def on_stop(self):
    self.clear_job(None)
    self.update_countdown(self.next_awake_in_minutes * 60)
    dpg.configure_item(self.trainer_status_text, default_value='Stopped', color=(210, 0, 0))
    dpg.delete_item(self.stop_btn)
    self.add_start_btn()
    self.started = False

  def on_enable_character_awake(self, _, enabled: bool):
    self.enable_character_awake = enabled

    if not enabled:
      self.clear_job(self.character_awake_job_tag)
      self.update_countdown(self.next_awake_in_minutes * 60)
    elif self.started and enabled:
      self.run_job(self.next_awake_in_minutes, self.awake_character, self.character_awake_job_tag)

  def on_enable_auto_equip(self, _, enabled):
    self.enable_auto_equip = enabled

    if not enabled:
      self.clear_job(self.auto_equip_job_tag)
    elif self.started and enabled:
      self.equip_weapon()
      self.run_job(self.auto_equip_timeout, self.equip_weapon, self.auto_equip_job_tag)

  def on_minutes_change(self, _, minutes):
    self.clear_job(self.character_awake_job_tag)
    self.next_awake_in_minutes = minutes
    self.update_countdown(minutes * 60)

    if self.started and self.enable_character_awake:
      self.run_job(self.next_awake_in_minutes, self.awake_character, self.character_awake_job_tag)
  
  def on_weapon_change(self, _, weapon):
    self.clear_job(self.auto_equip_job_tag)
    self.selected_weapon = weapon

    if self.started and self.enable_auto_equip:
      self.equip_weapon()
      self.run_job(self.auto_equip_timeout, self.equip_weapon, self.auto_equip_job_tag)
  
  def define_component(self):
    with dpg.window() as window:
      self.window = window
      dpg.set_primary_window(window, True)

      dpg.add_checkbox(
        tag=self.enable_character_awake_checkbox,
        label='Enable Character Awake',
        default_value=self.enable_character_awake, 
        callback=self.on_enable_character_awake,
      )
      dpg.add_input_int(
        label='Minutes',
        default_value=self.next_awake_in_minutes,
        min_value=1,
        max_value=10,
        min_clamped=True,
        max_clamped=True,
        callback=self.on_minutes_change
      )

      dpg.add_separator()

      dpg.add_checkbox(
        tag=self.enable_auto_equip_checkbox,
        label='Enable Auto Equip',
        default_value=self.enable_auto_equip,
        callback=self.on_enable_auto_equip
      )
      dpg.add_combo(
        [weapon for weapon in weapons], 
        label='Weapon', 
        default_value=self.selected_weapon,
        callback=self.on_weapon_change
      )

      dpg.add_separator()

      with dpg.table(
        header_row=False, 
        policy=dpg.mvTable_SizingStretchProp
      ):
        dpg.add_table_column()
        dpg.add_table_column(width_fixed=True)

        with dpg.table_row():
          dpg.add_text('Trainer Status:')
          dpg.add_text('Stopped', tag=self.trainer_status_text, color=(210, 0, 0))
        with dpg.table_row():
          dpg.add_text('Next Character Awake:')
          dpg.add_text(self.format_countdown(self.next_awake_in_minutes * 60), tag=self.countdown_text)

      with dpg.theme() as text_accent:
        with dpg.theme_component(dpg.mvAll):
          dpg.add_theme_color(dpg.mvThemeCol_Text, value=(255, 255, 255), category=dpg.mvThemeCat_Core)

          dpg.bind_item_theme(self.countdown_text, text_accent)
          dpg.bind_item_theme(self.enable_character_awake_checkbox, text_accent)
          dpg.bind_item_theme(self.enable_auto_equip_checkbox, text_accent)

      with dpg.theme() as start_btn_theme:
        self.start_btn_theme = start_btn_theme
        with dpg.theme_component(dpg.mvAll):
          category = dpg.mvThemeCat_Core
          dpg.add_theme_color(dpg.mvThemeCol_Text, value=(0, 0, 0), category=category)
          dpg.add_theme_color(dpg.mvThemeCol_Button, value=(0, 193, 0), category=category)
          dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, value=(2, 170, 2), category=category)
          dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, value=(2, 150, 2), category=category)

      self.add_start_btn()