from struct import unpack


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if self.is_logged_in:
            raise PermissionError('Login required')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def steam_id_to_account_id(steam_id):
    if isinstance(steam_id, str):
        steam_id = int(steam_id)
    account_id = unpack('>L', steam_id.to_bytes(8, byteorder='big')[4:])[0]
    return account_id


def get_text_between(text, begin, end):
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]
