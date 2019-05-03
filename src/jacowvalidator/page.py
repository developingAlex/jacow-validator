from docx.shared import Inches, Mm, Twips
from .authors import get_author_list

def get_page_size(section):
    width = round(section.page_width, -4)
    if width == round(Mm(210), -4):
        return 'A4'
    elif width == round(Inches(8.5), -4):
        return 'Letter'
    else:
        raise Exception('Unknown Page Size')


def get_paragraph_alignment(paragraph):
    # alignment style can be overridden by more local definition
    alignment = paragraph.style.paragraph_format.alignment
    if alignment is None and paragraph.style.base_style is not None:
        alignment = paragraph.style.base_style.paragraph_format.alignment

    if paragraph.alignment is not None:
        alignment = paragraph.alignment
    elif paragraph.paragraph_format.alignment is not None:
        alignment = paragraph.paragraph_format.alignment

    if alignment:
        return alignment._member_name
    else:
        return None


def get_paragraph_space(paragraph):
    # paragraph formatting style can be overridden by more local definition
    before, after = paragraph.style.paragraph_format.space_before, paragraph.style.paragraph_format.space_after
    if before is None and paragraph.style.base_style is not None:
        before = paragraph.style.base_style.paragraph_format.space_before
    if after is None and paragraph.style.base_style is not None:
        after = paragraph.style.base_style.paragraph_format.space_after

    if before:
        before = before.pt
    if after:
        after = after.pt

    return before, after


def get_style_font(paragraph):
    # use paragraph style if values set
    style = paragraph.style
    bold, italic, font_size, all_caps = style.font.bold, style.font.italic, style.font.size, style.font.all_caps
    if paragraph.style.base_style is not None:
        style = paragraph.style.base_style
        # if values not set, use base style
        if font_size is None:
            font_size = style.font.size
        if bold is None:
            bold = style.font.bold
        if italic is None:
            italic = style.font.italic
        if all_caps is None:
            all_caps = style.font.all_caps

    if font_size:
        font_size = font_size.pt

    return bold, italic, font_size, all_caps


def get_abstract_and_author(doc):
    abstract = {}

    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() == 'abstract':
            abstract = {
                'start': i,
                'text': p.text,
                'style': p.style.name,
                'style_ok': p.style.name in 'JACoW_Abstract_Heading',
            }
            break

    author_paragraphs = doc.paragraphs[1: abstract['start']]
    # TODO get set of values instead of just for first paragraph
    p = author_paragraphs[0]
    space_before, space_after = get_paragraph_space(p)
    bold, italic, font_size, all_caps = get_style_font(p)
    alignment = get_paragraph_alignment(p)

    text = ''.join(p.text for p in author_paragraphs)
    authors = {
        'text': text,
        'list': get_author_list(text),
        'style': set(p.style.name for p in author_paragraphs if p.text.strip()),
        'style_ok': all(
            p.style.name in ['JACoW_Author List']
            for p in author_paragraphs
            if p.text.strip()
        ),
        'alignment': alignment,
        'before': space_before,
        'after': space_after,
        'bold': bold,
        'italic': italic,
        'font_size': font_size,
        'all_caps': all_caps,
    }
    return abstract, authors


def convert_twips_to_cm(twips):
    width = Twips(int(twips))
    return round(width.mm / 10, 2)
