import operator
from copy import copy
from deepdiff import DeepDiff
from functools import reduce


def _get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def _set_in_dict(data_dict, map_list, value):
    _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def get_update_with_ids(remote, local):
    result = copy(local)
    diff = DeepDiff(local, remote)

    for added_items in diff["dictionary_item_added"]:
        if "id" not in added_items:
            continue

        original_parts = added_items.split("[")
        cleaned_parts = []

        for p in original_parts[1:]:
            p = p.replace("]", "")
            p = p.replace("'", "")

            try:
                p = int(p)
            except ValueError:
                pass

            cleaned_parts.append(p)
        value = _get_from_dict(remote, cleaned_parts)
        _set_in_dict(result, cleaned_parts, value)

    return result
