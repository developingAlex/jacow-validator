from docx.oxml.text.font import CT_RPr
from lxml.etree import _Element

VALID_LANGUAGES = ['en-US', 'en-GB', 'en-AU']


# simple unique list of languages
def get_language_tags(doc):
    tags = get_language_tags_location(doc)
    # get unique list
    return list(dict.fromkeys(tags.values()))


def get_language_tags_location(doc):
    tags = {}
    if doc.core_properties.language != '':
        tags['-1'] = doc.core_properties.language
    for i, p in enumerate(doc.paragraphs):
        for r in p.runs:
            for c in r.element.iterchildren():
                if isinstance(c, CT_RPr):
                    for cc in c.iterchildren():
                        if isinstance(cc, _Element) and 'lang' in str(cc):
                            tags[r.text] = cc.items()[0][1]
    # get unique list
    return tags
