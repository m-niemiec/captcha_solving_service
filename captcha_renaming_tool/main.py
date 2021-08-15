import tkinter as tk
from functools import partial
from tkinter import ttk
from tkinter.ttk import Style

from functional_view import AppFunctionalView
from helper_texts import show_help_text


class AppStartView:
    def __init__(self, root):
        self.root = root

        self.root.title("Captcha Renaming Tool")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='media/main_icon.png'))

        screen_size = (900, 300)
        self.root.geometry(f'{screen_size[0]}x{screen_size[1]}')

        style = Style()

        style.configure('TButton', font=('calibri', 15))

        select_folder_icon = tk.PhotoImage(file='media/folder_icon.png').subsample(2, 2)
        select_folder_button = ttk.Button(self.root, text='Select Folder', command=partial(AppFunctionalView, self.root),
                                          image=select_folder_icon, compound='left')
        select_folder_button.grid(row=0, column=0, padx=10, pady=10)

        show_help_icon = tk.PhotoImage(file='media/help_icon.png').subsample(2, 2)
        show_help_button = ttk.Button(self.root, text='Show Help', command=self.show_help,
                                      image=show_help_icon, compound='left')
        show_help_button.place(relx=0.5, rely=0.5, anchor='center')

        self.root.mainloop()

    @staticmethod
    def show_help():
        help_window = tk.Toplevel()

        label = tk.Label(help_window, text=show_help_text)
        label.pack(padx=50, pady=50)

        button_close = ttk.Button(help_window, text="Close", command=help_window.destroy)
        button_close.pack()


def main():
    root = tk.Tk()
    AppStartView(root)
    root.mainloop()


if __name__ == '__main__':
    main()
