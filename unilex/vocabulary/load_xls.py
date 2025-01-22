from unilex.vocabulary.models import Concept, Vocabulary
from django.template.defaultfilters import slugify
import xlrd
import csv


def has_unique_ids(col):
    """Gets cells of first column as a list,
    Checks if any contains a space meaning they are not IDs.
    checks for uniqueness of those IDs"""
    if any(' ' in str(i).strip() for i in col):
        return False  # Found a space in an ID cell
    return len(col) == len(set(col))


def last_full_cell(row_data):
    """Return last cell with text in and its column number"""
    rear_cells = []  # until full cell is found
    for x in reversed(row_data):
        rear_cells.append(x)
        if x != '':
            break
    last_full_cell = len(row_data) - len(rear_cells)
    return row_data[last_full_cell], last_full_cell


class XLSLoadException(Exception):
    pass


def load_xls(user, file, title):
    """Import a hierarchy into the DB from Excel
    Adds messages and returns redirect URL"""
    vocab = Vocabulary(title=title)
    vocab.node_id = slugify(title)
    vocab.user = user
    vocab.save()
    try:
        book = xlrd.open_workbook(file_contents=file)
        sheet1 = book.sheet_by_index(0)
        col1 = [x.value for x in sheet1.col(0)]
        reader = [[x.value for x in sheet1.row(row_no)]
                  for row_no in range(sheet1.nrows)]
    except xlrd.XLRDError:
        try:
            f = file.decode().splitlines()
        except UnicodeDecodeError as e:
            raise XLSLoadException("Not a CSV.") from e
        reader = [[cell.strip() for cell in row]
                  for row in csv.reader(f)]
        try:
            col1 = [x[0] for x in reader]
        except IndexError as e:
            raise XLSLoadException("Remove blank lines!") from e

    id_col = has_unique_ids(col1)
    description_column_index = None
    parents = []
    for line, row in enumerate(reader):
        # Check if a description column is present on line 1
        if line == 0:
            san_row = [str(cell).strip().lower() for cell in row]
            if 'definition' in san_row:
                description_column_index = san_row.index('definition')
                continue
        # create a concept
        name, blank = last_full_cell(row)
        concept = Concept(vocabulary=vocab, order=line, name=name)
        # set ID if present
        if id_col:
            concept.node_id = row[0]
            blank -= 1  # to account for ID column
        # set description if present
        if description_column_index is not None:
            concept.description = row[description_column_index]
            blank -= 1  # to account for description column
        
        concept.save()
        if len(parents) < blank:
            raise XLSLoadException(
                f"Wrong indent on line {line + 1} or non unique IDs.")
        
        if len(parents) > blank:
            for _i in range(len(parents) - blank):
                parents.pop()

        if parents:
            concept.parent.add(parents[-1])
            concept.save()
        parents.append(concept)

    return vocab
