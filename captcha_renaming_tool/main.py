import os
from tkinter import *
from tkinter import ttk, filedialog

from PIL import ImageTk, Image

root = Tk()

# Title of app
root.title("Captcha Renaming Tool")

# Size of the screen
root.geometry('700x350')

image_list = []


def get_folder_path():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)


def do_stuff():
    folder = folder_path.get()

    for image in os.listdir(folder):
        if image.endswith('jpeg'):
            image = Image.open(f'{folder}/{image}')
            tk_image = ImageTk.PhotoImage(image)
            image_list.append(tk_image)


folder_path = StringVar()
button_find_captchas = ttk.Button(root, text='Browse Folder', command=get_folder_path)
button_find_captchas.grid(row=0, column=2)
c = ttk.Button(root, text='Find Captchas', command=do_stuff)
c.grid(row=4, column=0)

button_exit = Button(root, text="Exit", command=root.quit)

root.mainloop()
