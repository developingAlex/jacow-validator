"""For verifying that an uploaded file matches an entry from the spms
   references csv file and if so, verifies that the title and authors match """

import os
import csv
import re
from jacowvalidator.docutils.authors import get_author_list

RE_MULTI_SPACE = re.compile(r' +')
NON_BREAKING_SPACE = '\u00A0'


class PaperNotFoundError(Exception):
    """Raised when the paper submitted by a user has no matching entry in the
    spms references list of papers"""
    pass


class ColumnNotFoundError(Exception):
    """Raised when the spms references csv file doesn't have a column this
    function expected"""
    pass


class CSVPathNotDeclared(Exception):
    """Raised when the PATH_TO_JACOW_REFERENCES_CSV environment variable is
    not set"""
    pass


class CSVFileNotFound(Exception):
    """Raised when the file pointed to by the PATH_TO_JACOW_REFERENCES_CSV
    environment variable doesnt exist"""
    pass


# runs conformity checks against the references csv file and returns a dict of
# results, eg: result = { title_match: True, authors_match: False }
def reference_csv_check(filename_minus_ext, title, authors):
    result = {
        'title_match': False, 'authors_match': False,
    }
    if 'PATH_TO_JACOW_REFERENCES_CSV' not in os.environ:
        raise CSVPathNotDeclared("The environment variable "
                                 "PATH_TO_JACOW_REFERENCES_CSV is not "
                                 "set! Unable to locate references.csv file for "
                                 "title checking")
    if not os.path.isfile(os.environ['PATH_TO_JACOW_REFERENCES_CSV']):
        raise CSVFileNotFound(f"No file was found at the location {os.environ['PATH_TO_JACOW_REFERENCES_CSV']}")
    # the encoding value is one that should work for most documents.
    # the encoding for a file can be detected with the command:
    #    ` file -i FILE `
    with open(os.environ['PATH_TO_JACOW_REFERENCES_CSV'], encoding="ISO-8859-1") as f:
        reader = csv.reader(f)
        reading_header_row = True
        match_found = False
        for row in reader:
            if reading_header_row:
                reading_header_row = False
                header = row
                title_col = header.index("title")
                paper_col = header.index("paper")
                authors_col = header.index("authors")
                # confirm those headers existed as expected:
                for heading in ['title_col', 'paper_col', 'authors_col']:
                    # (if they didn't exist, the vars will be undefined)
                    if heading not in locals():
                        raise ColumnNotFoundError(f"could not identify {heading} column in references csv")
            else:
                if filename_minus_ext == row[paper_col]:
                    reference_title = RE_MULTI_SPACE.sub(' ', row[title_col].upper())
                    title_match = title.upper().strip('*') == reference_title
                    report, authors_match = get_author_list_report(authors, row[authors_col])

                    summary_list = [{'type': 'Author', 'match_ok': result['match'], 'docx': result['docx'], 'spms': result['spms']} for result in report]

                    return {
                        'title': {
                            'match': title_match,
                            'docx': title,
                            'spms': reference_title
                        },
                        'author': {
                            'match': authors_match,
                            'docx': authors,
                            'spms': row[authors_col],
                            'docx_list': get_author_list(authors),
                            'spms_list': get_author_list(row[authors_col]),
                            'report': report
                        },
                        'summary': [{
                            'type': 'Title',
                            'match_ok': title_match,
                            'docx': title,
                            'spms': reference_title
                        }, {
                            'type': 'Extracted Author List',
                            'match_ok': authors_match,
                            'docx': authors,
                            'spms': row[authors_col],
                        }, *summary_list],
                    }

        # if not returned by now its because the paper wasn't found in the list
        if 'SPMS_DEBUG' in os.environ and os.environ['SPMS_DEBUG'] == 'True':
            return {
                'title': {
                    'match': False,
                    'docx': title.upper(),
                    'spms': 'No matching paper found in the spms csv file'
                },
                'author': {
                    'match': False,
                    'docx': authors,
                    'spms': 'No matching paper found in the spms csv file',
                    'docx_list': list(),
                    'spms_list': list(),
                    'report': list()
                },
                'summary': [{
                    'type': 'title',
                    'match': False,
                    'docx': title.upper(),
                    'spms': 'No matching paper found in the spms csv file'
                    }, {
                    'type': 'author',
                    'match': False,
                    'docx': authors,
                    'spms': 'No matching paper found in the spms csv file',
                }],

            }
        else:
            raise PaperNotFoundError("No matching paper found in the spms csv file")


def get_author_list_report(docx_text, spms_text):
    """Compares two lists of authors (one sourced from the uploaded docx file
    and one sourced from the corresponding paper's entry in the SPMS references
    csv file) and produces a dict array report of the
    form:
        [
            {
            match: True,
            docx: "T. Anderson",
            spms: "T. Anderson"
            },
            {
            match: False,
            docx: "A. Tiller",
            spms: ""
            },
        ]
    """
    space_fixed_docx_text = docx_text.replace(NON_BREAKING_SPACE, ' ')
    docx_list = get_author_list(space_fixed_docx_text)
    spms_list = get_author_list(spms_text)
    # create a copy of spms_list and docx_list so that we can remove items
    #  without mutating the originals:
    fixed_spms_list = normalize_author_names(spms_list)
    fixed_docx_list = normalize_author_names(docx_list)
    spms_authors_to_check = clone_list(fixed_spms_list)
    results = list()
    all_authors_match = True
    for author in fixed_docx_list:
        if author in fixed_spms_list:
            results.append({'match': True, 'docx': author, 'spms': author})
            spms_authors_to_check.remove(author)
        else:
            all_authors_match = False
            results.append({'match': False, 'docx': author, 'spms': ''})

    # by now any authors remaining in the spms_authors_to_check list are ones
    # that had no matching author in the docx list:
    for author in spms_authors_to_check:
        all_authors_match = False
        results.append({'match': False, 'docx': '', 'spms': author})

    return results, all_authors_match


def clone_list(list_to_clone):
    new_list = list()
    for item in list_to_clone:
        new_list.append(item)
    return new_list


def insert_spaces_after_periods(author_list_to_adjust):
    new_list = list()
    for author in author_list_to_adjust:
        fixed_author = author.replace('.', '. ')  # ensure each period is followed by a space
        fixed_author = fixed_author.replace('  ', ' ')  # remove any duplicate spaces that were made
        new_list.append(fixed_author)
    return new_list


def normalize_author_names(author_list_to_clean):
    new_list = list()
    for author in insert_spaces_after_periods(author_list_to_clean):
        # ignore asterisks when comparing:
        fixed_author = author.replace('*', '')
        # ignore hyphens when comparing:
        fixed_author = fixed_author.replace('-', '')
        new_list.append(fixed_author.strip())
    return new_list
