import random
import string
import time
import uuid


def random_choice():
    return random.choice(string.ascii_letters + string.digits)


def random_sample():
    return ''.join(random.sample(string.ascii_lowercase + string.digits, 10))


def random_sample_length(length):
    if length <= 0:
        return ''
    return ''.join(random.sample(string.ascii_uppercase, length))


def item_code(key):
    lime = time.localtime()
    t = time.time()
    return time.strftime("%Y%m%d%H%M%S", lime) + '-' + str(int(t)) + '-' + str(key) + '-' + random_sample()


def system_code(key):
    return time.strftime("%Y%m%d%H%M%S", time.localtime()) + '-' + random_sample() + '#' + str(key)


def deal_code():
    return time.strftime("%Y%m%d%H%M%S", time.localtime()) + str(int(time.time())) + '-' + random_sample()


def sell_code():
    return item_code(1)


def sell_record_code():
    return item_code(3)


def buy_code():
    return item_code(2)


def buy_record_code():
    return item_code(4)


def machine_code():
    return system_code(1)


def uuid_key():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()))


def unique_key():
    temp = int(time.time())
    res = ''
    code = string.digits + string.ascii_uppercase
    if temp == 0:
        return '0'
    while temp > 0:
        res = res + code[int(temp % 36)]
        temp = int(temp / 36)
    length = 12 - len(res)
    res = res + random_sample_length(length=length)
    return res
