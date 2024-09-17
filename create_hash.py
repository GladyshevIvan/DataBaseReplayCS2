def make_hash(raw):
    hash = 0
    for char in raw:
        hash = (hash * 31 + ord(char)) % (2 ** 32)
    return hash


def set_game_id(raw_name, date):
    raw_hash = f'{str(raw_name)}-{date}'
    return make_hash(raw_hash)