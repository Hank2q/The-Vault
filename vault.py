import sqlite3
import os
from cryptography.fernet import Fernet
import ezlog

vault_log = ezlog.MyLogger(
    name='vault_log', form='time:[level][function]: msg', file='logs/vault_log.log')


class Vault:
    KEY = b'f0e0HQdoUptcnOHYOjmhbjiYCYzPojVFSOhsoLwOMik='
    CRYPTER = Fernet(KEY)

    def __init__(self, name, encrypted=False):
        try:
            os.mkdir('temp')
            vault_log.info('making temporary folder')
        except FileExistsError:
            pass

        self.name = name
        self.db = sqlite3.connect(name)
        self.c = self.db.cursor()
        try:
            self.db.execute('''
            CREATE TABLE files (filename varchar(255) PRIMARY KEY NOT NULL UNIQUE, data TEXT)''')
            vault_log.info('creating database')
        except Exception:
            pass

        self.encrypted = encrypted

    def store(self, file):
        basename = os.path.basename(file)
        vault_log.debug(f'Attempting to add file: "{basename}" to the vault')
        with open(file, 'rb') as f:
            data = f.read() if not self.encrypted else self.encrypt(f.read())
        with self.db:
            self.c.execute("insert into files values (?, ?);",
                           (basename, data))
        os.remove(file)
        vault_log.debug(f'file: "{basename}" successfully added')

    def show_files(self):
        output = self.c.execute('select filename from files')
        vault_log.info('items listed')
        return [name[0]for name in output.fetchall()]

    def get(self, file):
        temp_items = os.listdir('temp')
        vault_log.debug(f'Attempting to get file: "{file}" from vault')
        if file in self.keys and file not in temp_items:
            vault_log.debug(f'file: "{file}" written to temp folder')
            result = self.c.execute(
                'SELECT * FROM files WHERE filename=?', (file,))
            filename, data = result.fetchone()
            if self.encrypted:
                data = self.decrypt(data)
            with open('temp/' + filename, 'wb') as unlock:
                unlock.write(data)
            os.popen(f'"temp/{file}"')
            vault_log.info(f'file: "{file}" ran successfully')
        else:
            vault_log.debug(
                f'file: "{file}" is not in database or is already in temporary view folder')

    def remove(self, file):
        vault_log.debug(f'attempting to delete file: "{file}" from the vault')
        if file in self.keys:
            result = self.c.execute(
                'SELECT * FROM files WHERE filename=?', (file,))
            filename, data = result.fetchone()
            if self.encrypted:
                data = self.decrypt(data)
            with self.db:
                self.c.execute(
                    'DELETE FROM files where filename=?', (filename,))
            self.vacuum()
            vault_log.debug(
                f'file: "{file}" was deleted from database')
            return filename, data

    def move_out(self, file, destination='.'):
        if file in self.keys:
            filename, data = self.remove(file)
            with open(f'{destination}/{filename}', 'wb') as moved:
                moved.write(data)
            vault_log.debug(
                f'file: "{file}" moved out of the vault to {destination}')

    def vacuum(self):
        with self.db:
            self.c.execute('VACUUM')
        vault_log.info('database extra size vacuumed')

    @staticmethod
    def encrypt(data):
        vault_log.info('data for file encrypted')
        return Vault.CRYPTER.encrypt(data)

    @staticmethod
    def decrypt(data):
        vault_log.info('data for file dencrypted')
        return Vault.CRYPTER.decrypt(data)

    @property
    def keys(self):
        output = self.c.execute('SELECT filename FROM files')
        vault_log.info('items listed')
        return [name[0] for name in output.fetchall()]

    @staticmethod
    def clean_up():
        vault_log.debug('cleaning up temporary')
        for file in os.listdir('temp'):
            os.remove('temp/' + file)
        vault_log.debug('temporary items successfully removed')
