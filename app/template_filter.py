def scope_display(s: str) -> str:
    from .scope import v1

    result = []
    for this in sorted(list(set(s.split("-")))):
        if this in v1.keys():
            result.append(v1[this]['display'])

    return ", ".join(result)


def user_agent_os(ua: str) -> str:
    from ua_parser.user_agent_parser import ParseOS

    def version(obj: list) -> str:
        result = ".".join([v for v in obj if v is not None])
        if len(result) == 0:
            return ""
        return f"({result})"

    uap = ParseOS(user_agent_string=ua)
    return f"{uap['family']} {version([uap['major'], uap['minor'], uap['patch'], uap['patch_minor']])}"


def user_agent_browser(ua: str) -> str:
    from ua_parser.user_agent_parser import ParseUserAgent

    def version(obj: list) -> str:
        result = ".".join([v for v in obj if v is not None])
        if len(result) == 0:
            return ""
        return f"({result})"

    uap = ParseUserAgent(user_agent_string=ua)
    return f"{uap['family']} {version([uap['major'], uap['minor'], uap['patch']])}"


filter_list = [name for name in dir() if not name.startswith("_")]
