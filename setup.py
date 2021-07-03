import bcrypt
from shelve import open as sopen
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from assets import email_validator


class Setup(Tk):
    def __init__(self):
        super().__init__()
        self.title('The Vault')
        self.iconbitmap('vicon.ico')
        self.resizable(False, False)
        self.email = None
        self.password = None
        self.done = False
        img = ImageTk.PhotoImage(Image.open('vicon.ico'))
        img_lable = Label(self, image=img)
        img_lable.pack()

        self.setup_lbl = Label(
            self, font='3',  text="Vault setup:")
        self.setup_lbl.pack()

        self.invalid_lbl = Label(self)
        self.invalid_lbl.pack()

        info_frame = Frame(self)
        info_frame.pack()

        self.new_email = self.make_entry(self, 'Email:', focus=True)
        self.new_pass = self.make_entry(self, 'Password:', show='●')
        self.confirm_pass = self.make_entry(
            self, 'Confirm Password:', show='●')
        self.confirm_pass.bind('<Return>', self.setup_vault)

        self.enter_button = ttk.Button(
            self, text='Confirm', command=self.setup_vault)
        self.enter_button.pack(pady=10)

        self.mainloop()

    def setup_vault(self):
        email = self.new_email.get()
        password = self.new_pass.get()
        confirm_pass = self.confirm_pass.get()
        if not email or not password or not confirm_pass:
            self.invalid_lbl.config(
                text='Please provide all required fields', foreground='red')
            return
        if not email_validator(email):
            self.invalid_lbl.config(
                text='Please enter a valid email', foreground='red')
            return
        if password != confirm_pass:
            self.invalid_lbl.config(
                text='Password must match', foreground='red')
            return
        self.email = email
        self.password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt())
        with sopen('cache/settings') as settings:
            settings['password'] = self.password
            settings['email'] = email
            settings['factors'] = False
            settings['vault email'] = 'the.vaults.key@gmail.com'
            settings['vault email password'] = 'Vault123456'
        self.done = True
        self.destroy()

    def make_entry(self, master, label, show='', focus=False):
        frame = Frame(master)
        label = ttk.Label(frame, text=label)
        entry = ttk.Entry(frame, show=show, width=50)
        if focus:
            entry.focus_set()
        frame.pack(pady=5, padx=10)
        label.pack(anchor='w')
        entry.pack(anchor='w')
        return entry
