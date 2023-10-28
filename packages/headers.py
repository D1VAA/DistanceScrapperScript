from random import randint


def randomHeader(func: object) -> object:
    """

    :rtype: object
    """

    def wrapper(*args, **kwargs):
        num = randint(1, 999)
        with open('./packages/headers.txt', 'r') as f:
            lines = f.readlines()
            text = lines[num].replace('\n', ' ').replace('\r', '')
            kwargs['headers'] = {'User-Agent': f'{text}'}
            return func(*args, **kwargs)

    return wrapper


def randomHeaderList(size=10) -> list:
    headers = list();
    list_length = [randint(1, 999) for _ in range(size)]
    with open('./packages/headers.txt', 'r') as f:
        lines = f.readlines()
        template = {'User-Agent': str(lines[i].replace('\n', '').replace('\r', '')) for i in list_length}
        headers.append(template)
    return headers
