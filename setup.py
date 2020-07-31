import bcrypt
from shelve import open as sopen


with sopen('cache/settings') as s:
    password = input(
        'Enter New Password to be used for opening the vault >>> ')
    s['password'] = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    s['email'] = input(
        'Enter email address that the vault will contact you on >>> ')

    # the vault will send you emails using this email, have to set up the email in the setting script if its not gmail
    s['vault email'] = input(
        'Enter email that the vault will use to send emails')
    s['vault email password'] = input('Enter password for vault\'s email >>> ')
    for k in s.keys():
        print(k, s[k])
