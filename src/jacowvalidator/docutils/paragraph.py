from jacowvalidator.docutils.styles import check_style


PARAGRAPH_DETAILS = {
    'styles': {
        'jacow': 'JACoW_Body Text Indent',
        'normal': 'Body Text Indent',
    },
    'alignment': 'LEFT',
    'font_size': 10.0,
    'space_before': ['>=', 3.0],
    'space_after': 3.0,
    'bold': None,
    'italic': None,
    # 0.33cm indent firstline
}


def get_paragraphs(doc):
    data = iter(doc.paragraphs)
    paragraphs = []
    # don't start looking until abstract header
    for p in data:
        if p.text.strip().lower() == 'abstract':
            break

    for i, p in enumerate(data):
        # only for paraphaphs that are not references, figure captions, headings
        # name = [name for name, h in PARAGRAPH_DETAILS.items() if p.style.name in [h['styles']['jacow'], h['styles']['normal']]]
        #if name:
        if p.text.strip():
            # no need to check after references
            if p.text.lower() == 'references':
                break
            # ignore table and figure cations
            if p.text.startswith('Table ') or p.text.startswith('Figure '):
                continue
            # short paragraphs are probably headings
            if len(p.text) < 30:
                continue

            style_ok, detail = check_style(p, PARAGRAPH_DETAILS)
            paragraph_details = {
                'type': 'Paragraph',
                'style': p.style.name,
                'style_ok': style_ok,
                'text': p.text
            }
            paragraph_details.update(detail)
            paragraphs.append(paragraph_details)

    return paragraphs
