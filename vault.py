import shelve
import os, sys
import subprocess
import mimetypes
import ezlog

vault_log = ezlog.MyLogger(name='vault_log', form='[level] - [function]: msg', file='logs/vault_log.log')


def store(file):
    if os.path.isfile(file):
        basename = os.path.basename(file)
        vault_log.debug(f'attempting to add file: "{basename}" to the vault')
        with shelve.open('cache/the_vault') as db:
            db[basename] = {'name': basename, 'data': open(file, 'rb').read()}
        os.remove(file)
        vault_log.debug(f'file: "{basename}" successfully added')



def show_files():
    vault_log.info('items listed')
    
    with shelve.open('cache/the_vault') as db:
        files = [key for key in db.keys()]
    return files


def get(file):
    temp_items = os.listdir('temps')
    
    vault_log.debug(f'attempting to get file: "{file}" from vault')
    
    with shelve.open('cache/the_vault') as db:
        if file in db.keys():
            vault_log.debug(f'file: "{file}" in the vault')
            
            if file not in temp_items:

                vault_log.debug(f'file: "{file}" written to temp folder')
                
                with open('temps/'+ file, 'wb') as unlock:
                    unlock.write(db[file]['data'])
            else:
                vault_log.debug(f'file: "{file}" already in temporary view folder, was not written again')

            os.popen(f'"temps\\{file}"')
            vault_log.info(f'file: "{file}" ran successfully')



def clean_up():
    vault_log.debug('cleaning up temporary')
    
    for file in os.listdir('temps'):
        os.remove('temps/'+file)

    vault_log.debug('temporary items successfully removed')


def remove(file):
    vault_log.debug(f'attempting to delete file: "{file}" from the vault')
    
    with shelve.open('cache/the_vault') as db:
        if file in db.keys():
            file_data = db[file]['data']
            file_name = db[file]['name']
            
            del db[file]
            vault_log.info(f'file: "{file}" deleted successfully')
        else:
            vault_log.info(f'file: "{file}" not in the vault')

    return file_name, file_data

