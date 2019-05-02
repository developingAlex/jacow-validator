from .page import get_paragraph_alignment, get_paragraph_space, get_style_font


def extract_title(doc):
    p = doc.paragraphs[0]

    def get_text(r):
        return r.text.upper() if r.style.font.all_caps or r.font.all_caps else r.text

    title = ''.join([get_text(r) for r in p.runs])

    if p.style.font.all_caps or p.style.base_style and p.style.base_style.font.all_caps:
        title = title.upper()

    space_before, space_after = get_paragraph_space(p)
    bold, italic, font_size, all_caps = get_style_font(p)
    alignment = get_paragraph_alignment(p)

    return {
        'text': title,
        'style': p.style.name,
        'style_ok': p.style.name in ['JACoW_Paper Title'],
        'case_ok': check_title_case(title),
        'alignment': alignment,
        'before': space_before,
        'after': space_after,
        'bold': bold,
        'italic': italic,
        'font_size': font_size,
        'all_caps': all_caps,
    }


def check_title_case(title):
    return (sum(map(str.isupper, title)) / len(list(filter(str.isalpha, title)))) > 0.7
