def to_int(i, default=None):
    try:
        return int(i)
    except ValueError:
        return default