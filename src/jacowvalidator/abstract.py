

def extract_abstract(doc):
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() == 'abstract':
            abstract = {
                'start': i,
                'text': p.text,
                'style': p.style.name,
                'style_ok': p.style.name in 'JACoW_Abstract_Heading',
            }

    author_paragraphs = doc.paragraphs[1: abstract['start']]
    authors = {
        'text': ''.join(p.text for p in author_paragraphs),
        'style': set(p.style.name for p in author_paragraphs if p.text.strip()),
        'style_ok': all(
            p.style.name in ['JACoW_Author List']
            for p in author_paragraphs
            if p.text.strip()
        ),
    }
    return abstract, authors