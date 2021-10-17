import typing
import os
import json
from talon import Module, Context, canvas, screen, ui, ctrl, settings
from talon.skia import Paint, Rect
from talon.types.point import Point2d

mod = Module()
ctx = Context()

mod.tag('fine_grid_enabled', desc='Tag enables fine grid commands')


class FineMouseGrid:
    ZOOM_RATIO = 0.6
    def __init__(self):
        self.screen = None
        self.mcanvas = None
        self.rect = None
        self.active = False

        letters = [chr(97 + i) for i in range(26)]
        numbers = [str(i) for i in range(10)]
        self.columns = letters + numbers
        self.rows = letters + numbers

    def setup(self, *, screen_num: int = None):
        screens = ui.screens()
        # each if block here might set the rect to None to indicate failure
        if screen_num is not None:
            screen = screens[screen_num % len(screens)]
        else:
            screen = screens[0]

        if not self.rect:
            rect = screen.rect
            self.rect = rect.copy()

        self.screen = screen

        if self.mcanvas is not None:
            self.mcanvas.close()
        self.mcanvas = canvas.Canvas.from_screen(screen)

        self.mcanvas.register("draw", self.draw)
        self.mcanvas.freeze()

    def draw(self, canvas):
        def draw_text(offset_x, offset_y, width, height):
            row_height = height / len(self.rows)
            column_width = width / len(self.columns)

            canvas.paint.text_align = canvas.paint.TextAlign.CENTER
            canvas.paint.textsize = 16
            for row, row_char in enumerate(self.rows):
                for col, col_char in enumerate(self.columns):
                    coordinate_x = offset_x + column_width * (col + 0.5)
                    coordinate_y = offset_y + row_height * (row + 0.5)
                    text_string = f"{row_char}{col_char}"
                    text_rect = canvas.paint.measure_text(text_string)[1]
                    background_rect = text_rect.copy()
                    background_rect.center = Point2d(
                        coordinate_x,
                        coordinate_y,
                        )
                    background_rect = background_rect.inset(-4)
                    canvas.paint.color = "9999994f"
                    canvas.paint.style = Paint.Style.FILL
                    canvas.draw_rect(background_rect)
                    canvas.paint.color = "00ff008f"
                    canvas.draw_text(
                        text_string,
                        coordinate_x,
                        coordinate_y + text_rect.height / 2,
                        )

        draw_text(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

        self.active = True

    def close(self):
        self.mcanvas.unregister("draw", self.draw)
        self.mcanvas.close()
        self.mcanvas = None
        self.active = False

    def reset(self):
        self.rect = None
        self.redraw()

    def redraw(self):
        self.close()
        self.setup()
        self.draw(self.mcanvas)

    def get_coordinate(self, row: str, column: str):        
        column_index = self.columns.index(column)
        row_index = self.rows.index(row)

        x = self.rect.x + self.rect.width * (column_index + 0.5) / len(self.columns)
        y = self.rect.y + self.rect.height * (row_index + 0.5) / len(self.rows)
        return x, y

    def go_coordinate(self, row: str, column: str):
        ctrl.mouse_move(*self.get_coordinate(row, column))

    def zoom(self, row: str, column: str):
        x, y = self.get_coordinate(row, column)

        xnew_min = self.rect.x 
        xnew_max = self.rect.x + (1 - self.ZOOM_RATIO)*self.rect.width
        xnew = x - 0.5*self.ZOOM_RATIO*self.rect.width
        self.rect.x = max(min(xnew, xnew_max), xnew_min)

        ynew_min = self.rect.y 
        ynew_may = self.rect.y + (1 - self.ZOOM_RATIO)*self.rect.height
        ynew = y - 0.5*self.ZOOM_RATIO*self.rect.height
        self.rect.y = max(min(ynew, ynew_may), ynew_min)

        self.rect.width = self.ZOOM_RATIO*self.rect.width
        self.rect.height = self.ZOOM_RATIO*self.rect.height
        self.redraw()


grid = FineMouseGrid()


@mod.capture(rule="(<user.letter> | <user.number_key>) (<user.letter> | <user.number_key>)")
def coordinate(m) -> str:
    "column or row character"
    return ','.join(m)


@mod.action_class
class GridActions:
    def fine_grid_activate():
        """activate chess board"""
        ctx.tags = ['user.fine_grid_enabled']
        grid.rect = None
        if not grid.mcanvas:
            grid.setup()
        grid.draw(grid.mcanvas)

    def fine_grid_close():
        """Close the chessboard"""
        print(ctx.tags)
        grid.close()
        ctx.tags = []

    def go_coordinate(coordinate: str):
        """select coordinate"""
        print(coordinate)
        row, column = coordinate.split(',')
        grid.go_coordinate(row, column)

    def zoom(coordinate: str):
        """zoom"""
        row, column = coordinate.split(',')
        grid.zoom(row, column)

    def fine_grid_reset():
        """reset grid to original state"""
        grid.reset()
