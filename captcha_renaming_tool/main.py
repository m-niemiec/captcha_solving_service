import os
import tkinter as tk
import re
from functools import partial
from tkinter import *
from tkinter import ttk, filedialog

from PIL import ImageTk, Image


class CaptchaRenamingTool:
    folder_path = None
    captcha_solution_text = None
    root = None
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

        button_select_folder = ttk.Button(self.root, text='Select Folder', command=self.get_folder_path)
        button_select_folder.grid(row=0, column=0)
        c = ttk.Button(self.root, text='Load Captchas', command=self.import_images)
        c.grid(row=0, column=2)

        self.root.mainloop()

    def get_folder_path(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def rename_image_file(self, event):
        image_path = self.image_list[self.image_index][1].filename
        image_directory = re.findall(r'(.+\/)', image_path)[0]
        image_extension = re.findall(r'(\.\w+)', image_path)[0]

        os.rename(image_path, image_directory + self.captcha_solution_text.get() + image_extension)

    def import_images(self):
        folder = self.folder_path.get()

        for image in os.listdir(folder):
            if image.endswith('jpeg'):
                image = Image.open(f'{folder}/{image}')
                tk_image = ImageTk.PhotoImage(image)
                self.image_list.append((tk_image, image))

        current_captcha_image = Label(image=self.image_list[self.image_index][0])
        current_captcha_image.grid(row=1, column=0, columnspan=3)
        current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        captcha_solution = tk.Entry(self.root, textvariable=self.captcha_solution_text)
        captcha_solution.insert(0, '(type captcha solution here)')
        captcha_solution.grid(row=0, column=0)
        captcha_solution.place(relx=0.5, rely=0.8, anchor='center')

        captcha_solution.bind('<Return>', self.rename_image_file)

        next_image_button = ttk.Button(self.root, text='Next',
                                       command=partial(self.switch_captcha_image, current_captcha_image, 1))
        next_image_button.grid(row=0, column=0)
        next_image_button.place(relx=0.85, rely=0.5, anchor='center')

        previous_image_button = ttk.Button(self.root, text='Previous',
                                           command=partial(self.switch_captcha_image, current_captcha_image, -1))
        previous_image_button.grid(row=0, column=0)
        previous_image_button.place(relx=0.15, rely=0.5, anchor='center')

    def switch_captcha_image(self, current_captcha_image, direction):
        current_captcha_image.destroy()

        try:
            current_captcha_image = Label(image=self.image_list[self.image_index+direction][0])
            current_captcha_image.grid(row=1, column=0, columnspan=3)
            current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

            self.image_index += direction
        except IndexError:
            pass


if __name__ == '__main__':
    CaptchaRenamingTool()
