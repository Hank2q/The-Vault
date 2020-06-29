from string import digits, ascii_letters
from random import choices
import re, shelve, threading, smtplib
from email.message import EmailMessage


def key_generator():
    chars = digits+ascii_letters
    key = ''.join(choices(chars, k=5))
    return key


def email_validator(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$' 
    return re.search(regex,email)


class EmailSender:
    def __init__(self, to, subject, bk):
        self.to = to
        self.subject = subject
        self.msg = '\n'.join(bk)
        self.body , self.key = bk

        with shelve.open('cache/settings') as s:
            self.email = s['vault email']
            self.pwd = s['vault email password']

        thread = threading.Thread(target=self.send)
        thread.start()


    @staticmethod
    def generate_html(body, key):
        html = open('email_key.html').read()
        matches = {'KEYPLACE': key, 'BODYPLACE': body}

        regex = re.compile("(%s)" % "|".join(map(re.escape, matches.keys())))
        return regex.sub(lambda mo: matches[mo.string[mo.start():mo.end()]], html) 

    def send(self):

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as mail:
            mail.login(self.email, self.pwd)

            messege = EmailMessage()
            messege['To'] = self.to  # or a list or emails or a comma seperated string or emails
            messege['From'] = self.email
            messege['Subject'] = self.subject

            messege.set_content(self.msg)

            html = self.generate_html(self.body, self.key)
            messege.add_alternative(html, subtype='html')
            mail.send_message(messege)

    @classmethod
    def email_change_sender(cls, to):
        key = key_generator()
        body = 'This message is to confirm that this is your new vault email.\nPlease enter this key:\n'
        cls(to, 'Vault email change', (body, key))
        return key

    @classmethod
    def two_step(cls, to):
        key = key_generator()
        body = 'This is your vault entrance key:\n'
        cls(to, 'Vault Access Key', (body, key))
        return key
