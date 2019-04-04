from docx import Document
from docx.shared import Inches, Mm
from pprint import pprint

import re
from glob import glob
from itertools import chain

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


# at least one style starts with JACoW
def check_jacow_styles(doc):
    return any([s.name.startswith('JACoW') for s in doc.styles])


def get_jacow_styles(doc):
    return [s.name for s in doc.styles if s.name.startswith('JACoW')]


def get_page_size(section):
    width = round(section.page_width, -4)
    if width == round(Mm(210), -4):
        return 'A4'
    elif width == round(Inches(8.5), -4):
        return 'Letter'
    else:
        raise Exception('Unknown Page Size')


def get_paragraph_style_exceptions(doc):
    jacow_styles = get_jacow_styles(doc)
    exceptions = []
    for i, p in enumerate(doc.paragraphs):
        if not p.text.strip() == '' and p.style.name not in jacow_styles and p.style.name not in OTHER_VALID_STYLES:
            exceptions.append(p)
    return exceptions


RE_REFS = re.compile(r'\[([\d ,-]+)\]')
RE_FIG_TITLES = re.compile(r'(^Figure \d+:)')
RE_FIG_INTEXT = re.compile(r'(Fig.\s?\d+|Figure\s?\d+\s+)')

def _ref_to_int(ref):
    try:
        return [int(ref), ]
    except ValueError:
        if '-' in ref:
            return list(range(*(int(v)+i for i, v in enumerate(ref.split('-')))))
        elif ',' in ref:
            return list(int(i) for i in ref.split(','))
        raise

def extract_references(doc):
    data = iter(doc.paragraphs)
    references_in_text = []

    # don't start looking until abstract header
    for p in data:
        if p.text.strip().lower() == 'abstract':
            break
    else:
        raise Exception('Abstract header not found')

    # find all references until references header
    for p in data:
        for ref in RE_REFS.findall(p.text):
            references_in_text.append(_ref_to_int(ref))
        if p.text.strip().lower() in ['references', 'reference']:
            break
    else:
        raise Exception('No reference list found at end of document')
    
    # find references at end of document
    references_list = []
    for p in data:
        for ref in RE_REFS.findall(p.text):
            references_list.append(dict(
                id=int(ref),
                text=p.text.strip(),
                style=p.style.name,
            ))

    # check refences in body are in correct order
    stack = [0, ]
    seen = []
    out_of_order = set()
    for _range in references_in_text:
        for _ref in _range:
            if _ref in stack:
                continue
            if _ref - stack[-1] == 1:
                stack.append(_ref)
            elif _ref not in seen:
                seen.append(_ref)
        for _ref in seen.copy():
            if _ref - stack[-1] == 1:
                stack.append(_ref)
                seen.remove(_ref)
        if len(seen) > 0:
            out_of_order.update(seen)

     # get a set of references so we know which ones are used
    used_references = set(chain.from_iterable(references_in_text))

    # check reference styles, order etc
    ref_count = len(references_list)
    for i, ref in enumerate(references_list, 1):
        ref['order_ok'] = i == ref['id'] and i not in out_of_order
        ref['used'] = i in used_references

        if ref_count <= 9:
            ref['style_ok'] = ref['style'] == 'JACoW_Reference when <= 9 Refs'
        else:
            if i <= 9:
                ref['style_ok'] = ref['style'] == 'JACoW_Reference #1-9 when >= 10 Refs'
            else:
                ref['style_ok'] = ref['style'] == 'JACoW_Reference #10 onwards'
    
    return references_in_text, references_list

# These are in the jacow templates so may be in docs created from them
# Caption and Normal for table title and figure title
# 'Body Text Indent' instead of 'JACoW_Body Text Indent' in a few places
# 'Heading 3' for Acronyms header
OTHER_VALID_STYLES = ['Body Text Indent', 'Normal', 'Caption', 'Heading 3']

