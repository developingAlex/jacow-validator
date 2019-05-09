import re
from jacowvalidator.docutils.styles import check_style
from jacowvalidator.docutils.paragraph import PARAGRAPH_SIZE_MIN

HEADING_DETAILS = {
    'Section': {
        'styles': {
            'jacow': 'JACoW_Section Heading',
            'normal': 'Section Heading',
        },
        'alignment': 'CENTER',
        'font_size': 12.0,
        'space_before': 9.0,
        'space_after': 3.0,
        'bold': True,
        'italic': None,
        'case': 'uppercase',
    },
    'Subsection': {
        'styles': {
            'jacow': 'JACoW_Subsection Heading',
            'normal': 'Subsection Heading',
        },
        'alignment': None,
        'font_size': 12.0,
        'space_before': 6.0,
        'space_after': 3.0,
        'bold': None,
        'italic': True,
        'case': 'initialcaps',
    },
    'Third': {
        'styles': {
            'jacow': 'JACoW_Third - Level Heading',
            'normal': 'Third - Level Heading',
        },
        'alignment': None,
        'font_size': 10.0,
        'space_before': 6.0,
        'space_after': 0.0,
        'bold': True,
        'italic': None,
        'case': 'initialcaps',
    },
}


def guess_heading_type(p):
    #
    if p.style.name == 'Heading':
        return 'Section'
    if p.style.name == 'Heading 2':
        return 'Subsection'
    if p.style.name == 'Heading 3':
        return 'Third'
    else:
        return 'Section'


def get_headings(doc):
    data = iter(doc.paragraphs)
    headings = []
    # don't start looking until abstract header
    for p in data:
        if p.text.strip().lower() == 'abstract':
            break

    for i, p in enumerate(data):
        # no need to check after references
        if p.text.lower() == 'references':
            break

        # find matching style
        name = [name for name, h in HEADING_DETAILS.items() if p.style.name in [h['styles']['jacow'], h['styles']['normal']]]
        text = p.text.strip()
        text = re.sub(' +', ' ', text)

        if name:
            style_ok, detail = check_style(p, HEADING_DETAILS[name[0]])
            if detail['all_caps']:
                text = text.upper()

            heading_details = {
                'type': name[0],
                'style': p.style.name,
                'style_ok': style_ok,
                'text': p.text
            }
            heading_details.update(detail)
            headings.append(heading_details)
        elif 10 < len(text) < PARAGRAPH_SIZE_MIN:
            # TODO check if any real paragraphs start with figure or table
            if text.startswith('Table ') or text.startswith('Figure ') or text.startswith('Fig. '):
                continue

            name = guess_heading_type(p)
            style_ok, detail = check_style(p, HEADING_DETAILS[name])
            if detail['all_caps']:
                text = text.upper()

            final_style_ok = 2
            heading_details = {
                'type': name[0],
                'style': f"'{p.style.name}' checking against heading type: '{name}'",
                'style_ok': final_style_ok,
                'text': text
            }
            heading_details.update(detail)
            headings.append(heading_details)

    return headings
