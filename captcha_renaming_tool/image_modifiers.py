import tkinter as tk
from functools import partial
from tkinter import ttk, Label

from PIL import ImageTk, Image, ImageEnhance

from image_control import ImageControl
from settings import Settings


class ImageModifiers(ImageControl):
    current_zoom: int = 1
    black_white_mode: bool = False
    big_contrast_mode: bool = False
    next_image_icon = None
    previous_image_icon = None
    increase_image_size_icon = None
    decrease_image_size_icon = None
    change_black_white_icon = None
    change_contrast_color_icon = None

    def apply_modes(self):
        Settings.get_value('current_captcha_image').destroy()

        image: Image = Settings.get_value('image_list')[Settings.get_value('image_index')][1]

        image = image.convert('L') if self.black_white_mode else image.convert('RGB')

        if self.big_contrast_mode:
            image = ImageEnhance.Contrast(image).enhance(2)
            image = ImageEnhance.Color(image).enhance(2)
        else:
            image = ImageEnhance.Contrast(image).enhance(1)
            image = ImageEnhance.Color(image).enhance(1)

        converted_image: ImageTk = ImageTk.PhotoImage(image)

        Settings.set_value('current_captcha_image', Label(image=converted_image))
        Settings.get_value('current_captcha_image').image = converted_image
        Settings.get_value('current_captcha_image').place(relx=0.5, rely=0.5, anchor='center')

    def render_additional_buttons(self):
        # Icons in this method needs to have a reference to prevent garbage collector from deleting them.
        self.next_image_icon = tk.PhotoImage(file='media/next_icon.png').subsample(2, 2)
        next_image_button = ttk.Button(Settings.get_value('root'), text='Next', command=partial(self.switch_captcha_image, 1),
                                       image=self.next_image_icon, compound='left')
        next_image_button.place(relx=0.85, rely=0.5, anchor='center')
        Settings.get_value('root').bind('<Up>', partial(self.switch_captcha_image, 1))

        self.previous_image_icon = tk.PhotoImage(file='media/previous_icon.png').subsample(2, 2)
        previous_image_button = ttk.Button(Settings.get_value('root'), text='Previous', command=partial(self.switch_captcha_image, -1),
                                           image=self.previous_image_icon, compound='left')
        previous_image_button.place(relx=0.15, rely=0.5, anchor='center')
        Settings.get_value('root').bind('<Down>', partial(self.switch_captcha_image, -1))

        self.increase_image_size_icon = tk.PhotoImage(file='media/zoomin_icon.png').subsample(2, 2)
        increase_image_size_button = ttk.Button(Settings.get_value('root'), text='Zoom IN', command=partial(self.set_zoom, 'increase'),
                                                image=self.increase_image_size_icon, compound='left')
        increase_image_size_button.grid(row=0, column=2, padx=3, pady=3)

        self.decrease_image_size_icon = tk.PhotoImage(file='media/zoomout_icon.png').subsample(2, 2)
        decrease_image_size_button = ttk.Button(Settings.get_value('root'), text='Zoom OUT', command=partial(self.set_zoom, 'decrease'),
                                                image=self.decrease_image_size_icon, compound='left')
        decrease_image_size_button.grid(row=0, column=3, padx=3, pady=3)

        self.change_black_white_icon = tk.PhotoImage(file='media/blackandwhite_icon.png').subsample(2, 2)
        change_black_white_button = ttk.Button(Settings.get_value('root'), text='B&W Mode', command=self.set_black_white_mode,
                                               image=self.change_black_white_icon, compound='left')
        change_black_white_button.grid(row=0, column=4, padx=3, pady=3)

        self.change_contrast_color_icon = tk.PhotoImage(file='media/increasedcolors_icon.png').subsample(2, 2)
        change_contrast_color_button = ttk.Button(Settings.get_value('root'), text='Color&Contrast Mode', command=self.set_big_contrast_mode,
                                                  image=self.change_contrast_color_icon, compound='left')
        change_contrast_color_button.grid(row=0, column=5, padx=3, pady=3)

    def set_zoom(self, direction: int):
        if direction == 'increase' and self.current_zoom < 2:
            self.current_zoom += 0.25

        elif direction == 'decrease' and self.current_zoom > 0.5:
            self.current_zoom -= 0.25

        self.update_captcha_image()

    def set_black_white_mode(self):
        self.black_white_mode: bool = False if self.black_white_mode else True

        self.update_captcha_image()

    def set_big_contrast_mode(self):
        self.big_contrast_mode: bool = False if self.big_contrast_mode else True

        self.update_captcha_image()

    def update_captcha_image(self):
        image: Image = Settings.get_value('image_list')[Settings.get_value('image_index')][1]

        resized_image = image.resize((int(Settings.get_value('current_size')[0] * self.current_zoom),
                                      int(Settings.get_value('current_size')[1] * self.current_zoom)))

        Settings.get_value('image_list')[Settings.get_value('image_index')][1]: Image = resized_image
        Settings.get_value('image_list')[Settings.get_value('image_index')][1].filename = image.filename

        resized_image = ImageTk.PhotoImage(resized_image)

        Settings.get_value('current_captcha_image').destroy()
        Settings.set_value('current_captcha_image', Label(image=resized_image))
        Settings.get_value('current_captcha_image').image = resized_image
        Settings.get_value('current_captcha_image').place(relx=0.5, rely=0.5, anchor='center')

        self.apply_modes()
        self.update_image_label()
        self.update_captcha_solution_entry()
