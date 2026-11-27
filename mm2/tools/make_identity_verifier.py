"""Generate only a salted scrypt verifier; identity inputs are not saved."""
import getpass
import hashlib
import secrets


def make_record(username, user_id):
    name = username.strip().lower()
    if not name or not user_id.isdecimal():
        raise ValueError("Enter a username and decimal numeric user ID.")
    key = (name + ":" + str(int(user_id))).encode("utf-8")
    salt = secrets.token_bytes(16)
    verifier = hashlib.scrypt(key, salt=salt, n=16384, r=8, p=1, dklen=32)
    return salt, verifier


def literal(value):
    return "string.char(" + ",".join(map(str, value)) + ")"


if __name__ == "__main__":
    salt, verifier = make_record(
        getpass.getpass("Protected username (hidden): "),
        getpass.getpass("Protected numeric user ID (hidden): "),
    )
    print("-- scrypt N=16384, r=8, p=1; 16 MiB work area. Keep runtime settings identical.")
    print("local salt = " + literal(salt))
    print("local verifier = " + literal(verifier))
