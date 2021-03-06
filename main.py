from selenium.webdriver import Chrome, ChromeOptions
from lxml import html
from bs4 import BeautifulSoup
from traceback import format_exc


def option_adding_xpath_helper():
    options = ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_extension(r"chrome_extension_xpath_helper.crx")
    return options


def _main():
    c = Chrome(chrome_options=option_adding_xpath_helper())
    element_candidates = []
    while True:
        func = _recv_commands()
        element_candidates = func(c, element_candidates)


def get_url(c, element_candidates):
    print("input url:")
    url = input()
    try:
        c.get(url)
    except (Exception, ) as e:
        print(e)
    return element_candidates


def reset_filtering(c, element_candidates):
    element_candidates.clear()
    return element_candidates


def _sort_elements(elements):
    elements.sort(key=lambda x: x.treepath, reverse=False)
    return elements


def _xpath_func(c, xpath_):
    lxml_elements = html.fromstring(c.page_source).xpath(xpath_)
    paths = [le.getroottree().getpath(le) for le in lxml_elements]
    raw_elements = []
    for path in paths:
        e = c.find_element_by_xpath(path)
        e.treepath = path
        raw_elements.append(e)
    return raw_elements


def filter_by_xpath(c, element_candidates):
    print("input xpath:")
    xpath_ = input()
    raw_elements = _xpath_func(c, xpath_)
    print(f"xpath found {len(raw_elements)} elements")
    common_elements = _exact_common(raw_elements, element_candidates)
    common_elements = _sort_elements(common_elements)
    return common_elements


def _exact_common(raw_elements, element_candidates):
    raw_element_ids = list(map(lambda x: x.id, raw_elements))
    element_candidate_ids = list(map(lambda x: x.id, element_candidates))
    if len(element_candidate_ids) > 0:
        common_ids = set(raw_element_ids) & set(element_candidate_ids)
    else:
        common_ids = set(raw_element_ids)
    common_elements = [e for e in raw_elements if e.id in common_ids]
    return common_elements


def show_elements(c, element_candidates):
    print(f"there are {len(element_candidates)} elements.")
    for i,  element in enumerate(element_candidates):
        path = element.treepath
        print(
            f"{i}, {element.tag_name}, len:{len(element.get_attribute('outerHTML'))}, {path}")
    return element_candidates


def eval_mode(c, element_candidates):
    print("interface mode. 'c' is Chrome.")
    command = input()
    try:
        eval(command)
    except (Exception, ) as e:
        print(format_exc())
    return element_candidates


def print_outerHTML(c, element_candidates):
    print(f"input number (which command '{show_elements.__name__}' tell you):")
    number = input()
    try:
        element = element_candidates[int(number)]
    except (IndexError, ) as e:
        print(e)
        print("len(element_candidates) = {len(element_candidates)}")
    except (Exception, ) as e:
        print(e)
    else:
        _show_an_element_detail_print_func(element)
    finally:
        return element_candidates


def _show_an_element_detail_print_func(element):
    outerHTML = element.get_attribute("outerHTML")
    soup = BeautifulSoup(outerHTML, "lxml")
    print(element.tag_name)
    print(element.treepath)
    print(soup.prettify())


def _recv_commands():
    funcs = [get_url, filter_by_xpath, show_elements,
             print_outerHTML, reset_filtering, eval_mode]
    names = [_insert_bracket(f.__name__) for f in funcs]
    dict_input_to_names = {
        name[1: 4]:  func for name, func in zip(names, funcs)}
    while True:
        print(f'commands:{names}')
        input_ = input()
        if input_ in dict_input_to_names:
            func = dict_input_to_names[input_]
            return func
        else:
            print(f"input:{[input_, ]} don't mt anything")


def _insert_bracket(str_): return f'({str_[:3]}){str_[3:]}'


if __name__ == '__main__':
    _main()
