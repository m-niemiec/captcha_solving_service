import os
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog

from PIL import ImageTk, Image

root = Tk()

# Title of app
root.title("Captcha Renaming Tool")

# Size of the screen
screen_size = (700, 350)
root.geometry(f'{screen_size[0]}x{screen_size[1]}')

image_list = []


def get_folder_path():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)


def rename_image_file(event):
    print('rename_image_file')


def do_stuff():
    folder = folder_path.get()

    for image in os.listdir(folder):
        if image.endswith('jpeg'):
            image = Image.open(f'{folder}/{image}')
            tk_image = ImageTk.PhotoImage(image)
            image_list.append(tk_image)

    label = Label(image=image_list[0])
    label.grid(row=1, column=0, columnspan=3)
    label.place(relx=0.5, rely=0.5, anchor='center')

    captcha_solution = tk.Entry(root, textvariable=captcha_solution_text)
    captcha_solution.insert(0, '(type captcha solution here)')
    captcha_solution.grid(row=0, column=0)
    captcha_solution.place(relx=0.5, rely=0.8, anchor='center')

    captcha_solution.bind('<Return>', rename_image_file)
    # captcha_solution.pack()
    # res = tk.Label(root)
    # res.pack()


folder_path = StringVar()
captcha_solution_text = StringVar()

button_select_folder = ttk.Button(root, text='Select Folder', command=get_folder_path)
button_select_folder.grid(row=0, column=0)
c = ttk.Button(root, text='Load Captchas', command=do_stuff)
c.grid(row=0, column=2)

button_exit = Button(root, text="Exit", command=root.quit)

root.mainloop()
