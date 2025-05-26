from typing import List


def unique_list(items: List[str], error_message: str) -> List[str]:
    """
    Validates that all elements in the supplied list are unique. If duplicates
    exist, raises a ValueError with the provided error message and details about
    the duplicate elements. If all elements are unique, the original list is
    returned unchanged.

    :param items: The list of strings to be validated for uniqueness.
    :param error_message: The error message to be included in the exception if
        duplicate elements are found.
    :return: The original list if all elements are unique.
    :rtype: List[str]
    :raises ValueError: If duplicate elements are found in the `items` list.
    """
    if len(items) != len(set(items)):
        duplicates = {item for item in items if items.count(item) > 1}
        raise ValueError(f"{error_message}: {duplicates}")
    return items
