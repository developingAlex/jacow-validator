"""For verifying that an uploaded file matches an entry from the spms
   references csv file and if so, verifies that the title and authors match """

import os
import csv


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
                    title_match = title.upper() == row[title_col].upper()
                    authors_match = authors == row[authors_col]
                    return title_match, authors_match
        # if not returned by now its because the paper wasn't found in the list
        raise PaperNotFoundError("No matching paper found in the spms csv file")
