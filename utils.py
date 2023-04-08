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


def markdown_to_bbcode(text):
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\g<1>[/b]', text)
    # Italics
    text = re.sub(r'_(.+?)_', r'[i]\g<1>[/i]', text)
    # Headers
    for i in range(1, 4):
        text = re.sub(f'^{"#" * i} (.+?)$', f'[size={5 - i}]\g<1>[/size]', text, flags=re.MULTILINE)
    # Links
    text = re.sub(r'\[(.+?)]\((.+?)\)', r'[url=\g<2>]\g<1>[/url]', text)
    # Images
    text = re.sub(r'!\[(.+?)]\((.+?)\)', r'[img]\g<2>[/img]', text)
    # Lists
    text = re.sub(r'^\* (.+?)$', r'[*]\g<1>', text, flags=re.MULTILINE)
    # Blockquotes
    text = re.sub(r'^> (.+?)$', r'[quote]\g<1>[/quote]', text, flags=re.MULTILINE)
    return text


def bing_in_text(text):
    return None if any(word in text for word in ["Bing", "bing"]) else text


def add_modifiers(text):
    if text is None:
        return
    out = text
    for m in [remove_reference_simbols, markdown_to_bbcode, add_period, bing_in_text]:
        out = m(out)
    return out


def cookie_swap(cookies, cookie_index):
    new_index = (cookie_index + 1) % len(cookies)
    save_conf("cookie_swap.conf", str(new_index))
    return cookies[new_index]
