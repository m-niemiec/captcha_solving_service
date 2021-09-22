import os
import tkinter as tk
from tkinter import ttk, filedialog, Tk, StringVar, Label

from PIL import ImageTk, Image

from image_modifiers import ImageModifiers
from helper_texts import show_help_text
from settings import Settings


class AppFunctionalView(ImageModifiers):
    def __init__(self, root: Tk):
        Settings().root = root

        Settings().total_images_amount = 0
        Settings().image_index = 0
        Settings().image_list = []
        Settings().captcha_solution_text = StringVar()
        Settings().current_captcha_name = Label(text='', width=300, font=('calibri', 20), foreground='#D4d4d4',
                                                background='#313232')
        Settings().renamed_total_images_amount = Label(text='', foreground='#D4d4d4', background='#313232')
        Settings().update_captcha_image_method = self.update_captcha_image

        self.get_folder_path()

    def get_folder_path(self):
        # Reset variables that this function sets if users would like to select another folder.
        Settings().total_images_amount = 0

        try:
            Settings().current_captcha_image.destroy()
        except AttributeError:
            pass

        folder: str = filedialog.askdirectory()

        if not folder:
            return

        for image in os.listdir(folder):
            if image.lower().endswith(('jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png', 'gif', 'webp')):
                Settings().total_images_amount = Settings().total_images_amount + 1

                image = Image.open(f'{folder}/{image}')
                tk_image = ImageTk.PhotoImage(image)

                Settings().image_list.append([tk_image, image])

        width, height = self.get_proper_image_size()
        Settings().current_size = (width, height)

        Settings().current_captcha_image = Label(image=Settings().image_list[Settings().image_index][0])
        Settings().current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        Settings().current_captcha_name.place(relx=0.5, rely=0.25, anchor='center')

        Settings().renamed_total_images_amount.place(relx=0.5, rely=0.9, anchor='center')

        self.update_captcha_image()
        self.update_renamed_images_count()
        self.render_additional_buttons()

    @staticmethod
    def get_proper_image_size() -> tuple[int, int]:
        width, height = Settings().image_list[0][1].width, Settings().image_list[0][1].height
        max_width, max_height = Settings().root.winfo_screenwidth() * 0.5, Settings().root.winfo_screenheight() * 0.5

        width = width if width < max_width else max_width
        height = height if height < max_height else max_height

        return width, height

    @staticmethod
    def show_help():
        help_window = tk.Toplevel(background='#313232')

        label = tk.Label(help_window, text=show_help_text, background='#313232', foreground='#D4d4d4',)
        label.pack(padx=50, pady=50)

        button_close = ttk.Button(help_window, text='Close', command=help_window.destroy)
        button_close.pack()
