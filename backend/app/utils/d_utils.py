def list_from_list_of_lists(some_list: list):
    """
    List comp way for make_single_list
    """
    result = [item for sublist in some_list for item in sublist]
    return result


def make_single_list(list_of_list_of_ids) -> list:
    """
    from many database I get list of lists of dicts and I need to make it lists of dicts
    to represent info on front
    """
    result = []
    for list_of_ids in list_of_list_of_ids:
        for id in list_of_ids:
            result.append(id)
    return result


def get_lowest_base(items) -> int:
    """
    to decomposite load from one database we look on database that filled the lowest
    and send data to it
    """
    less_values_list = 0
    base_list_length = len(items[less_values_list])
    for i, values_list in enumerate(items):
        if len(values_list) < base_list_length:
            less_values_list = i
    return less_values_list


def get_first_missing_number(sequence, start=1):
    """
    for fill all empty numbers in base I need algorithm to
    find min missing number in some number list
    For example [1,2,4] returns 3
    [1,2,3,4] returns 5
    With that we can choose global id and set it to new person
    """
    uniques = set()
    maxitem = start - 1
    for e in sequence:
        if e >= start:
            uniques.add(e)
            if e > maxitem:
                maxitem = e
    return next(x for x in range(start, maxitem + 2) if x not in uniques)


if __name__ == "__main__":
    ...
