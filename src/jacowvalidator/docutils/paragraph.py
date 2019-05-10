import re
from jacowvalidator.docutils.styles import check_style
from jacowvalidator.docutils.heading import HEADING_DETAILS

PARAGRAPH_DETAILS = {
    'styles': {
        'jacow': 'JACoW_Body Text Indent',
        'normal': 'Body Text Indent',
    },
    'alignment': 'JUSTIFY',
    'font_size': 10.0,
    'space_before': 0.0,
    'space_after': 0.0,
    'first_line_indent': 9.35  # 0.33cm
}

PARAGRAPH_SIZE_MIN = 50


def get_paragraphs(doc):
    data = iter(doc.paragraphs)
    paragraphs = []
    # don't start looking until abstract header
    for p in data:
        if p.text.strip().lower() == 'abstract':
            break

    for i, p in enumerate(data):
        # only for paraphaphs that are not references, figure captions, headings
        text = p.text.strip()
        text = re.sub(' +', ' ', text)

        if text:
            # no need to check after references
            if text.lower() == 'references':
                break

            # ignore table and figure cations
            # TODO check if any real paragraphs start with figure or table
            if text.startswith('Table ') or text.startswith('Figure ') or text.startswith('Fig. '):
                continue

            # ignore if heading style
            name = [name for name, h in HEADING_DETAILS.items() if
                        p.style.name in [h['styles']['jacow'], h['styles']['normal']]]

            if name:
                continue

            # short paragraphs are probably headings
            if len(text) < PARAGRAPH_SIZE_MIN:
                continue

            style_ok, detail = check_style(p, PARAGRAPH_DETAILS)
            if detail['all_caps']:
                text = text.upper()

            paragraph_details = {
                'type': 'Paragraph',
                'style': p.style.name,
                'style_ok': style_ok,
                'text': text
            }
            paragraph_details.update(detail)
            paragraphs.append(paragraph_details)

    return paragraphs
