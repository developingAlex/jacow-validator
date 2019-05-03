import re
from collections import OrderedDict
from itertools import chain
from .styles import check_style

RE_FIG_TITLES = re.compile(r'(^Figure \d+[.:])')
RE_FIG_INTEXT = re.compile(r'(Fig.\s?\d+|Figure\s?\d+[.\s]+)')

FIGURE_DETAILS = {
    'styles': {
        'jacow': 'Figure Caption',
    },
    'alignment': 'CENTER',
    'font_size': 10.0,
    'space_before': 3.0,
    'space_after': ['>=', 3.0],
    'bold': None,
    'italic': None,
}

FIGURE_MULTI_DETAILS = {
    'styles': {
        'jacow': 'Caption Multi Line',
    },
    'alignment': 'JUSTIFY',
    'font_size': 10.0,
    'space_before': 3.0,
    'space_after': ['>=', 3.0],
    'bold': None,
    'italic': None,
}


def _fig_to_int(s):
    return int(''.join(filter(str.isdigit, s)))


def extract_figures(doc):
    figures_refs = []
    figures_captions = []

    def _find_figure_captions(p):
        for f in RE_FIG_TITLES.findall(p.text.strip()):
            figure_compare = FIGURE_DETAILS
            # 53 chars is approx where it changes from 1 line to 2 lines
            if len(p.text.strip()) > 53:
                figure_compare = FIGURE_MULTI_DETAILS
            style_ok, detail = check_style(p, figure_compare)
            _id = _fig_to_int(f)
            figure_detail = dict(
                id=_id,
                name=f,
                text=p.text.strip(),
                style=p.style.name,
                style_ok=style_ok and p.style.name in ['Figure Caption', 'Caption Multi Line', 'Caption'],
            )
            figure_detail.update(detail)
            # figure_detail.update(detail)
            figures_captions.append(figure_detail)

    for p in doc.paragraphs:
        # find references to figures
        for f in iter(f.strip() for f in RE_FIG_INTEXT.findall(p.text)):
            if f.endswith('.') and p.text.strip().startswith(f):
                # probably a figure caption with . instead of :
                continue
            figures_refs.append(dict(id=_fig_to_int(f), name=f))

        # find figure captions
        _find_figure_captions(p)

    # search for figure captions in tables
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    _find_figure_captions(p)

    figures = OrderedDict()
    # no figure found means there is probably an error with parsing though.
    if len(figures_refs) == 0 and len(figures_captions) == 0:
        _last = 0
    else:
        _last = max(
            chain.from_iterable(
                [
                    (fig['id'] for fig in figures_captions),
                    (fig['id'] for fig in figures_refs),
                ]
            )
        )

    for i in range(1, _last + 1):
        caption = [c for c in figures_captions if c['id'] == i]

        figures[i] = {
            'refs': list(f['name'] for f in figures_refs if f['id'] == i),
            'duplicate': len(caption) != 1,
            'found': len(caption) > 0,
            'caption_ok': len(caption) == 1 and caption[0]['name'].endswith(':')
        }
        figures[i]['used'] = len(figures[i]['refs']) > 0
        if caption:
            figures[i].update(**caption[0])

    return figures
