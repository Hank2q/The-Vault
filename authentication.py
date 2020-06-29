from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import winsound
from bcrypt import checkpw
from tkinter.simpledialog import askstring
from assets import EmailSender



class Authenticator(Tk):

    def __init__(self,email, password, both):
        super().__init__() 
        self.correct = False
        self.email = email
        self.password = password
        self.both = both

        self.title('The Vault')
        self.geometry('500x300')
        self.iconbitmap('vicon.ico')
        self.resizable(False, False)



        img = ImageTk.PhotoImage(Image.open('vicon.ico'))
        img_lable = Label(self, image=img)
        img_lable.pack()

        self.pass_lbl = Label(self,font='3',  text="Please enter the vault password:")
        self.pass_lbl.pack(pady=10)

        self.invalid_lbl= Label(self)
        self.invalid_lbl.pack()

        pass_frame = Frame(self)
        pass_frame.pack(pady=13)

        self.pass_entry = ttk.Entry(pass_frame, show='●', width=50)
        self.pass_entry.pack()
        self.pass_entry.bind('<Return>', self.check_pass)
        self.pass_entry.focus_set()

        self.enter_button = ttk.Button(pass_frame, text='Enter', command=self.check_pass)
        self.enter_button.pack(pady=10)

        self.mainloop()

    def check_pass(self, _=None):

        if checkpw(self.pass_entry.get().encode(), self.password):
            self.invalid_lbl.config(text='')
            if self.both:
                self.activate_key_check()
            else:
                self.correct = True
                self.destroy()
        else:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            self.invalid_lbl.config(text='Invalid password, try again', foreground='red')

    def activate_key_check(self):
        self.pass_lbl.config(text='Please enter the vault key sent to your email')
        self.pass_entry.delete(0, END)
        self.pass_entry.config(show='')
        self.pass_entry.bind('<Return>', lambda : self.check_key())
        self.enter_button.config(command=lambda: self.check_key())
        self.key = EmailSender.two_step(self.email)

    def check_key(self, _=None):
        entered_key = self.pass_entry.get()
        if entered_key == self.key:
            self.invalid_lbl.config(text='')
            self.correct = True
            self.destroy()
        else:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            self.invalid_lbl.config(text='Invalid Key, enter correct key', foreground='red')
