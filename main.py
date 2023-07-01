from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import os


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
        self.drawing_area.pack(side=TOP)

        self.controls_frame = Frame(root, width=500, height=200, bg='lightgrey')
        self.controls_frame.pack(side=BOTTOM)

        colors = ['black', 'blue', 'green', 'lime', 'orange', 'purple', 'red', 'yellow', 'white']
        self.color_buttons = []
        for i, color in enumerate(colors):
            image = Image.open(os.path.join('icon', f'{color}.png'))  # Opens the image from the icon directory
            image = image.resize((20, 20), Image.ANTIALIAS)  # Resizes the image
            photo = ImageTk.PhotoImage(image)  # Creates a PhotoImage
            button = Button(self.controls_frame, image=photo, command=lambda i=i: self.choose_color(colors[i]))
            button.image = photo  # Necessary to prevent garbage collection from deleting the PhotoImage
            button.pack(side=LEFT)
            self.color_buttons.append(button)

        # Create a scale for brush size
        self.brush_size_scale = Scale(self.controls_frame, from_=1, to=50, orient=HORIZONTAL, label="Brush Size",
                                      command=self.change_brush_size)
        self.brush_size_scale.set(self.brush_size)
        self.brush_size_scale.pack(side=TOP)

        eraser_image = Image.open(os.path.join('icon', 'rubber.png'))
        eraser_image = eraser_image.resize((20, 20), Image.ANTIALIAS)
        eraser_photo = ImageTk.PhotoImage(eraser_image)
        self.eraser_button = Button(self.controls_frame, image=eraser_photo, command=self.use_eraser)
        self.eraser_button.image = eraser_photo
        self.eraser_button.pack(side=LEFT)

        pencil_image = Image.open(os.path.join('icon', 'bursh.png'))
        pencil_image = pencil_image.resize((20, 20), Image.ANTIALIAS)
        pencil_photo = ImageTk.PhotoImage(pencil_image)
        self.pencil_button = Button(self.controls_frame, image=pencil_photo, command=self.use_pencil)
        self.pencil_button.image = pencil_photo
        self.pencil_button.pack(side=LEFT)

        bucket_image = Image.open(os.path.join('icon', 'bucket.png'))
        bucket_image = bucket_image.resize((20, 20), Image.ANTIALIAS)
        bucket_photo = ImageTk.PhotoImage(bucket_image)
        self.bucket_button = Button(self.controls_frame, image=bucket_photo, command=self.use_bucket)
        self.bucket_button.image = bucket_photo
        self.bucket_button.pack(side=LEFT)

        clean_image = Image.open(os.path.join('icon', 'clean.png'))
        clean_image = clean_image.resize((20, 20), Image.ANTIALIAS)
        clean_photo = ImageTk.PhotoImage(clean_image)
        self.clean_button = Button(self.controls_frame, image=clean_photo, command=self.clean_canvas)
        self.clean_button.image = clean_photo
        self.clean_button.pack(side=LEFT)

        self.drawing_area.bind("<B1-Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_button_down)
        self.drawing_area.bind("<Motion>", self.show_brush_size)

    def choose_color(self, color_name):
        # color mapping dictionary
        color_dict = {
            'black': [0, 0, 0],
            'blue': [0, 0, 255],
            'green': [0, 255, 0],
            'lime': [0, 255, 255],
            'orange': [255, 165, 0],
            'purple': [128, 0, 128],
            'red': [255, 0, 0],
            'yellow': [255, 255, 0],
            'white': [255, 255, 255]
        }
        self.color = color_dict[color_name]

    def use_pencil(self):
        self.drawing_tool = "pencil"

    def use_eraser(self):
        self.drawing_tool = "eraser"

    def clean(self):
        self.img = np.ones((500, 500, 3), dtype=np.uint8) * 255
        self.update_canvas()

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
            cv2.line(self.img, (self.x_position, self.y_position), (event.x, event.y), self.color, self.brush_size * 2)
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

    def clean_canvas(self):
        self.img = np.ones((500, 500, 3), dtype=np.uint8) * 255
        self.update_canvas()


root = Tk()
paint_app = PaintApp(root)
root.mainloop()
