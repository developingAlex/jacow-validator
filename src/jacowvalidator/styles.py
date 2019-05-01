

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
