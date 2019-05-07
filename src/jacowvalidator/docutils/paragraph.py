from jacowvalidator.docutils.styles import check_style


PARAGRAPH_DETAILS = {
    'styles': {
        'jacow': 'JACoW_Body Text Indent',
        'normal': 'Body Text Indent',
    },
    'font_size': 10.0,
    'space_before': ['>=', 3.0],
    'space_after': 3.0,
    'first_line_indent': 9.35
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
        if p.text.strip():
            # no need to check after references
            if p.text.lower() == 'references':
                break
            # ignore table and figure cations
            # TODO check if any real paragraphs start with figure or table
            if len(p.text) < 200 and \
                    (p.text.startswith('Table ') or p.text.startswith('Figure ') or p.text.startswith('Fig. ')):
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
