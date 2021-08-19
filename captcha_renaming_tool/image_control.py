import os
import re
import tkinter as tk
from tkinter import messagebox, StringVar, Label

from PIL import ImageTk

from settings import Settings


class ImageControl:
    renamed_images_amount: int = -1

    def update_captcha_solution_entry(self):
        Settings.set_value('captcha_solution_text', StringVar())

        captcha_solution_entry = tk.Entry(Settings.get_value('root'), textvariable=Settings.get_value('captcha_solution_text'),
                                          background='#4e4e4e', foreground='#D4d4d4', borderwidth='0', highlightcolor='#313232')
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

    def rename_image_file(self, event):
        old_image_path: str = Settings.get_value('image_list')[Settings.get_value('image_index')][1].filename
        image_directory: str = re.findall(r'(.+\/)', old_image_path)[0]
        image_extension: str = re.findall(r'(\.\w+)', old_image_path)[0]

        # If user didn't provide any name, do nothing.
        if not Settings.get_value('captcha_solution_text').get():
            return

        new_image_path: str = image_directory + Settings.get_value('captcha_solution_text').get() + image_extension

        if os.path.isfile(new_image_path):
            messagebox.showerror('Warning!', 'Image with this name already exist!')
        else:
            os.replace(old_image_path, new_image_path)

            Settings.get_value('image_list')[Settings.get_value('image_index')][1].filename = new_image_path

            self.switch_captcha_image()
            self.update_captcha_solution_entry()
            self.update_renamed_images_count()
            self.update_image_label()

    def update_renamed_images_count(self):
        self.renamed_images_amount += 1

        if self.renamed_images_amount == Settings.get_value('total_images_amount'):
            messagebox.showinfo('Success!', 'You renamed all captcha images in folder!')

        Settings.get_value('renamed_total_images_amount').config(text=f'Renamed {self.renamed_images_amount} '
                                                                      f'images out of {Settings.get_value("total_images_amount")}.')

    @staticmethod
    def update_image_label():
        image_path = Settings.get_value('image_list')[Settings.get_value('image_index')][1].filename

        captcha_name: str = re.findall(r'.+\/(.+)\.', image_path)[0]

        Settings.get_value('current_captcha_name').config(text=captcha_name)

    @staticmethod
    def switch_captcha_image(direction: int = 1, event=None):
        try:
            image: ImageTk = Settings.get_value('image_list')[Settings.get_value('image_index')+direction][0]
            Settings.get_value('current_captcha_image').destroy()
            Settings.set_value('current_captcha_image', Label(image=image))
            Settings.get_value('current_captcha_image').place(relx=0.5, rely=0.5, anchor='center')

            if Settings.get_value('image_index') > 0 or direction == 1:
                Settings.set_value('image_index', Settings.get_value('image_index') + direction)

            Settings.get_value('update_captcha_image_method')()
        except IndexError:
            pass
