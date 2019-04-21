# temp solution to saving table and figure
save_text = [
    {'text': 'Table ', 'replace': '******'},
    {'text': 'Figure ', 'replace': '@@@@@@'},
    {'text': 'Fig ', 'replace': '######'},
    {'text': 'Fig.', 'replace': '&&&&&&'},
    {'text': 'References', 'replace': '!!!!!!'},
    {'text': 'Abstract', 'replace': '^^^^^^'},
]


# at the moment, this will replace character formatting within the paragraph
def replace_identifying_text(doc, filename):
    for paragraph in doc.paragraphs:
        # leave headings so can still see abstract and reference sections
        if paragraph.style.name not in [
            'JACoW_Abstract_Heading',
            'JACoW_Section Heading',
            'JACoW_Subsection Heading',
            'J_Section Heading',
            'J_Abstract Title',
        ]:
            replace_paragraph_text(paragraph)

    doc.save(filename)


# replace text using same case
def replace_paragraph_text(paragraph):
    p_all_caps = False
    if paragraph.style.font.all_caps or paragraph.style.base_style and paragraph.style.base_style.font.all_caps:
        p_all_caps = True

    for r in paragraph.runs:
        all_caps = p_all_caps or r.style.font.all_caps or r.font.all_caps
        r.text = replace_text(r.text, all_caps)


def replace_text(text, all_caps):
    for t in save_text:
        text = text.replace(t['text'], t['replace'])
    new_text = []

    for c in text:
        new_char = c
        if c.isalpha() and (all_caps or c.isupper()):
            new_char = 'A'
        elif c.islower():
            new_char = 'a'
        new_text.append(new_char)

    new_text = ''.join(new_text)
    for t in save_text:
        text = new_text.replace(t['replace'], t['text'])

    return text
