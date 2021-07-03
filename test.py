import shelve

with shelve.open('cache/settings') as settings:
    for k, v in settings.items():
        print(k, v)
