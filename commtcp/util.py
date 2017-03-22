import random
import string

letters = string.ascii_letters + string.digits


def make_password(length):
    return ''.join([random.choice(letters) for _ in range(length)])
