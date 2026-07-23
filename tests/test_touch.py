import sys
sys.path.append('firmware/python')
from UI.touch_interface import TouchInterface

ti = TouchInterface('firmware/python/UI/touch_settings.json', (320, 240))
ti.last_x = 672
ti.last_y = 1097
ui_state = {}
cmd, mapped_x, mapped_y = ti._map_to_command(ti.last_x, ti.last_y, ui_state)
print(f"TEST -> MAPPED: {mapped_x}, {mapped_y} | CMD: {cmd}")
