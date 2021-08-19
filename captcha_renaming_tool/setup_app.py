from setuptools import setup

APP = ['main.py']

DATA_FILES = [
    'media',
    'media/blackandwhite_icon.png',
    'media/folder_icon.png',
    'media/help_icon.png',
    'media/increasedcolors_icon.png',
    'media/main_icon.png',
    'media/next_icon.png',
    'media/previous_icon.png',
    'media/zoomin_icon.png',
    'media/zoomout_icon.png',
]
OPTIONS = {
    'packages': ['PIL'],
    'iconfile': 'media/main_icon.png',
}

setup(
    app=APP,
    name='Captcha Renaming Tool',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
