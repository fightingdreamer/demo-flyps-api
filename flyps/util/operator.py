def itempathgetter(path: str):
    nodes = path.split(".")

    def getter(v: dict):
        for node in nodes:
            v = v[node]
        return v

    return getter
