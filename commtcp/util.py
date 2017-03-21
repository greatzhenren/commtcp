import random
import string

letters = string.ascii_letters + string.digits


def makePassword(length):
    return ''.join([random.choice(letters) for _ in range(length)])
