import operator
import os


def cipher_string(
    text: str,
    initial_offset: int,
    jumps: int = 0,
    encrypt: bool = True,
) -> str:
    """
    Encrypts or decrypts a given string using a modified version
    of Caesar cipher algorithm, with a varying offset based on a "jumps" parameter.

    This way, the normal caesar cipher algorithm can't be used to decrypt the string.

    Args:
        text (str): The string to be encrypted/decrypted
        initial_offset (int): The initial offset used to shift each character in the string
        jumps (int, optional): The number of characters to shift the offset by. Defaults to 0.
        encrypt (bool, optional): Whether to encrypt or decrypt the string. Defaults to True.

    Returns:
        result (str): The encrypted/decrypted string
    """

    # Argument validation
    if isinstance(text, str) is False:
        raise TypeError("text must be a string")
    if isinstance(initial_offset, int) is False:
        raise TypeError("initial_offset must be an integer")
    if isinstance(jumps, int) is False:
        raise TypeError("jumps must be an integer")

    result = ""
    offset = int(initial_offset)
    count = 0

    for char in text:
        count += 1
        choff = getattr(operator, "add" if encrypt else "sub")(ord(char), offset)

        if char.isupper():
            result += chr((choff - 65) % 26 + 65)
        elif char.islower():
            result += chr((choff - 97) % 26 + 97)
        else:
            result += char

        if jumps == 0:
            continue

        if count % int(jumps) == 0:
            offset = offset + 1 % 26
            count = 0

    return result


def decode_logged_keys(file: str, config: dict) -> str:
    """
    Decode a string of logged keys using the given configuration.

    Args:
        file (str): The file path to the logged keys
        config (dict): The configuration used to decode the string

    Returns:
    result (str): The decoded string
    """
    offset = config["offset"]
    jumps = config["jumps"]
    chars = config["chars"]
    delim = config["delim"]
    result = []

    if not os.path.exists(file):
        return "<File does not exist>"

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    # Loop through each session.
    # We use sessions to separate and reset the cipher offset.
    for session in text.split(delim):
        if len(session) == 0:
            continue
        chunks = [session[i : i + chars] for i in range(0, len(session), chars)]
        for chunk in chunks:
            result.append(cipher_string(chunk, offset, jumps, encrypt=False))
        result.append(" ")

    return "".join(result)
