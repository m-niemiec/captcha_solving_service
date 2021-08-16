import tkinter as tk
from functools import partial
from tkinter import ttk
from tkinter.ttk import Style

from functional_view import AppFunctionalView
from helper_texts import show_help_text


class AppStartView:
    def __init__(self, root):
        self.root = root

        style = Style()
        style.theme_use('clam')

        style.theme_settings('clam', {
            'TButton': {
                'map': {
                    'background': [('active', '#4e4e4e'),
                                   ('!disabled', '#4e4e4e')]
                }
            }
        })

        style.configure('TButton', font=('calibri', 15), foreground='#D4d4d4', borderwidth='0', padx=10, pady=10)

        self.select_folder_icon = tk.PhotoImage(file='media/folder_icon.png').subsample(2, 2)
        select_folder_button = ttk.Button(self.root, text='Select Folder', command=partial(AppFunctionalView, self.root),
                                          image=self.select_folder_icon, compound='left')
        select_folder_button.grid(row=0, column=0, padx=10, pady=10)

        self.show_help_icon = tk.PhotoImage(file='media/help_icon.png').subsample(2, 2)
        show_help_button = ttk.Button(self.root, text='Show Help', command=self.show_help,
                                      image=self.show_help_icon, compound='left')
        show_help_button.place(relx=0.5, rely=0.5, anchor='center')

        self.root.mainloop()

    @staticmethod
    def show_help():
        help_window = tk.Toplevel(background='#313232')

        label = tk.Label(help_window, text=show_help_text, background='#313232', foreground='#D4d4d4',)
        label.pack(padx=50, pady=50)

        button_close = ttk.Button(help_window, text='Close', command=help_window.destroy)
        button_close.pack()


def main():
    root = tk.Tk()

    root.configure(background='#313232')
    root.title('Captcha Renaming Tool')
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='media/main_icon.png'))

    root.geometry('900x300')

    AppStartView(root)


if __name__ == '__main__':
    main()
