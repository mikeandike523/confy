import os

def is_superuser():
    return os.getuid == 0