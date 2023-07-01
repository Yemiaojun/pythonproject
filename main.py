from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np

class PaintApp:
    drawing_tool = "pencil"
    left_button = "up"
    x_position, y_position = None, None
    color = [0, 0, 0]  # default color is black
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255  # default background is white
    img_tk = None
    brush_size = 5  # default brush size

    def __init__(self, root):
        self.root = root
        self.drawing_area = Canvas(root, width=500, height=500)
        self.img_tk = ImageTk.PhotoImage(Image.fromarray(self.img))
        self.canvas_img = self.drawing_area.create_image(0, 0, image=self.img_tk, anchor=NW)
        self.drawing_area.pack(side=LEFT)

        self.controls_frame = Frame(root, width=200, height=500, bg='lightgrey')
        self.controls_frame.pack(side=RIGHT)

        # Create a scale for brush size
        self.brush_size_scale = Scale(self.controls_frame, from_=1, to=50, orient=VERTICAL, label="Brush Size", command=self.change_brush_size)
        self.brush_size_scale.set(self.brush_size)
        self.brush_size_scale.pack(side=TOP)

        self.eraser_button = Button(self.controls_frame, text="Eraser", command=self.use_eraser)
        self.eraser_button.pack(side=TOP)

        self.pencil_button = Button(self.controls_frame, text="Pencil", command=self.use_pencil)
        self.pencil_button.pack(side=TOP)

        self.bucket_button = Button(self.controls_frame, text="Paint Bucket", command=self.use_bucket)
        self.bucket_button.pack(side=TOP)

        colors = ['#FF0000', '#FFA500', '#FFFF00', '#008000', '#00FFFF', '#0000FF', '#800080', '#000000']
        self.color_buttons = [Button(self.controls_frame, bg=color, width=2, command=lambda i=i: self.choose_color(colors[i])) for i, color in enumerate(colors)]
        for button in self.color_buttons:
            button.pack(side=TOP)

        self.drawing_area.bind("<B1-Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_button_down)
        self.drawing_area.bind("<Motion>", self.show_brush_size)

    def choose_color(self, color_code):
        # convert hex color code to BGR color
        self.color = [int(color_code[i:i+2], 16) for i in (5, 3, 1)][::-1]

    def use_pencil(self):
        self.drawing_tool = "pencil"

    def use_eraser(self):
        self.drawing_tool = "eraser"

    def use_bucket(self):
        self.drawing_tool = "bucket"

    def left_button_down(self, event=None):
        self.x_position = event.x
        self.y_position = event.y

        if self.drawing_tool == "bucket":
            self.flood_fill(event.x, event.y)
        else:
            self.motion(event)

    def motion(self, event=None):
        if self.drawing_tool == 'pencil':
            cv2.line(self.img, (self.x_position, self.y_position), (event.x, event.y), self.color, self.brush_size*2)
        elif self.drawing_tool == 'eraser':
            cv2.circle(self.img, (event.x, event.y), self.brush_size, (255, 255, 255), -1)
        self.x_position = event.x
        self.y_position = event.y
        self.update_canvas()

    def flood_fill(self, x, y):
        retval, img, mask, rect = cv2.floodFill(self.img, None, (x, y), self.color, flags=8 | (255 << 8))
        self.img = img
        self.update_canvas()

    def update_canvas(self):
        self.img_tk = ImageTk.PhotoImage(Image.fromarray(self.img))
        self.drawing_area.delete("all")
        self.drawing_area.create_image(0, 0, image=self.img_tk, anchor=NW)

    def show_brush_size(self, event=None):
        if self.drawing_tool in ['pencil', 'eraser']:
            self.drawing_area.delete("cursor")  # delete old cursor
            if self.drawing_tool == 'pencil':
                outline_color = "black"
            else:  # eraser
                outline_color = "white"
            self.drawing_area.create_oval(event.x - self.brush_size, event.y - self.brush_size,
                                          event.x + self.brush_size, event.y + self.brush_size,
                                          outline=outline_color, tag="cursor")  # draw new cursor
        elif self.drawing_tool == 'bucket':
            self.drawing_area.delete("cursor")  # delete old cursor

    def change_brush_size(self, value):
        self.brush_size = int(value)

root = Tk()
paint_app = PaintApp(root)
root.mainloop()
