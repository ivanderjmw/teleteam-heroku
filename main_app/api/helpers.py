import hmac, hashlib

# from teleteam.settings import DJANGO_TELEGRAMBOT

from collections import OrderedDict

def generate_data_check_string(data):
    ordered_dict = OrderedDict(sorted(data.items()))
    to_concatenate = []
    for key, value in ordered_dict.items():
        if key is not 'hash':
            to_concatenate += [key + '=' + str(value)]
    data_check_string = '\n'.join(to_concatenate)
    
    return data_check_string

# TODO: Fix this function
def verify_login_data(data):
    print(data)
    data_check_string = generate_data_check_string(data).encode('ASCII')
    secret_key = hashlib.sha256("1160495867:AAF90CYdpZXg1bf7eWg8geqm4pYZqstepaY".encode('ASCII')).digest()
    signature = hmac.new(secret_key, data_check_string, hashlib.sha256).hexdigest()

    # return signature == data['hash']
    return True
