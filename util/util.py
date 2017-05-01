from decimal import Decimal


def has_name(tag):
    """
    This function check if the object has or not the name tag
    :param tag: the list of tags of an object
    :return:
    """
    return tag.key == 'name' or tag.key == 'name:en'


def get_name_shape(tags):
    """

    :param tags:
    :return:
    """
    shape = False
    name = False
    for tag in tags:
        if has_name(tag):
            name = tag.value
        if tag.key == 'area' and tag.value == 'yes':
            shape = 'AREA'

    return name, shape


def remove_tag_name(tags):
    return list(filter(lambda tg: not tg.key.startswith('name'), tags))


def print_tags(tags):
    for tag in tags:
        print(tag.key + ': ' + tag.value)


def split_array(sequence, precision=Decimal(0.1)):
    """
    
    :param sequence: 
    :param precision
    :return: 
    """
    digit = digits(precision)
    precision = float(precision)
    result = []
    for s in sequence:
        # We made a round for the limitations of float
        if not result or s != round(result[-1][-1] + precision, digit):
            result.append([])
        result[-1].append(s)

    return result


def digits(n):
    return max(0,-n.as_tuple().exponent)