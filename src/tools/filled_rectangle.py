# filled_rectangle.py
#
# Copyright 2023 Nokse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gdk, Gio, GObject

import math

class FilledRectangle(GObject.GObject):
    def __init__(self, _canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas

        self._active = False
        self._char = '#'

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

        self.flip = False
        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.end_x = 0
        self.end_y = 0

        self._style = 0

        self.prev_x = 0
        self.prev_y = 0

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

    @GObject.Property(type=str, default='#')
    def char(self):
        return self._char

    @char.setter
    def char(self, value):
        self._char = value
        self.notify('char')

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return
        self.start_x = start_x
        self.start_y = start_y

    def on_drag_follow(self, gesture, end_x, end_y):
        if not self._active: return
        if self.flip:
            end_x = - end_x
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        width = int((end_x + self.start_x) // self.x_mul - start_x_char)
        height = int((end_y + self.start_y) // self.y_mul - start_y_char)

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul

        if abs(self.prev_x) > abs(width) or abs(self.prev_y) > abs(height) or math.copysign(1, self.prev_x) != math.copysign(1, width) or math.copysign(1, self.prev_y) != math.copysign(1, height):
            self.canvas.clear_preview()
        self.prev_x = width
        self.prev_y = height
        self.changed_chars = []

        if width < 0:
            width = -width
            start_x_char -= width
        width += 1
        if height < 0:
            height = - height
            start_y_char -= height
        height += 1
        self.preview_filled_rectangle(start_x_char, start_y_char, width, height, self._char)

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.canvas.clear_preview()

        if self.flip:
            delta_x = - delta_x
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((delta_x + self.start_x) // self.x_mul - start_x_char)
        height = int((delta_y + self.start_y) // self.y_mul - start_y_char)

        self.prev_x = 0
        self.prev_y = 0

        self.canvas.add_undo_action("Filled Rectangle")

        if width < 0:
            width = -width
            start_x_char -= width
        width += 1
        if height < 0:
            height = - height
            start_y_char -= height
        height += 1
        self.draw_filled_rectangle(start_x_char, start_y_char, width, height, self._char)

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        pass

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass

    def preview_filled_rectangle(self, start_x_char, start_y_char, width, height, char):
        for y in range(height):
            for x in range(width):
                self.canvas.preview_char_at(start_x_char + x, start_y_char + y, char)

    def draw_filled_rectangle(self, start_x_char, start_y_char, width, height, char):
        for y in range(height):
            for x in range(width):
                self.canvas.draw_char_at(start_x_char + x, start_y_char + y, char)
