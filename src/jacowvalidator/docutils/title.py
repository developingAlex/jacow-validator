from jacowvalidator.docutils.styles import check_style


TITLE_DETAILS = {
    'styles': {
        'jacow': 'JACoW_Paper Title',
        'normal': 'Paper Title',
    },
    'alignment': 'CENTER',
    'font_size': 14.0,
    'space_before': 0.0,
    'space_after': 3.0,
    'bold': True,
    'italic': None,
}


def extract_title(doc):
    # find first not empty paragraph
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip():
            def get_text(r):
                return r.text.upper() if r.style.font.all_caps or r.font.all_caps else r.text

            title = ''.join([get_text(r) for r in p.runs])

            if p.style.font.all_caps or p.style.base_style and p.style.base_style.font.all_caps:
                title = title.upper()

            style_ok, detail = check_style(p, TITLE_DETAILS)
            title_detail = {
                'text': title,
                'style': p.style.name,
                'style_ok': style_ok,
                'case_ok': check_title_case(title),
            }
            title_detail.update(detail)
        return title_detail


def check_title_case(title):
    if title:
        return (sum(map(str.isupper, title)) / len(list(filter(str.isalpha, title)))) > 0.7
    else:
        return False
