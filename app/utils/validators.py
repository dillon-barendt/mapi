from typing import List


def unique_list(items: List[str], error_message: str) -> List[str]:
    if len(items) != len(set(items)):
        duplicates = {item for item in items if items.count(item) > 1}
        raise ValueError(f"{error_message}: {duplicates}")
    return items
