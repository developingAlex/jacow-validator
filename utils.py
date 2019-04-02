from docx import Document
from docx.shared import Inches, Mm
from pprint import pprint

import re
from glob import glob

def check_margins_A4(section):
    return all([
        int(section.top_margin.mm) == 37,
        int(section.bottom_margin.mm) == 19,
        int(section.left_margin.mm) == 20,
        int(section.right_margin.mm) == 20,
    ])

def check_margins_letter(section):
    return all([
        round(section.top_margin.inches, 2) == 0.75,
        round(section.bottom_margin.inches, 2) == 0.75,
        round(section.left_margin.inches, 2) == 0.79,
        round(section.right_margin.inches, 2) == 1.02,
    ])

def check_margins(section):
    page_size = get_page_size(section)
    if page_size == 'A4':
        return check_margins_A4(section)
    elif page_size == 'Letter':
        return check_margins_letter(section)

def check_jacow_styles(doc):
    return any([s.name.startswith('JACoW') for s in doc.styles])

def get_page_size(section):
    width = round(section.page_width, -4)
    if width == round(Mm(210), -4):
        return 'A4'
    elif width == round(Inches(8.5), -4):
        return 'Letter'
    else:
        raise Exception('Unknown Page Size')

RE_REFS = re.compile(r'\[([\d ,-]+)\]')
RE_FIG_TITLES = re.compile(r'(^Figure \d+:)')
RE_FIG_INTEXT = re.compile(r'(Fig.\s?\d+|Figure\s?\d+\s+)')

