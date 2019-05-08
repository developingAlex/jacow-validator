from lxml.etree import _Element
from jacowvalidator.docutils.page import get_page_size, convert_twips_to_cm


def check_sections(doc):
    sections = []
    for i, section in enumerate(doc.sections):
        cols = get_columns(section)
        sections.append(
            {
                'page_size': get_page_size(section),
                'margins_ok': check_margins(section),
                'margins': get_margins(section),
                'col_number': cols[0],
                'col_gutter': cols[1],
                'col_ok': cols[2],
            }
        )
    return sections


def check_margins_A4(section):
    return get_margins_A4(section) == [37, 19, 20, 20]


def check_margins_letter(section):
    return get_margins_letter(section) == [0.75, 0.75, 0.79, 1.02]


def get_margins_A4(section):
    return [
        round(section.top_margin.mm),
        round(section.bottom_margin.mm),
        round(section.left_margin.mm),
        round(section.right_margin.mm),
    ]


def get_margins_letter(section):
    return [
        round(section.top_margin.inches, 2),
        round(section.bottom_margin.inches, 2),
        round(section.left_margin.inches, 2),
        round(section.right_margin.inches, 2),
    ]


def get_margins(section):
    page_size = get_page_size(section)
    if page_size == 'A4':
        return get_margins_A4(section)
    elif page_size == 'Letter':
        return get_margins_letter(section)


def check_margins(section):
    page_size = get_page_size(section)
    if page_size == 'A4':
        return check_margins_A4(section)
    elif page_size == 'Letter':
        return check_margins_letter(section)


def get_columns(section):
    num = 1
    space = 0
    ok = False
    for c1 in section._sectPr.iterchildren():
        if isinstance(c1, _Element) and 'cols' in str(c1):
            for c2 in c1.items():
                if 'num' in str(c2):
                    num = int(c2[1])
                if 'space' in str(c2):
                    space = convert_twips_to_cm(c2[1])
    if num == 1 or ( num == 2 and space == 0.51):
        ok = True
    return num, space, ok
