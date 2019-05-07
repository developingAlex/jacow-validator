from jacowvalidator.docutils.styles import check_style


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


def get_headings(doc):
    headings = []
    for i, p in enumerate(doc.paragraphs):
        # find matching style
        name = [name for name, h in HEADING_DETAILS.items() if p.style.name in [h['styles']['jacow'], h['styles']['normal']]]
        if name:
            style_ok, detail = check_style(p, HEADING_DETAILS[name[0]])
            heading_details = {
                'type': name[0],
                'style': p.style.name,
                'style_ok': style_ok,
                'text': p.text
            }
            heading_details.update(detail)
            headings.append(heading_details)

    return headings
