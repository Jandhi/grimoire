import re


def camel_to_snake_case(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def trim_minecraft_label(string: str) -> str:
    return string.replace("minecraft:", "")
