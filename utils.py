import re


def load_conf(file):
    try:
        with open(file) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0"


def save_conf(file, data):
    with open(file, 'w') as f:
        f.write(data)


def get_not_answered(last_answered, list_of_posts):
    item_index = next((i for i, d in enumerate(list_of_posts) if d["id"] == last_answered), None)
    if item_index is None:
        return list_of_posts
    return list_of_posts[item_index + 1:]


def add_period(text):
    return text + '.' if not (text.endswith('.') or text.endswith('?')) else text


def remove_reference_simbols(text):
    return re.sub(r'\[[^]]*]', '', text)
