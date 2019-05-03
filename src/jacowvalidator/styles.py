

VALID_STYLES = ['JACoW_Abstract_Heading',
                'JACoW_Author List',
                'JACoW_Body Text Indent',
                'JACoW_Bulleted List',
                'JACoW_Numbered list',
                'JACoW_Paper Title',
                'JACoW_Reference #10 onwards',
                'JACoW_Reference #1-9 when >= 10 Refs',
                'JACoW_Reference when <= 9 Refs',
                'JACoW_Reference Italics',
                'JACoW_Reference url_doi',
                'JACoW_Third-level Heading',
                'JACoW_Section Heading',
                'JACoW_Subsection Heading']

# These are in the jacow templates so may be in docs created from them
# Caption and Normal for table title and figure title
# 'Body Text Indent' instead of 'JACoW_Body Text Indent' in a few places
# 'Heading 3' for Acronyms header
OTHER_VALID_STYLES = ['Body Text Indent', 'Normal', 'Caption', 'Heading 3']


# check if th
def check_jacow_styles(doc):
    result = {}
    jacow_styles = get_jacow_styles(doc)

    for valid_style in VALID_STYLES:
        result[valid_style] = valid_style in jacow_styles

    return result


def get_jacow_styles(doc):
    return [s.name for s in doc.styles if s.name.startswith('JACoW')]


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


def get_paragraph_alignment(paragraph):
    # alignment style can be overridden by more local definition
    alignment = paragraph.style.paragraph_format.alignment
    if alignment is None and paragraph.style.base_style is not None and \
            paragraph.style.base_style.paragraph_format.alignment is not None:
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

    if paragraph.paragraph_format.space_before is not None:
        before = paragraph.paragraph_format.space_before
    if paragraph.paragraph_format.space_after is not None:
        after = paragraph.paragraph_format.space_after

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

    # TODO get distinct list
    for r in paragraph.runs:
        if not r.text.strip():
            continue

        if r.font is not None:
            if r.font.size is not None:
                font_size = r.font.size
            if r.font.bold is not None:
                bold = r.font.bold
            if r.font.italic is not None:
                italic = r.font.italic
            if r.font.all_caps is not None:
                all_caps = r.font.all_caps
        if r.bold is not None:
            bold = r.bold
        if r.italic is not None:
            italic = r.italic

    if font_size:
        font_size = font_size.pt

    return bold, italic, font_size, all_caps


def get_style_details(p):
    space_before, space_after = get_paragraph_space(p)
    bold, italic, font_size, all_caps = get_style_font(p)
    alignment = get_paragraph_alignment(p)
    return locals()


def check_style(p, compare):
    detail = get_style_details(p)

    if p.style.name in compare['styles']['jacow']:
        # TODO have different rules here
        style_ok = all([
            detail['space_before'] == compare['space_before'] or (detail['space_before'] is None and compare['space_before'] == 0.0),
            detail['space_after'] == compare['space_after']or (detail['space_after'] is None and compare['space_after'] == 0.0),
            detail['bold'] == compare['bold'],
            detail['italic'] == compare['italic'],
            detail['font_size'] == compare['font_size'],
            detail['alignment'] == compare['alignment']
        ])
    else:
        style_ok = all([
            detail['space_before'] == compare['space_before'] or (detail['space_before'] is None and compare['space_before'] == 0.0),
            detail['space_after'] == compare['space_after']or (detail['space_after'] is None and compare['space_after'] == 0.0),
            detail['bold'] == compare['bold'],
            detail['italic'] == compare['italic'],
            detail['font_size'] == compare['font_size'],
            detail['alignment'] == compare['alignment']
        ])

    # add messages
    # TODO optimise this
    if not (detail['space_before'] == compare['space_before'] or (detail['space_before'] is None and compare['space_before'] == 0.0)):
        detail['space_before'] = f"{detail['space_before']} should be {compare['space_before']}"
    if not (detail['space_after'] == compare['space_after'] or (detail['space_after'] is None and compare['space_after'] == 0.0)):
        detail['space_after'] = f"{detail['space_after']} should be {compare['space_after']}"
    if not detail['bold'] == compare['bold']:
        detail['bold'] = f"{detail['bold']} should be {compare['bold']}"
    if not detail['italic'] == compare['italic']:
        detail['italic'] = f"{detail['italic']} should be {compare['italic']}"
    if not detail['font_size'] == compare['font_size']:
        detail['font_size'] = f"{detail['font_size']} should be {compare['font_size']}"
    if not detail['alignment'] == compare['alignment']:
        detail['alignment'] = f"{detail['alignment']} should be {compare['alignment']}"

    return style_ok, detail
