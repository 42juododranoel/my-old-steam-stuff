import time
import hmac
import struct
from hashlib import sha1
from base64 import b64decode


def generate_one_time_code(shared_secret):
    b64_shared_secret = b64decode(shared_secret)

    time_buffer = struct.pack('>Q', int(time.time()) // 30)
    time_hmac = hmac.new(
        b64_shared_secret,
        time_buffer,
        digestmod=sha1
    )
    digest = time_hmac.digest()

    begin = ord(digest[19:20]) & 0xf
    full_code = struct.unpack('>I', digest[begin:begin + 4])[0] & 0x7fffffff
    chars = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for _ in range(5):
        full_code, i = divmod(full_code, len(chars))
        code += chars[i]

    return code
