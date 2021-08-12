def scope_display(s: str):
    from .scope import v1

    result = []
    for this in sorted(list(set(s.split("-")))):
        if this in v1.keys():
            result.append(v1[this]['display'])

    return ", ".join(result)


filter_list = [name for name in dir() if not name.startswith("_")]
