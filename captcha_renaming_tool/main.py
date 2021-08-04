import os
import tkinter as tk
import re
from functools import partial
from tkinter import *
from tkinter import ttk, filedialog, messagebox

from PIL import ImageTk, Image

from helper_texts import show_help_text


class CaptchaRenamingTool:
    folder_path = None
    captcha_solution_text = None
    root = None
    current_captcha_name = None
    current_captcha_image = None
    image_index = 0
    image_list = []
    
    def __init__(self):
        self.root = Tk()

        # Title of app
        self.root.title("Captcha Renaming Tool")

        # Size of the screen
        screen_size = (700, 350)
        self.root.geometry(f'{screen_size[0]}x{screen_size[1]}')

        self.folder_path = StringVar()
        self.captcha_solution_text = StringVar()
        self.current_captcha_name = StringVar()

        select_folder_button = ttk.Button(self.root, text='Select Folder', command=self.get_folder_path)
        select_folder_button.grid(row=0, column=0)

        import_captchas_button = ttk.Button(self.root, text='Load Captchas', command=self.import_captchas)
        import_captchas_button.grid(row=0, column=2)

        show_help_button = ttk.Button(self.root, text='Show Help', command=self.show_help)
        show_help_button.place(relx=0.5, rely=0.5, anchor='center')

        self.root.mainloop()

    def get_folder_path(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def import_captchas(self):
        folder = self.folder_path.get()

        for image in os.listdir(folder):
            if image.endswith('jpeg'):
                image = Image.open(f'{folder}/{image}')
                tk_image = ImageTk.PhotoImage(image)
                self.image_list.append((tk_image, image))

        self.current_captcha_image = Label(image=self.image_list[self.image_index][0])
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        self.update_image_label()

        captcha_solution = tk.Entry(self.root, textvariable=self.captcha_solution_text)
        captcha_solution.insert(0, '(type captcha solution here)')
        captcha_solution.place(relx=0.5, rely=0.8, anchor='center')

        captcha_solution.bind('<Return>', self.rename_image_file)

        next_image_button = ttk.Button(self.root, text='Next',
                                       command=partial(self.switch_captcha_image, 1))
        next_image_button.place(relx=0.85, rely=0.5, anchor='center')

        previous_image_button = ttk.Button(self.root, text='Previous',
                                           command=partial(self.switch_captcha_image, -1))
        previous_image_button.place(relx=0.15, rely=0.5, anchor='center')

    def rename_image_file(self, event):
        old_image_path = self.image_list[self.image_index][1].filename
        image_directory = re.findall(r'(.+\/)', old_image_path)[0]
        image_extension = re.findall(r'(\.\w+)', old_image_path)[0]

        new_image_path = image_directory + self.captcha_solution_text.get() + image_extension

        os.rename(old_image_path, new_image_path)

        self.image_list[self.image_index][1].filename = new_image_path

        self.switch_captcha_image()

    def switch_captcha_image(self, direction=1):
        try:
            image = self.image_list[self.image_index+direction][0]
            self.current_captcha_image.destroy()
            self.current_captcha_image = Label(image=image)
            self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

            self.image_index += direction

            self.update_image_label()
        except IndexError:
            pass

    def update_image_label(self):
        image_path = self.image_list[self.image_index][1].filename
        captcha_name = re.findall(r'.+\/(.+)\.', image_path)[0]

        try:
            self.current_captcha_name.destroy()
        except AttributeError:
            pass

        self.current_captcha_name = Label(text=captcha_name)
        self.current_captcha_name.place(relx=0.5, rely=0.25, anchor='center')

    @staticmethod
    def show_help():
        messagebox.showinfo('Help', show_help_text)


if __name__ == '__main__':
    CaptchaRenamingTool()
