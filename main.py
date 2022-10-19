# All DPG apps must do 3 things:
# Create & Destroy context
# Create & Show Viewport
# Setup & Start DearPyGui
from datetime import datetime

import schedule
import dearpygui.dearpygui as dpg
import pyautogui

from src.components.auto_trainer import AutoTrainer

pyautogui.FAILSAFE = True

dpg.create_context()

# Components
auto_trainer = AutoTrainer()

dpg.create_viewport(
    title='Tibia Auto Trainer', 
    width=250, 
    height=240,
    resizable=False,
    always_on_top=True,
    small_icon='images/small_icon.ico',
    large_icon='images/large_icon.png'
)
dpg.setup_dearpygui()
dpg.show_viewport()

# Setup global theme
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        category = dpg.mvThemeCat_Core
        dpg.add_theme_color(dpg.mvThemeCol_Text, (192, 192, 192), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (24, 25, 25), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (192, 192, 192), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (192, 192, 192, 100), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (192, 192, 192, 200), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (54, 54, 54), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (54, 54, 54), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (192, 192, 192, 100), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0), category=category)
        dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (120, 120, 120), category=category)

        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, x=14, y=14, category=category)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, x=8, category=category)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, y=8, category=category)

        dpg.bind_theme(global_theme)

# Run event loop
while dpg.is_dearpygui_running():
    schedule.run_pending()
    dpg.render_dearpygui_frame()

    character_job = schedule.get_jobs(auto_trainer.character_awake_job_tag)
    if len(character_job):
        diff = character_job[0].next_run - datetime.today()
        auto_trainer.update_countdown(round(diff.total_seconds()))
    
dpg.destroy_context()