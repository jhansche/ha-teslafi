def _is_state(src: str | None, expect: str) -> bool | None:
    return None if src is None else src == expect


def _is_state_in(src: str | None, expect: list[str]) -> bool | None:
    return None if src is None else src in expect


def _lower_or_none(src: str | None) -> str | None:
    return None if src is None else src.lower()


def _int_or_none(src: str | None) -> int | None:
    return None if src is None else int(float(src))


def _convert_to_bool(value: any) -> bool | None:
    """Convert the TeslaFi value to a boolean"""
    if value is bool:
        return value
    if value is None:
        return None
    if not value:
        return False
    # Otherwise it might be a non-falsey string that is actually false
    if value == "0":
        return False
    return bool(value)
