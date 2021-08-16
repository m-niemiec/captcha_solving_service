import os
import re
import tkinter as tk
from functools import partial
from tkinter import ttk, filedialog, messagebox, Tk, StringVar, Label

from PIL import ImageTk, Image, ImageEnhance


class AppFunctionalView:
    def __init__(self, root: Tk):
        self.root = root

        self.current_captcha_image = None
        self.total_images_amount: int = 0
        self.renamed_images_amount: int = -1
        self.image_index: int = 0
        self.image_list: list[list] = []
        self.current_zoom: float = 1
        self.current_size = None
        self.black_white_mode: bool = False
        self.big_contrast_mode: bool = False
        self.captcha_solution_text = None
        self.next_image_icon = None
        self.previous_image_icon = None
        self.increase_image_size_icon = None
        self.decrease_image_size_icon = None
        self.change_black_white_icon = None
        self.change_contrast_color_icon = None
        self.current_captcha_name: Label = Label(text='', font=('calibri', 20), foreground='#D4d4d4', background='#313232')
        self.renamed_total_images_amount: Label = Label(text='', foreground='#D4d4d4', background='#313232')

        self.get_folder_path()

    def get_folder_path(self):
        # Reset variables that this function sets if users would like to select another folder.
        self.total_images_amount: int = 0

        try:
            self.current_captcha_image.destroy()
        except AttributeError:
            pass

        folder: str = filedialog.askdirectory()

        if not folder:
            return

        for image in os.listdir(folder):
            if image.lower().endswith(('jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png', 'gif', 'webp')):
                self.total_images_amount += 1

                image = Image.open(f'{folder}/{image}')
                tk_image = ImageTk.PhotoImage(image)

                self.image_list.append([tk_image, image])

        self.current_size: tuple[int, int] = (self.image_list[0][1].width, self.image_list[0][1].height)

        self.current_captcha_image: Label = Label(image=self.image_list[self.image_index][0])
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        self.current_captcha_name.place(relx=0.5, rely=0.25, anchor='center')

        self.renamed_total_images_amount.place(relx=0.5, rely=0.9, anchor='center')

        self.update_captcha_image()
        self.update_renamed_images_count()
        self.render_additional_buttons()

    def apply_modes(self):
        self.current_captcha_image.destroy()

        image: Image = self.image_list[self.image_index][1]

        image = image.convert('L') if self.black_white_mode else image.convert('RGB')

        if self.big_contrast_mode:
            image = ImageEnhance.Contrast(image).enhance(2)
            image = ImageEnhance.Color(image).enhance(2)
        else:
            image = ImageEnhance.Contrast(image).enhance(1)
            image = ImageEnhance.Color(image).enhance(1)

        converted_image: ImageTk = ImageTk.PhotoImage(image)

        self.current_captcha_image: Label = Label(image=converted_image)
        self.current_captcha_image.image = converted_image
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

    def render_additional_buttons(self):
        # Icons in this method needs to have a reference to prevent garbage collector from deleting them.
        self.next_image_icon = tk.PhotoImage(file='media/next_icon.png').subsample(2, 2)
        next_image_button = ttk.Button(self.root, text='Next', command=partial(self.switch_captcha_image, 1),
                                       image=self.next_image_icon, compound='left')
        next_image_button.place(relx=0.85, rely=0.5, anchor='center')
        self.root.bind('<Up>', partial(self.switch_captcha_image, 1))

        self.previous_image_icon = tk.PhotoImage(file='media/previous_icon.png').subsample(2, 2)
        previous_image_button = ttk.Button(self.root, text='Previous', command=partial(self.switch_captcha_image, -1),
                                           image=self.previous_image_icon, compound='left')
        previous_image_button.place(relx=0.15, rely=0.5, anchor='center')
        self.root.bind('<Down>', partial(self.switch_captcha_image, -1))

        self.increase_image_size_icon = tk.PhotoImage(file='media/zoomin_icon.png').subsample(2, 2)
        increase_image_size_button = ttk.Button(self.root, text='Zoom IN', command=partial(self.set_zoom, 'increase'),
                                                image=self.increase_image_size_icon, compound='left')
        increase_image_size_button.grid(row=0, column=2, padx=3, pady=3)

        self.decrease_image_size_icon = tk.PhotoImage(file='media/zoomout_icon.png').subsample(2, 2)
        decrease_image_size_button = ttk.Button(self.root, text='Zoom OUT', command=partial(self.set_zoom, 'decrease'),
                                                image=self.decrease_image_size_icon, compound='left')
        decrease_image_size_button.grid(row=0, column=3, padx=3, pady=3)

        self.change_black_white_icon = tk.PhotoImage(file='media/blackandwhite_icon.png').subsample(2, 2)
        change_black_white_button = ttk.Button(self.root, text='B&W Mode', command=self.set_black_white_mode,
                                               image=self.change_black_white_icon, compound='left')
        change_black_white_button.grid(row=0, column=4, padx=3, pady=3)

        self.change_contrast_color_icon = tk.PhotoImage(file='media/increasedcolors_icon.png').subsample(2, 2)
        change_contrast_color_button = ttk.Button(self.root, text='Color&Contrast Mode', command=self.set_big_contrast_mode,
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
        image: Image = self.image_list[self.image_index][1]

        resized_image = image.resize((int(self.current_size[0] * self.current_zoom),
                                      int(self.current_size[1] * self.current_zoom)))

        self.image_list[self.image_index][1]: Image = resized_image
        self.image_list[self.image_index][1].filename = image.filename

        resized_image = ImageTk.PhotoImage(resized_image)

        self.current_captcha_image.destroy()
        self.current_captcha_image = Label(image=resized_image)
        self.current_captcha_image.image = resized_image
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        self.apply_modes()
        self.update_image_label()
        self.update_captcha_solution_entry()

    def rename_image_file(self, event):
        old_image_path: str = self.image_list[self.image_index][1].filename
        image_directory: str = re.findall(r'(.+\/)', old_image_path)[0]
        image_extension: str = re.findall(r'(\.\w+)', old_image_path)[0]

        # If user didn't provide any name, do nothing.
        if not self.captcha_solution_text.get():
            return

        new_image_path: str = image_directory + self.captcha_solution_text.get() + image_extension

        if os.path.isfile(new_image_path):
            messagebox.showerror('Warning!', 'Image with this name already exist!')
        else:
            os.replace(old_image_path, new_image_path)

            self.image_list[self.image_index][1].filename = new_image_path

            self.switch_captcha_image()
            self.update_captcha_solution_entry()
            self.update_renamed_images_count()
            self.update_image_label()

    def switch_captcha_image(self, direction: int = 1, event=None):
        try:
            image: ImageTk = self.image_list[self.image_index+direction][0]
            self.current_captcha_image.destroy()
            self.current_captcha_image = Label(image=image)
            self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

            if self.image_index > 0 or direction == 1:
                self.image_index += direction

            self.update_captcha_image()
        except IndexError:
            pass

    def update_image_label(self):
        image_path = self.image_list[self.image_index][1].filename

        captcha_name: str = re.findall(r'.+\/(.+)\.', image_path)[0]

        self.current_captcha_name.config(text=captcha_name)

    def update_renamed_images_count(self):
        self.renamed_images_amount += 1

        if self.renamed_images_amount == self.total_images_amount:
            messagebox.showinfo('Success!', 'You renamed all captcha images in folder!')

        self.renamed_total_images_amount.config(text=f'Renamed {self.renamed_images_amount} '
                                                     f'images out of {self.total_images_amount}.')

    def update_captcha_solution_entry(self):
        self.captcha_solution_text = StringVar()

        captcha_solution_entry = tk.Entry(self.root, textvariable=self.captcha_solution_text, background='#4e4e4e',
                                          foreground='#D4d4d4', borderwidth='0', highlightcolor='#313232')
        captcha_solution_entry.insert(0, '(type captcha solution here)')
        captcha_solution_entry.place(relx=0.5, rely=0.8, anchor='center')

        def _on_entry_click(event):
            if captcha_solution_entry.get() == '(type captcha solution here)':
                captcha_solution_entry.delete(0, 'end')
                captcha_solution_entry.insert(0, '')

        def _on_focusout(event):
            if captcha_solution_entry.get() == '':
                captcha_solution_entry.insert(0, '(type captcha solution here)')

        captcha_solution_entry.bind('<FocusIn>', _on_entry_click)
        captcha_solution_entry.bind('<FocusOut>', _on_focusout)
        captcha_solution_entry.bind('<Return>', self.rename_image_file)
        captcha_solution_entry.focus()
