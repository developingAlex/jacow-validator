import re
from collections import OrderedDict
from itertools import chain

from docx.shared import Inches, Mm
from docx.oxml.text.font import CT_RPr
from lxml.etree import _Element


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


def extract_title(doc):
    p = doc.paragraphs[0]

    def get_text(r):
        return r.text.upper() if r.style.font.all_caps or r.font.all_caps else r.text

    title = ''.join([get_text(r) for r in p.runs])

    if p.style.font.all_caps or p.style.base_style and p.style.base_style.font.all_caps:
        title = title.upper()

    return {
        'text': title,
        'style': p.style.name,
        'style_ok': p.style.name in ['JACoW_Paper Title'],
        'case_ok': check_title_case(title)
    }


def check_title_case(title):
    return (sum(map(str.isupper, title)) / len(list(filter(str.isalpha, title)))) > 0.7


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
RE_REFS_LIST_TAB = re.compile(r'^\[([\d]+)\]\t')
RE_REFS_INTEXT = re.compile(r'(?<!^)\[([\d ,-]+)\]')
RE_FIG_TITLES = re.compile(r'(^Figure \d+[.:])')
RE_FIG_INTEXT = re.compile(r'(Fig.\s?\d+|Figure\s?\d+[.\s]+)')


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
    ref_list_start = 0
    for i, p in enumerate(data):
        for ref in RE_REFS_INTEXT.findall(p.text):
            references_in_text.append(_ref_to_int(ref))

        refs = RE_REFS_LIST.findall(p.text.strip())
        if refs:
            for ref in refs:
                if int(ref) == 1:
                    ref_list_start = i
                references_list.append(
                    dict(id=int(ref), text=p.text.strip(), style=p.style.name)
                )
        elif ref_list_start > 0:
            should_find = references_list[-1]['id'] + 1
            if str(should_find) in p.text.strip()[:4]: # only look in first 4 chars
                references_list.append(
                    dict(id=should_find, text=p.text.strip(), style=p.style.name, text_error=f"Number format wrong should be [{should_find}]")
                )

    # check references in body are in correct order
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
    seen = set()
    for i, ref in enumerate(references_list, 1):
        if ref['id'] in seen:
            ref['duplicate'] = True
        seen.add(ref['id'])
        ref['order_ok'] = i == ref['id'] and i not in out_of_order
        ref['used'] = i in used_references

        if not RE_REFS_LIST_TAB.search(ref['text']):
            ref['text_error'] = f"Number format error should be [{i}] followed by a tab"

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

    def _find_figure_captions(p):
        for f in RE_FIG_TITLES.findall(p.text.strip()):
            _id = _fig_to_int(f)
            figures_captions.append(
                dict(
                    id=_id,
                    name=f,
                    text=p.text.strip(),
                    style=p.style.name,
                    style_ok=p.style.name in ['Figure Caption', 'Caption Multi Line', 'Caption'],
                )
            )

    for p in doc.paragraphs:
        # find references to figures
        for f in iter(f.strip() for f in RE_FIG_INTEXT.findall(p.text)):
            if f.endswith('.') and p.text.strip().startswith(f):
                # probably a figure caption with . instead of :
                continue
            figures_refs.append(dict(id=_fig_to_int(f), name=f))

        # find figure captions
        _find_figure_captions(p)

    # search for figure captions in tables
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    _find_figure_captions(p)

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
            'caption_ok': len(caption) == 1 and caption[0]['name'].endswith(':')
        }
        figures[i]['used'] = len(figures[i]['refs']) > 0
        if caption:
            figures[i].update(**caption[0])

    return figures


def get_abstract_and_author(doc):
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() == 'abstract':
            abstract = {
                'start': i,
                'text': p.text,
                'style': p.style.name,
                'style_ok': p.style.name in 'JACoW_Abstract_Heading',
            }

    author_paragraphs = doc.paragraphs[1: abstract['start']]
    authors = {
        'text': ''.join(p.text for p in author_paragraphs),
        'style': set(p.style.name for p in author_paragraphs if p.text.strip()),
        'style_ok': all(
            p.style.name in ['JACoW_Author List']
            for p in author_paragraphs
            if p.text.strip()
        ),
    }
    return abstract, authors


def get_paragraph_alignment(paragraph):
    # alignment style can be overridden by more local definition
    alignment = paragraph.style.paragraph_format.alignment
    if paragraph.alignment is not None:
        alignment = paragraph.alignment
    elif paragraph.paragraph_format.alignment is not None:
        alignment = paragraph.paragraph_format.alignment

    if alignment:
        return alignment._member_name
    else:
        return None


# simple unique list of languages
def get_language_tags(doc):
    tags = get_language_tags_location(doc)
    # get unique list
    return list(dict.fromkeys(tags.values()))


def get_language_tags_location(doc):
    tags = {}
    if doc.core_properties.language != '':
        tags['-1'] = doc.core_properties.language
    for i, p in enumerate(doc.paragraphs):
        for r in p.runs:
            for c in r.element.iterchildren():
                if isinstance(c, CT_RPr):
                    for cc in c.iterchildren():
                        if isinstance(cc, _Element) and 'lang' in str(cc):
                            tags[r.text] = cc.items()[0][1]
    # get unique list
    return tags


# These are in the jacow templates so may be in docs created from them
# Caption and Normal for table title and figure title
# 'Body Text Indent' instead of 'JACoW_Body Text Indent' in a few places
# 'Heading 3' for Acronyms header
OTHER_VALID_STYLES = ['Body Text Indent', 'Normal', 'Caption', 'Heading 3']
