import os
import tkinter as tk
import re
from functools import partial
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Style

from PIL import ImageTk, Image, ImageEnhance

from helper_texts import show_help_text

# TODO [6] Refactor
# TODO [7] Build both DMG and EXE standalone files


class CaptchaRenamingTool:
    folder_path = None
    captcha_solution_text = None
    root = None
    current_captcha_name = None
    current_captcha_image = None
    captcha_solution_entry = None
    renamed_total_images_amount = None
    total_images_amount = 0
    renamed_images_amount = -1
    image_index = 0
    image_list = []
    current_zoom = 1
    current_width = None
    current_height = None
    black_white_mode = False
    big_contrast_mode = False

    def __init__(self):
        self.root = Tk()

        # Title of app
        self.root.title("Captcha Renaming Tool")
        self.root.iconbitmap('media/main_icon.ico')
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='media/main_icon.png'))

        # Size of the screen
        screen_size = (900, 300)
        self.root.geometry(f'{screen_size[0]}x{screen_size[1]}')

        self.captcha_solution_text = StringVar()
        self.current_captcha_name = StringVar()

        style = Style()

        style.configure('TButton', font=('calibri', 15))

        select_folder_icon = tk.PhotoImage(file='media/folder_icon.png').subsample(2, 2)
        select_folder_button = ttk.Button(self.root, text='Select Folder', command=self.get_folder_path,
                                          image=select_folder_icon, compound='left')
        select_folder_button.grid(row=0, column=0, padx=10, pady=10)

        show_help_icon = tk.PhotoImage(file='media/help_icon.png').subsample(2, 2)
        show_help_button = ttk.Button(self.root, text='Show Help', command=self.show_help,
                                      image=show_help_icon, compound='left')
        show_help_button.place(relx=0.5, rely=0.5, anchor='center')

        self.root.mainloop()

    def apply_modes(self):
        self.current_captcha_image.destroy()

        image = self.image_list[self.image_index][1]

        image = image.convert('L') if self.black_white_mode else image.convert('RGB')

        if self.big_contrast_mode:
            image = ImageEnhance.Contrast(image).enhance(2)
            image = ImageEnhance.Color(image).enhance(2)
        else:
            image = ImageEnhance.Contrast(image).enhance(1)
            image = ImageEnhance.Color(image).enhance(1)

        converted_image = ImageTk.PhotoImage(image)

        self.current_captcha_image = Label(image=converted_image)
        self.current_captcha_image.image = converted_image
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

    def get_folder_path(self):
        # Reset variables that this function sets if users would like to select another folder.
        self.total_images_amount = -1
        self.image_list = []
        try:
            self.current_captcha_image.destroy()
        except AttributeError:
            pass

        folder = filedialog.askdirectory()

        for image in os.listdir(folder):
            if image.lower().endswith(('jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png', 'gif', 'webp')):
                self.total_images_amount += 1

                image = Image.open(f'{folder}/{image}')
                tk_image = ImageTk.PhotoImage(image)

                self.image_list.append([tk_image, image])

        self.current_width = self.image_list[0][1].width
        self.current_height = self.image_list[0][1].height

        self.current_captcha_image = Label(image=self.image_list[self.image_index][0])
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        self.update_captcha_image()

        self.update_renamed_images_count()

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
        increase_image_size_button.grid(row=0, column=2)

        self.decrease_image_size_icon = tk.PhotoImage(file='media/zoomout_icon.png').subsample(2, 2)
        decrease_image_size_button = ttk.Button(self.root, text='Zoom OUT', command=partial(self.set_zoom, 'decrease'),
                                                image=self.decrease_image_size_icon, compound='left')
        decrease_image_size_button.grid(row=0, column=3)

        self.change_black_white_icon = tk.PhotoImage(file='media/blackandwhite_icon.png').subsample(2, 2)
        change_black_white_button = ttk.Button(self.root, text='B&W Mode', command=self.set_black_white_mode,
                                               image=self.change_black_white_icon, compound='left')
        change_black_white_button.grid(row=0, column=4)

        self.change_contrast_color_icon = tk.PhotoImage(file='media/increasedcolors_icon.png').subsample(2, 2)
        change_contrast_color_button = ttk.Button(self.root, text='Color&Contrast Mode', command=self.set_big_contrast_mode,
                                                  image=self.change_contrast_color_icon, compound='left')
        change_contrast_color_button.grid(row=0, column=5)

    def set_zoom(self, direction):
        if direction == 'increase' and self.current_zoom < 2:
            self.current_zoom += 0.25

        elif direction == 'decrease' and self.current_zoom > 0.5:
            self.current_zoom -= 0.25

        self.update_captcha_image()

    def set_black_white_mode(self):
        self.black_white_mode = False if self.black_white_mode else True

        self.update_captcha_image()

    def set_big_contrast_mode(self):
        self.big_contrast_mode = False if self.big_contrast_mode else True

        self.update_captcha_image()

    def update_captcha_image(self):
        image = self.image_list[self.image_index][1]

        resized_image = image.resize((int(self.current_width * self.current_zoom), int(self.current_height * self.current_zoom)))

        self.image_list[self.image_index][1] = resized_image
        self.image_list[self.image_index][1].filename = image.filename

        resized_image = ImageTk.PhotoImage(resized_image)

        self.current_captcha_image.destroy()
        self.current_captcha_image = Label(image=resized_image)
        self.current_captcha_image.image = resized_image
        self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

        self.apply_modes()

        self.update_image_label()

        self.update_captcha_solution_entry()

    def rename_image_file(self):
        old_image_path = self.image_list[self.image_index][1].filename
        image_directory = re.findall(r'(.+\/)', old_image_path)[0]
        image_extension = re.findall(r'(\.\w+)', old_image_path)[0]

        new_image_path = image_directory + self.captcha_solution_text.get() + image_extension

        os.rename(old_image_path, new_image_path)

        self.image_list[self.image_index][1].filename = new_image_path

        self.switch_captcha_image()

        self.update_captcha_solution_entry()

        self.update_renamed_images_count()

    def switch_captcha_image(self, direction=1, event=None):
        try:
            image = self.image_list[self.image_index+direction][0]
            self.current_captcha_image.destroy()
            self.current_captcha_image = Label(image=image)
            self.current_captcha_image.place(relx=0.5, rely=0.5, anchor='center')

            self.image_index += direction

            self.update_captcha_image()
        except IndexError:
            pass

    def update_image_label(self):
        image_path = self.image_list[self.image_index][1].filename

        captcha_name = re.findall(r'.+\/(.+)\.', image_path)[0]

        try:
            self.current_captcha_name.destroy()
        except AttributeError:
            pass

        self.current_captcha_name = Label(text=captcha_name, font=('calibri', 20))
        self.current_captcha_name.place(relx=0.5, rely=0.25, anchor='center')

    def update_renamed_images_count(self):
        try:
            self.renamed_total_images_amount.destroy()
        except AttributeError:
            pass

        if self.renamed_images_amount < self.total_images_amount:
            self.renamed_images_amount += 1
        else:
            messagebox.showinfo('Success!', 'You renamed all captcha images in folder!')

        self.renamed_total_images_amount = Label(text=f'Renamed {self.renamed_images_amount} '
                                                      f'images out of {self.total_images_amount}.')
        self.renamed_total_images_amount.place(relx=0.5, rely=0.9, anchor='center')

    def update_captcha_solution_entry(self):
        try:
            self.captcha_solution_entry.destroy()
        except AttributeError:
            pass

        self.captcha_solution_text = StringVar()

        self.captcha_solution_entry = tk.Entry(self.root, textvariable=self.captcha_solution_text)
        self.captcha_solution_entry.insert(0, '(type captcha solution here)')
        self.captcha_solution_entry.place(relx=0.5, rely=0.8, anchor='center')

        def _on_entry_click(event):
            if self.captcha_solution_entry.get() == '(type captcha solution here)':
                self.captcha_solution_entry.delete(0, 'end')
                self.captcha_solution_entry.insert(0, '')

        def _on_focusout(event):
            if self.captcha_solution_entry.get() == '':
                self.captcha_solution_entry.insert(0, '(type captcha solution here)')

        self.captcha_solution_entry.bind('<FocusIn>', _on_entry_click)
        self.captcha_solution_entry.bind('<FocusOut>', _on_focusout)
        self.captcha_solution_entry.bind('<Return>', self.rename_image_file)
        self.captcha_solution_entry.focus()

    @staticmethod
    def show_help():
        help_window = tk.Toplevel()

        label = tk.Label(help_window, text=show_help_text)
        label.pack(fill='x', padx=50, pady=50)

        button_close = ttk.Button(help_window, text="Close", command=help_window.destroy)
        button_close.pack(fill='x')


if __name__ == '__main__':
    CaptchaRenamingTool()
#
# def main():
#     root = tk.Tk()
#     app = CaptchaRenamingTool(root)
#     root.mainloop()
#
#
# if __name__ == '__main__':
#     main()
