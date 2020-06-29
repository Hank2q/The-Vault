import bcrypt
from shelve import open as sopen

with sopen('cache/settings') as s:
    pwd = s['password']

print(bcrypt.checkpw('hank'.encode(), pwd))