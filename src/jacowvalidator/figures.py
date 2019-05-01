import re
from collections import OrderedDict
from itertools import chain


RE_FIG_TITLES = re.compile(r'(^Figure \d+[.:])')
RE_FIG_INTEXT = re.compile(r'(Fig.\s?\d+|Figure\s?\d+[.\s]+)')


def _fig_to_int(s):
    return int(''.join(filter(str.isdigit, s)))


def extract_figures(doc):
    figures_refs = []
    figures_captions = []

    def _find_figure_captions(p):
        for f in RE_FIG_TITLES.findall(p.text.strip()):
            _id = _fig_to_int(f)
            figures_captions.append(
                dict(
                    id=_id,
                    name=f,
                    text=p.text.strip(),
                    style=p.style.name,
                    style_ok=p.style.name in ['Figure Caption', 'Caption Multi Line', 'Caption'],
                )
            )

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
