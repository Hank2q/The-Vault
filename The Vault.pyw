from tkinter import *
from shelve import open as sopen
from tkinter import messagebox, filedialog, ttk
import os
import sys
from authentication import Authenticator
from settings import MainWindow as setting
from ezlog import MyLogger
from vault import Vault
from setup import Setup

log = MyLogger(name='GUI', form='time: msg', file='logs/gui.log', stream=False)
log.log_errors()

vault = Vault('data/the_vault', True)

with sopen('cache/settings') as s:
    try:
        pwd = s['password']
        email = s['email']
        twos = s['factors']
    except KeyError:
        new_vaules = Setup()
        if not new_vaules.done:
            sys.exit()
        pwd = new_vaules.password
        email = new_vaules.email
        twos = False

check = Authenticator(email, pwd, twos)
if not check.correct:
    sys.exit()


def store():
    file = filedialog.askopenfilename(
        filetypes=[('all files', '*.*')], multiple=True, parent=root)
    if file != '':
        if len(file) == 1:
            file = file[0]
            vault.store(file)
            files_box.insert(END, os.path.basename(file))
        else:
            for one in file:
                vault.store(one)
                files_box.insert(END, os.path.basename(one))


def ask(_):
    file = files_box.get(ANCHOR)
    vault.get(file)


def move_file(file):
    check = messagebox.askyesno(
        title='Move file', message=f'Do you want to move "{file}" out of the vault?')
    if check:
        new_place = filedialog.askdirectory()
        if new_place:
            vault.move_out(file, new_place)
            files_box.delete(ANCHOR)


def delete_file(file):
    check = messagebox.askyesno(
        'Delete file', f'Are you sure you want to permenantly delete "{file}"', icon=messagebox.WARNING)
    if check:
        vault.remove(file)
        files_box.delete(ANCHOR)


log.debug('GUI ran')
root = Tk()
root.title("The Vault")
root.geometry('700x515')
root.iconbitmap('vicon.ico')
root.resizable(False, False)

sframe = Frame(root)
sframe.pack(fill=X)

simage = PhotoImage(file='small.png')
settings_button = ttk.Button(sframe, image=simage, command=setting)
settings_button.pack(side=RIGHT, padx=10)


welcome = ttk.Label(root, text="Welocom to your vault", font='5')
welcome.pack()


files_frame = ttk.Frame(root)
files_frame.pack(fill=BOTH, pady=15, padx=10)


files_box = Listbox(files_frame, font='15', height=15, width=60)
for item in sorted(vault.keys):
    files_box.insert(END, item)
files_box.pack(fill=X, side=LEFT)
files_box.bind("<Double-Button-3>", ask)
files_box.bind("<Return>", ask)


files_scroll = ttk.Scrollbar(files_frame, command=files_box.yview)
files_box.config(yscrollcommand=files_scroll.set)
files_scroll.pack(fill=Y, side=LEFT)


buttons = Frame(root, relief='sunken')
buttons.pack(side=BOTTOM, fill=X, padx=10)
open_button = ttk.Button(buttons,  text='Open',
                         command=lambda: vault.get(files_box.get(ANCHOR)))
move_button = ttk.Button(buttons, text='Move',
                         command=lambda: move_file(files_box.get(ANCHOR)))
delete_button = ttk.Button(buttons, text='Delete',
                           command=lambda: delete_file(files_box.get(ANCHOR)))
open_button.pack(side=LEFT, pady=2)
move_button.pack(side=LEFT, pady=2)
delete_button.pack(side=LEFT, pady=2)
store_button = ttk.Button(buttons, text='Add File', command=store)
store_button.pack(pady=15, side=RIGHT)

root.mainloop()
log.debug('GUI terminated')
vault.clean_up()
