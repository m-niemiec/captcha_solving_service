# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
    ('media/folder_icon.png', 'media'),
    ('media/help_icon.png', 'media'),
    ('media/increasedcolors_icon.png', 'media'),
    ('media/main_icon.ico', 'media'),
    ('media/blackandwhite_icon.png', 'media'),
    ('media/main_icon.png', 'media'),
    ('media/next_icon.png', 'media'),
    ('media/previous_icon.png', 'media'),
    ('media/zoomin_icon.png', 'media'),
    ('media/zoomout_icon.png', 'media')
]

a = Analysis(['main.py'],
             pathex=['C:\\Users\\micha\\Dysk Google\\Programming_Stuff\\Python_Projects\\captcha_solving_service\\captcha_renaming_tool'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             # win_no_prefbinaries_or_dataser_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='Captcha Renaming Tool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='media/main_icon.ico')
