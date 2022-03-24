
import sha512_crypt


def check_token(func):

    def inner(a, b, c):
        print(f"Number {a}")
        func(a, b, c)
        print(f"End {b}")
    return inner


@check_token
def say(x: int, y: int, z: int):
    print(x+y-z)

password_hash = sha512_crypt.encrypt("123")
print(password_hash)
