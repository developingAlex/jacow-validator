import re
from collections import OrderedDict
from itertools import chain

from docx.shared import Inches, Mm


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
        if (
            not p.text.strip() == ''
            and p.style.name not in jacow_styles
            and p.style.name not in OTHER_VALID_STYLES
        ):
            exceptions.append(p)
    return exceptions


RE_REFS_LIST = re.compile(r'^\[([\d]+)\]')
RE_REFS_INTEXT = re.compile(r'(?<!^)\[([\d ,-]+)\]')
RE_FIG_TITLES = re.compile(r'(^Figure \d+:)')
RE_FIG_INTEXT = re.compile(r'(Fig.\s?\d+|Figure\s?\d+\s+)')


def _ref_to_int(ref):
    try:
        return [int(ref)]
    except ValueError:
        if ',' in ref:
            return list(
                chain.from_iterable(_ref_to_int(i) for i in ref.split(',') if i.strip())
            )
        elif '-' in ref:
            return list(range(*(int(v) + i for i, v in enumerate(ref.split('-')))))
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

    # find all references in text and references list
    references_list = []
    for p in data:
        for ref in RE_REFS_INTEXT.findall(p.text):
            references_in_text.append(_ref_to_int(ref))

        for ref in RE_REFS_LIST.findall(p.text.strip()):
            references_list.append(
                dict(id=int(ref), text=p.text.strip(), style=p.style.name)
            )

    # check refences in body are in correct order
    stack = [0]
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


def _fig_to_int(s):
    return int(''.join(filter(str.isdigit, s)))


def extract_figures(doc):
    figures_refs = []
    figures_captions = []

    for p in doc.paragraphs:
        # find references to figures
        for f in RE_FIG_INTEXT.findall(p.text):
            figures_refs.append(dict(id=_fig_to_int(f), name=f.strip()))

        # find figure captions
        for f in RE_FIG_TITLES.findall(p.text.strip()):
            _id = _fig_to_int(f)
            figures_captions.append(
                dict(
                    id=_id,
                    name=f,
                    text=p.text.strip(),
                    style=p.style.name,
                    style_ok=p.style.name in ['Figure Caption', 'Caption Multi Line'],
                )
            )

    figures = OrderedDict()
    _last = max(
        chain.from_iterable(
            [
                (fig['id'] for fig in figures_captions),
                (fig['id'] for fig in figures_refs),
            ]
        )
    )

    for i in range(1, _last + 1):
        caption = [c for c in figures_captions if c['id'] == i]

        figures[i] = {
            'refs': list(f['name'] for f in figures_refs if f['id'] == i),
            'duplicate': len(caption) != 1,
            'found': len(caption) > 0,
        }
        figures[i]['used'] = len(figures[i]['refs']) > 0
        if caption:
            figures[i].update(**caption[0])

    return figures


# These are in the jacow templates so may be in docs created from them
# Caption and Normal for table title and figure title
# 'Body Text Indent' instead of 'JACoW_Body Text Indent' in a few places
# 'Heading 3' for Acronyms header
OTHER_VALID_STYLES = ['Body Text Indent', 'Normal', 'Caption', 'Heading 3']

