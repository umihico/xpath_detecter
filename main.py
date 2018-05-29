from selenium.webdriver import Chrome, ChromeOptions


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


def _get_tree_location(element):
    path = element.tagname
    while True:
        parent = element.parent
        path = parent.tagname + '/' + path


def get_url(c, element_candidates):
    print("input url:")
    url = input()
    c.get(url)
    return element_candidates


def reset_filtering(c, element_candidates):
    element_candidates.clear()
    return element_candidates


def _sort_elements(elements):
    elements.sort(key=lambda x: _get_tree_location(x), reverse=False)
    return elements


def filter_by_xpath(c, element_candidates):
    print("input xpath:")
    xpath_ = input()
    try:
        raw_elements = c.find_elements_by_xpath(xpath_)
        print(f"xpath found {len(raw_elements)} elements")
    except (Exception, ) as e:
        print(e)
        return element_candidates
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
        path = _get_tree_location(element)
        print(f"{i}, {element.tagname}, len:{element}, {path}")
    return element_candidates


def show_an_element_detail(c, element_candidates):
    print(f"input number (which command '{show_elements.__name__}' tell you):")
    number = input()
    try:
        element = element_candidates[int(number)]
    except (Exception, ) as e:
        print(e)
    else:
        _show_an_element_detail_print_func(element)
    finally:
        return element_candidates


def _show_an_element_detail_print_func(element):
    print(element.tagname)
    print(_get_tree_location(element))
    print(element.get_attribute("outerHTML"))


def _recv_commands():
    funcs = [get_url, filter_by_xpath, show_elements, reset_filtering]
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
