
def has_name(tag):
    """
    This function check if the object has or not the name tag
    :param tag: the list of tags of an object
    :return:
    """
    return tag.key == 'name' or tag.key == 'name:en'


def get_name(tags):
    """

    :param tags:
    :return:
    """
    for tag in tags:
        if has_name(tag):
            return tag.value

    return False


def remove_tag_name(tags):
    return list(filter(lambda tg: not tg.key.startswith('name'), tags))


def print_tags(tags):
    for tag in tags:
        print(tag.key + ': ' + tag.value)
