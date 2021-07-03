from tkinter import *
from tkinter import ttk, messagebox, BooleanVar
from shelve import open as sopen
import bcrypt
from assets import email_validator, EmailSender
from tkinter.simpledialog import askstring
from ezlog import MyLogger

log = MyLogger(name='settings_log',
               form='time:[level]: msg', file='logs/settings_log.log')


class EmailChanger(Frame):

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.old_email = self.controller.settings['email']

        self.size = '290x210'
        self.title = 'Change Email'

        self.message = Label(
            self, text=f'Current email:\n{self.old_email}', wraplength=220)
        self.message.pack(fill=X, padx=10, pady=10)

        self.error_message = Label(self, wraplength=220)
        self.error_message.pack(fill=X, padx=10)

        self.new_email = ttk.Entry(self, width=40)
        self.new_email.pack(pady=10)
        self.new_email.focus_set()
        self.new_email.bind('<Return>', self.change_email)

        self.bframe = ttk.Frame(self)
        self.bframe.pack(pady=10)
        self.submit = ttk.Button(
            self.bframe, text='Change', command=self.change_email)
        self.submit.pack(side=LEFT, padx=10)
        self.cancel = ttk.Button(
            self.bframe, text='Cancel', command=self.controller.back)
        self.cancel.pack(side=LEFT, padx=10)

    def change_email(self, _=None):
        self.updated_email = self.new_email.get()
        full = len(self.updated_email)
        if not full:
            self.error_message.config(
                text='Please enter a new email', foreground='red')
            return
        if self.updated_email == self.old_email:
            self.error_message.config(
                text='New email cant be the same as old email', foreground='red')
            return

        if not email_validator(self.updated_email):
            self.error_message.config(
                text='Please enter a valid email address', foreground='red')
            return

        log.debug(
            f'Attempt to change vault email\nfrom: "{self.old_email}"\nto: "{self.updated_email}"')
        self.sent_key = EmailSender.email_change_sender(self.updated_email)
        self.activate_key_checker()

    def key_checker(self, _=None):
        entered_key = self.new_email.get()
        if entered_key == self.sent_key:
            self.controller.settings['email'] = self.updated_email
            log.info(f'vault email changed to: "{self.updated_email}"')
            self.controller.back()
            messagebox.showinfo(
                title='Email Changed', message=f'Email has been successfully changed to:\n{self.updated_email}')
        else:
            self.error_message.config(
                text=f'Invalid key, enter correct key sent to {self.updated_email}', foreground='red')

    def activate_key_checker(self):
        self.error_message.config(
            text=f'Enter the key that was sent to the new email: {self.updated_email}', foreground='black')
        self.new_email.delete(0, END)
        self.new_email.bind('<Return>', self.key_checker)
        self.submit.config(text='Enter', command=self.key_checker)


class PasswordChanger(Frame):

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.config(padx=13)
        self.size = '290x210'
        self.title = 'Change Password'
        self.message = Label(self, wraplength=240)
        self.message.pack(fill=X, padx=10)

        old_frame = Frame(self)
        old_frame.pack(fill=X, pady=5, padx=10)
        old_text = ttk.Label(old_frame, text='Enter old password:')
        old_text.pack(anchor='w')
        self.old_password = ttk.Entry(old_frame, show='●', width=40)
        self.old_password.pack(anchor='w', pady=5)
        self.old_password.bind('<Return>', self.change_password)
        self.old_password.focus_set()
        new_frame = Frame(self)
        new_frame.pack(fill=X, pady=10, padx=10)
        new_text = ttk.Label(new_frame, text='Enter new password:')
        new_text.pack(anchor='w')
        self.new_password = ttk.Entry(new_frame, show='●', width=40)
        self.new_password.pack(anchor='w', pady=5)
        self.new_password.bind('<Return>', self.change_password)

        submit_frame = Frame(self)
        submit_frame.pack()
        submit_button = ttk.Button(
            submit_frame, text='Change', command=self.change_password)
        submit_button.pack(side=LEFT, padx=10)
        cancel = ttk.Button(submit_frame, text='Cancel',
                            command=self.controller.back)
        cancel.pack(side=LEFT, padx=10)

    def change_password(self, _=None):
        log.debug('Attempting to change vault password')
        checked = True
        old_password = self.controller.settings['password']

        old_entered = self.old_password.get().encode()
        new_password = self.new_password.get().encode()

        old_empty = self.old_password.index(END)
        new_empty = self.new_password.index(END)

        if old_empty == 0 and new_empty == 0:
            self.message.config(
                text='Please enter your old and new passwords', foreground='red')
            return
        elif not bcrypt.checkpw(old_entered, old_password):
            self.message.config(
                text='Old password does not match, please enter the correct password', foreground='red')
            return
        elif old_empty == 0:
            self.message.config(
                text='Please enter your old password', foreground='red')
            return
        elif new_empty == 0:
            self.message.config(
                text='Please enter your new password', foreground='red')
            return
        else:
            pass

        if bcrypt.checkpw(new_password, old_password):
            self.message.config(
                text='Old and new passwords cannot be the same, please enter a different new password', foreground='red')
            checked = False

        if checked:
            self.controller.settings['password'] = bcrypt.hashpw(
                new_password, bcrypt.gensalt())
            log.info('Vault password was changed')
            self.controller.back()
            messagebox.showinfo('Password changed',
                                'Password successfully changed')


class Options(Frame):

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.size = '290x210'
        self.title = 'Settings'

        repass = Button(self, text='Reset Password'+' '*21, command=lambda: self.controller.show_window(
            PasswordChanger), pady=13, bd=3, relief='groove', font='TkDefaultFont 15')
        repass.grid(row=0, column=0, sticky='w', pady=2)

        reemail = Button(self, text='Reset Email'+' '*27, command=lambda: self.controller.show_window(
            EmailChanger), pady=13, bd=3, relief='groove', font='TkDefaultFont 15')
        reemail.grid(row=1, column=0, sticky='w', pady=2)

        condition = '☑'if self.controller.settings['factors'] else '❎'

        self.two_factor = Button(self, text='2-Step verification '+' '*13 + condition,
                                 command=self.two_step_change, bd=3, pady=13, font='TkDefaultFont 15', relief='groove')

        self.two_factor.grid(row=2, column=0, sticky='w', pady=2)

    def two_step_change(self):
        self.controller.settings['factors'] = not self.controller.settings['factors']
        condition = ("ON", '☑') if self.controller.settings['factors'] else (
            'OFF', '❎')
        log.debug(f'2-Step verification was set {condition[0]}')
        self.two_factor.config(
            text='2-Step verification '+' '*13 + condition[1])


class MainWindow(Toplevel):

    def __init__(self, master=None):
        self.settings = sopen('cache/settings')
        super().__init__(master)
        self.title('Settings')
        self.iconbitmap('sicon.ico')
        self.resizable(False, False)

        container = Frame(self)
        container.pack(fill=BOTH)

        self.frames = {}
        for F in (Options, PasswordChanger, EmailChanger):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='news')

        self.show_window(Options)

        self.grab_set()
        self.mainloop()
        self.settings.close()

    def show_window(self, k):
        frame = self.frames[k]
        self.geometry(frame.size)
        self.title(frame.title)
        frame.tkraise()

    def back(self):
        self.show_window(Options)
