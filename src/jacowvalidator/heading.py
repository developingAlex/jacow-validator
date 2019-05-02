from .page import get_paragraph_alignment, get_paragraph_space, get_style_font

HEADING_DETAILS = {
    'Section': {
        'styles': {
            'jacow': 'JACoW_Section Heading',
            'normal': 'Section Heading',
        },
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
            detail = HEADING_DETAILS[name[0]]
            if p.style.name == detail['styles']['jacow']:
                style_ok = True
                space_before, space_after = get_paragraph_space(p)
                bold, italic, font_size, all_caps = get_style_font(p)
            else:
                # need to check if equivalent
                space_before, space_after = get_paragraph_space(p)
                bold, italic, font_size, all_caps = get_style_font(p)

                style_ok = all([
                    space_before == detail['space_before'],
                    space_after == detail['space_after'],
                    bold == detail['bold'],
                    italic == detail['italic'],
                    font_size == detail['font_size']
                ])

                # Add details if errors
                if not space_before == detail['space_before']:
                    space_before = f"{space_before} should be {detail['space_before']}"
                if not space_after == detail['space_after']:
                    space_after = f"{space_after} should be {detail['space_after']}"
                if not font_size == detail['font_size']:
                    font_size = f"{font_size} should be {detail['font_size']}"
                if not bold == detail['bold']:
                    bold = f"{bold} should be {detail['bold']}"
                if not italic == detail['italic']:
                    italic = f"{italic} should be {detail['italic']}"

            headings.append({
                'type': name[0],
                'style': p.style.name,
                'style_ok': style_ok,
                'text': p.text,
                'alignment': get_paragraph_alignment(p),
                'before': space_before,
                'after': space_after,
                'bold': bold,
                'italic': italic,
                'font_size': font_size,
                'all_caps': all_caps,
            })

    return headings
