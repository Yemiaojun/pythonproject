from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import pygame
import time
from commentary import Commentary

class PaintApp:
    drawing_tool = "pencil"
    left_button = "up"
    x_position, y_position = None, None
    color = [0, 0, 0]  # default color is black
    img = np.ones((800, 500, 3), dtype=np.uint8) * 255  # default background is white
    img_tk = None
    brush_size = 5  # default brush size
    img_stack = []
    def __init__(self, root):
        self.root = root
        theme_color = "lightgrey"
        # Create left and right frames
        self.left_frame = Frame(root, bg=theme_color)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_frame = Frame(root, width=100, bg=theme_color)
        self.right_frame.pack(side=RIGHT, fill=Y)

        # Drawing canvas setup
        self.drawing_area = Canvas(self.left_frame, width=500, height=800)
        self.img_tk = ImageTk.PhotoImage(Image.fromarray(self.img))
        self.canvas_img = self.drawing_area.create_image(0, 0, image=self.img_tk, anchor=NW)
        self.drawing_area.pack(side=TOP, fill=BOTH, expand=True)

        # Submit button
        self.submit_frame = Frame(self.left_frame, width=500, height=100, bg=theme_color)
        self.submit_frame.pack(side=BOTTOM, fill=X)
        self.submit_button = Button(self.submit_frame, text="完成", command=self.open_entry)
        self.submit_button.pack(anchor=CENTER)

        # Controls frame
        self.controls_frame = Frame(self.left_frame, width=50, height=50, bg=theme_color)
        self.controls_frame.pack(side=BOTTOM, fill=X)

        tool_icon_image = Image.open(os.path.join('icon', 'bursh.png'))  # default tool icon
        tool_icon_image = tool_icon_image.resize((30, 30), Image.ANTIALIAS)
        self.tool_icon_image = ImageTk.PhotoImage(tool_icon_image)
        self.tool_icon_label = Label(self.controls_frame, image=self.tool_icon_image, bg=theme_color)
        self.tool_icon_label.pack(side=LEFT)

        # Tool buttons
        self.tool_frame = Frame(self.controls_frame, bg=theme_color)
        self.tool_frame.pack(side=LEFT, fill=X, expand=True)

        # Tool buttons code here...
        eraser_image = Image.open(os.path.join('icon', 'rubber.png'))
        eraser_image = eraser_image.resize((20, 20), Image.ANTIALIAS)
        eraser_photo = ImageTk.PhotoImage(eraser_image)
        self.eraser_button = Button(self.controls_frame, image=eraser_photo, command=self.use_eraser, bg=theme_color)
        self.eraser_button.image = eraser_photo
        self.eraser_button.pack(side=LEFT)

        pencil_image = Image.open(os.path.join('icon', 'bursh.png'))
        pencil_image = pencil_image.resize((20, 20), Image.ANTIALIAS)
        pencil_photo = ImageTk.PhotoImage(pencil_image)
        self.pencil_button = Button(self.controls_frame, image=pencil_photo, command=self.use_pencil, bg=theme_color)
        self.pencil_button.image = pencil_photo
        self.pencil_button.pack(side=LEFT)

        bucket_image = Image.open(os.path.join('icon', 'bucket.png'))
        bucket_image = bucket_image.resize((20, 20), Image.ANTIALIAS)
        bucket_photo = ImageTk.PhotoImage(bucket_image)
        self.bucket_button = Button(self.controls_frame, image=bucket_photo, command=self.use_bucket, bg=theme_color)
        self.bucket_button.image = bucket_photo
        self.bucket_button.pack(side=LEFT)

        clean_image = Image.open(os.path.join('icon', 'clean.png'))
        clean_image = clean_image.resize((20, 20), Image.ANTIALIAS)
        clean_photo = ImageTk.PhotoImage(clean_image)
        self.clean_button = Button(self.controls_frame, image=clean_photo, command=self.clean_canvas, bg=theme_color)
        self.clean_button.image = clean_photo
        self.clean_button.pack(side=LEFT)

        # undo button
        undo_image = Image.open(os.path.join('icon', 'undo.png'))
        undo_image = undo_image.resize((20, 20), Image.ANTIALIAS)
        undo_photo = ImageTk.PhotoImage(undo_image)
        self.undo_button = Button(self.controls_frame, image=undo_photo, command=self.undo, bg=theme_color)
        self.undo_button.image = undo_photo
        self.undo_button.pack(side=LEFT)

        # Brush size scale
        self.brush_size_scale = Scale(self.controls_frame, from_=1, to=50, orient=HORIZONTAL, label="笔刷尺寸",
                                      command=self.change_brush_size)
        self.brush_size_scale.set(self.brush_size)
        self.brush_size_scale.pack(side=RIGHT,padx=50)



        # Color buttons
        self.color_frame = Frame(self.left_frame, width=500, height=200, bg=theme_color)
        self.color_frame.pack(side=BOTTOM, fill=X, padx=120)  # padx=100 used to add space on the sides
        colors = ['black', 'blue', 'green', 'lime', 'orange', 'purple', 'red', 'yellow', 'pink','white']
        self.color_buttons = []
        for i, color in enumerate(colors):
            image = Image.open(os.path.join('icon', f'{color}.png'))
            image = image.resize((20, 20), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            button = Button(self.color_frame, image=photo, command=lambda i=i: self.choose_color(colors[i]))
            button.image = photo
            button.pack(side=LEFT, anchor=CENTER)  # anchor=CENTER used to center the buttons
            self.color_buttons.append(button)

        # Right frame content
        self.comment_label = Label(self.right_frame, text="你好", pady=100, font=("SimHei", 20), bg=theme_color)
        self.comment_label.pack(side=TOP, fill=X)

        reviewer_image = Image.open(os.path.join('icon', 'man2.png'))
        new_width = 400
        new_height = reviewer_image.height * new_width // reviewer_image.width
        reviewer_image = reviewer_image.resize((new_width, new_height), Image.ANTIALIAS)
        reviewer_photo = ImageTk.PhotoImage(reviewer_image)
        reviewer_label = Label(self.right_frame, image=reviewer_photo, bg=theme_color)
        reviewer_label.image = reviewer_photo
        reviewer_label.pack(side=BOTTOM, fill=BOTH)

        self.drawing_area.bind("<B1-Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_button_down)
        self.drawing_area.bind("<Motion>", self.show_brush_size)
        self.drawing_area.bind("<ButtonRelease-1>", self.left_button_up)

        # Initialize pygame mixer
        pygame.mixer.init()
        self.play_music('music/Salut.mp3')

        self.commentary = Commentary([
            "艺术本身就是意象，一个艺术工作者不只是素描、绘画或雕刻而已，他一定要有思想",
            "当艺术穿着破旧衣衫时,最容易让人认出它是艺术",
            "我看到了你的灵感",
            "不存在糟糕的艺术，只有随意或刻意的艺术",
            "如果你知道我的作品”丛林猎杀雪人“，你会知道艺术是什么",
            "你的艺术让我惊叹",
            "艺术是人类的天性",
            "上帝创造了人类，人类创造了艺术",
            "俗世于艺术相斥，却又密不可分",
            "我喜欢你",
            "灵感的暴雨",
            "思维的泉涌",
            "情感的乱流",
            "艺术的诞生地只有一个，那就是你",
            "何不在画中增添一点”迷人的爱情“",
            "何不在画中增添一点“吊诡的哀伤”",
            "何不在画中增添一点”优雅的几何“",
            "何不在画中增添一点“忧郁的漩涡”",
            "何不在画中增添一点“井喷的秘密”",
            "简洁可以是艺术，繁复也可以是艺术",
            "你就是艺术",
            "我就是艺术",
            "瀑布，瀑布"
        ], self.comment_label)

        self.commentary.set_random_comment()

    def random_comment_timer(self):
        self.comment_label.config(text=self.commentary.random_comment())
        self.root.after(10000, self.random_comment_timer)  # update the comment every 10 seconds (10000 milliseconds)
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
            'white': [255, 255, 255],
            'pink' : [255, 174, 201]
        }
        self.color = color_dict[color_name]

    def use_pencil(self):
        self.drawing_tool = "pencil"
        tool_icon_image = Image.open(os.path.join('icon', 'bursh.png'))  # update tool icon
        tool_icon_image = tool_icon_image.resize((30, 30), Image.ANTIALIAS)
        self.tool_icon_image = ImageTk.PhotoImage(tool_icon_image)
        self.tool_icon_label.config(image=self.tool_icon_image)

    def use_eraser(self):
        self.drawing_tool = "eraser"
        tool_icon_image = Image.open(os.path.join('icon', 'rubber.png'))  # update tool icon
        tool_icon_image = tool_icon_image.resize((30, 30), Image.ANTIALIAS)  # resize the image
        self.tool_icon_image = ImageTk.PhotoImage(tool_icon_image)
        self.tool_icon_label.config(image=self.tool_icon_image)

    def clean(self):

        self.img = np.ones((800, 500, 3), dtype=np.uint8) * 255
        self.update_canvas()
        self.img_stack.append(self.img.copy())  # add the current state to the stack

    def use_bucket(self):
        self.drawing_tool = "bucket"
        tool_icon_image = Image.open(os.path.join('icon', 'bucket.png'))  # update tool icon
        tool_icon_image = tool_icon_image.resize((30, 30), Image.ANTIALIAS)  # resize the image
        self.tool_icon_image = ImageTk.PhotoImage(tool_icon_image)
        self.tool_icon_label.config(image=self.tool_icon_image)

    def left_button_down(self, event=None):
        self.x_position = event.x
        self.y_position = event.y

        if self.drawing_tool == "bucket":
            self.flood_fill(event.x, event.y)
        else:
            self.motion(event)

    def left_button_up(self, event=None):
        if self.drawing_tool in ["pencil", "eraser"]:  # Only add to stack if pencil or eraser was used
            self.img_stack.append(self.img.copy())
            print(f"Saved state to img_stack. Stack size: {len(self.img_stack)}")


    def motion(self, event=None):
        if self.drawing_tool == 'pencil':
            cv2.line(self.img, (self.x_position, self.y_position), (event.x, event.y), self.color, self.brush_size * 2)
        elif self.drawing_tool == 'eraser':
            cv2.line(self.img, (self.x_position, self.y_position), (event.x, event.y),  (255, 255, 255), self.brush_size * 2)
        self.x_position = event.x
        self.y_position = event.y
        self.update_canvas()

    def flood_fill(self, x, y):
        retval, img, mask, rect = cv2.floodFill(self.img, None, (x, y), self.color, flags=8 | (255 << 8))
        self.img = img
        self.update_canvas()
        self.img_stack.append(self.img.copy())  # add the current state to the stack

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
        self.img = np.ones((800, 500, 3), dtype=np.uint8) * 255
        self.update_canvas()
        self.img_stack.append(self.img.copy())  # add the current state to the stack

    def open_entry(self):
        self.entry_window = Toplevel(self.root)
        self.entry_window.title('最后一步')

        # Set the pop-up window as a child of the root window
        self.entry_window.transient(self.root)

        # Set window size
        self.entry_window.geometry("300x200")  # Width x Height

        # Set the minimum and maximum window size
        self.entry_window.minsize(300, 200)  # Minimum width and height
        self.entry_window.maxsize(500, 400)  # Maximum width and height

        Label(self.entry_window, text="为这副作品命名", pady=20).pack()
        self.artwork_name = Entry(self.entry_window)
        self.artwork_name.pack(padx=50, pady=20)  # Provide padding for the Entry widget

        Button(self.entry_window, text="确认", command=self.save_image).pack()
        Button(self.entry_window, text="取消", command=self.entry_window.destroy).pack()

        # Center the window
        self.entry_window.update()
        width = self.entry_window.winfo_width()
        height = self.entry_window.winfo_height()
        x = (self.entry_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.entry_window.winfo_screenheight() // 2) - (height // 2)
        self.entry_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # Grabs all the events
        self.entry_window.grab_set()

    def save_image(self):
        name = self.artwork_name.get()  # Fetch the user input
        if name:
            save_path = os.path.join('works', f'{name}.png')

            # Convert the OpenCV image to a PIL image
            img_pil = Image.fromarray(self.img)

            # Save the image using PIL
            img_pil.save(save_path)

            self.commentary.analyze_image(self.img)  # Analyze the image

            self.entry_window.destroy()  # Close the name entry window

    def undo(self):
        if len(self.img_stack) > 1:
            self.img_stack.pop()  # remove the current state
            self.img = self.img_stack[-1]
            self.img_stack.pop()  # remove the current state
            self.img_stack.append(self.img.copy())
            self.update_canvas()
            print(f"Undo performed. Current stack size: {len(self.img_stack)}")
        elif len(self.img_stack) == 1:  # only one state left
            self.img_stack.clear()  # clear the entire stack
            self.clean()  # clean the canvas
            print("Performed undo. Canvas cleaned and the entire stack was cleared.")

    def play_music(self, music_file):
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(loops=-1)



root = Tk()
paint_app = PaintApp(root)
root.mainloop()
