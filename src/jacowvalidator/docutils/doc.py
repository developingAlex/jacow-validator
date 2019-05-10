from jacowvalidator.docutils.styles import check_style_detail, VALID_STYLES, VALID_NON_JACOW_STYLES
from jacowvalidator.docutils.page import get_text, check_title_case

DETAILS = {
    'Heading': {
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
    },
    'Paragraph': {
        'styles': {
            'jacow': 'JACoW_Body Text Indent',
            'normal': 'Body Text Indent',
        },
        'alignment': 'JUSTIFY',
        'font_size': 10.0,
        'space_before': ['>=', 3.0],
        'space_after': 3.0,
        'first_line_indent': 9.35  # 0.33cm
    },
    'Figure': {
        'SingleLine': {
            'styles': {
                'jacow': 'Figure Caption',
            },
            'alignment': 'CENTER',
            'font_size': 10.0,
            'space_before': 3.0,
            'space_after': ['>=', 3.0],
            'bold': None,
            'italic': None,
        },
        'MultiLine': {
            'styles': {
                'jacow': 'Figure Caption Multi Line',
            },
            'alignment': 'JUSTIFY',
            'font_size': 10.0,
            'space_before': 3.0,
            'space_after': ['>=', 3.0],
            'bold': None,
            'italic': None,
        }
    },
    'Reference': {
        'LessThanNineTotal': {
            'styles': {
                'jacow': 'JACoW_References when ≤ 9',
            },
            'alignment': 'JUSTIFY',
            'font_size': 9.0,
            'space_before': 0.0,
            'space_after': 3.0,
            'hanging_indent':  0.0,
            'first_line_indent': -14.75,  # 0.52 cm,
        },
        'LessThanNine': {
            'styles': {
                'jacow': 'JACoW_Reference #1-9 when >= 10 Refs',
            },
            'alignment': 'JUSTIFY',
            'font_size': 9.0,
            'space_before': 0.0,
            'space_after': 3.0,
            'hanging_indent': 0,  # 0.16 cm,
            'first_line_indent': -14.75,  # 0.52 cm,
        },
        'MoreThanNine': {
            'styles': {
                'jacow': 'JACoW_Reference #10 onwards',
            },
            'alignment': 'JUSTIFY',
            'font_size': 9.0,
            'space_before': 0.0,
            'space_after': 3.0,
            'hanging_indent':  0.0,
            'first_line_indent': -18.7,  # 0.68 cm,
        }
    },
    'Table': {
        'SingleLine': {
            'styles': {
                'jacow': 'Table Caption',
            },
            'alignment': 'CENTER',
            'font_size': 10.0,
            'space_before': ['>=', 3.0],
            'space_after': 3.0,
            'bold': None,
            'italic': None,
        },
        'MultiLine': {
            'styles': {
                'jacow': 'Table Caption Multi Line',
            },
            'alignment': 'JUSTIFY',
            'font_size': 10.0,
            'space_before': ['>=', 3.0],
            'space_after': 3.0,
            'bold': None,
            'italic': None,
        }
    },
    'Title': {
        'styles': {
            'jacow': 'JACoW_Paper Heading',
            'normal': 'Paper Heading',
        },
        'alignment': 'CENTER',
        'font_size': 14.0,
        'space_before': 0.0,
        'space_after': 3.0,
        'bold': True,
        'italic': None,
    },
    'Author': {
        'styles': {
            'jacow': 'JACoW_Author List',
            'normal': 'Author List',
        },
        'alignment': 'CENTER',
        'font_size': 12.0,
        'space_before': 9.0,
        'space_after': 12.0,
        'bold': None,
        'italic': None,
    },
    'Abstract': {
        'styles': {
            'jacow': 'JACoW_Abstract_Heading',
            'normal': 'Abstract_Heading',
        },
        'alignment': None,
        'font_size': 12.0,
        'space_before': 0.0,
        'space_after': 3.0,
        'bold': None,
        'italic': True,
    },
}


def get_title_details(p):
    title = get_text(p)
    title_detail = {
        'display_text': title,
        'case_ok': check_title_case(title, 0.7),
    }
    return title_detail


def get_author_details(p):
    superscript_removed_text = ''  # remove superscript footnotes
    for r in p.runs:
        superscript_removed_text += r.text if not r.font.superscript else ''
    author_detail = {
        'display_text': superscript_removed_text
    }
    return author_detail


def get_abstract_detail(p):
    abstract_detail = {
        'display_text': p.text,
    }
    return abstract_detail


def parse_all_paragraphs(doc):
    all_paragraphs = []
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip():
            style_ok = p.style.name in VALID_STYLES or p.style.name in VALID_NON_JACOW_STYLES
            if not style_ok:
                style_ok = 2
            all_paragraphs.append({
                'index': i,
                'style': p.style.name,
                'text': get_text(p),
                'style_ok': style_ok,
                'in_table': 'No'
            })

    # search for figure captions in tables
    for t in doc.tables:
        if len(t.rows) > 2:
            continue
        for r in t.rows:
            if len(r.cells) > 2:
                continue
            for c in r.cells:
                for p in c.paragraphs:
                    if p.text.strip():
                        style_ok = p.style.name in VALID_STYLES or p.style.name in VALID_NON_JACOW_STYLES
                        if not style_ok:
                            style_ok = 2
                        all_paragraphs.append({
                            'index': 0,
                            'style': p.style.name,
                            'text': get_text(p),
                            'style_ok': style_ok,
                            'in_table': 'Yes'
                        })

    return all_paragraphs


def parse_paragraphs(doc):
    abstract_index = reference_index = 0
    summary = {}
    for i, p in enumerate(doc.paragraphs):
        # first paragraph is the title
        if i == 0:
            details = get_title_details(p)
            details.update(check_style_detail(p, DETAILS['Title']))
            summary['Title'] = {'details': [details] }

        text = p.text.strip()
        if not text:
            continue

        # find abstract heading
        if text.lower() == 'abstract':
            abstract_index = i
            details = get_abstract_detail(p)
            details.update(check_style_detail(p, DETAILS['Abstract']))
            summary['Abstract'] = {'details': [details] }

        # all headings, paragraphs captions, figures, tables, equations should be between these two
        if abstract_index > 0 and reference_index == 0:
            print(i)
            # check if a known jacow style
            for section_type, section_data in DETAILS.items():
                if 'styles' in section_data:
                    if p.style.name in section_data['styles']['jacow']:
                        found = f"{section_type} - {p.style.name}"
                        print(found)
                        break
                    elif p.style.name in section_data['styles']['normal']:
                        found = f"{section_type} -- {p.style.name}"
                        print(found)
                        break
                else:
                    for sub_type, sub_data in section_data.items():
                        if p.style.name in sub_data['styles']['jacow']:
                            found = f"{section_type} - {sub_type} - {p.style.name}"
                            print(found)
                        elif 'normal' in sub_data['styles'] and p.style.name in sub_data['styles']['normal']:
                            found = f"{section_type} -- {sub_type} -- {p.style.name}"
                            print(found)
                            break

        # find reference heading
        if text.lower() == 'references':
            reference_index = i
            break

    # authors is all the text between title and abstract heading
    summary['Author'] = {'details': [] }
    for p in doc.paragraphs[1: abstract_index]:
        if p.text.strip():
            details = get_author_details(p)
            details.update(check_style_detail(p, DETAILS['Author']))
            summary['Author']['details'].append(details)

    print(summary)
    return summary








