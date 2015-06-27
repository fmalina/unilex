from vocabulary.models import Concept, Vocabulary
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import xlrd

def has_unique_ids(col1):
    col = [x.value for x in col1]
    return len(col) == len(set(col))

def last_full_cell(row_data):
    """Return last cell with text in and its column number"""
    rear_cells=[] # until full cell is found
    for x in reversed(row_data):
        rear_cells.append(x)
        if x.value != '':
            break
    last_full_cell = len(row_data) - len(rear_cells)
    return row_data[last_full_cell].value, last_full_cell

def first_full_cell(sheet1, row_no):
    """Return 1st full cell and number of preceeding blank
    >>> name, blank = first_full_cell(sheet1, row_no)
    """
    blank = 0
    while True:
        cell = sheet1.cell(row_no, blank)
        if cell.value:
            break
        blank += 1
    return cell.value, blank

def handle_error(request, vocab, error):
    messages.error(request, error)
    vocab.delete()
    return '/vocabularies/load-xls'

def load_xls(request, file):
    """Import a hierarchy into the DB from Excel
    Adds messages and returns redirect URL"""
    vocab = Vocabulary(title=file.name.split('.')[0].split('/')[-1])
    vocab.user = request.user
    vocab.save()
    xls = file.read()
    try:
        book = xlrd.open_workbook(file_contents=xls)
    except xlrd.XLRDError:
        return handle_error(request, vocab,
            "Sorry, that wasn't XLS format. Try again.")
    sheet1 = book.sheet_by_index(0)
    id_col = has_unique_ids(sheet1.col(0))
    conceptstack = []
    for row_no in range(sheet1.nrows):
        row = sheet1.row(row_no)
        name, blank = last_full_cell(row)
        concept = Concept(vocabulary=vocab, order=0, name=name)
        if id_col:
            concept.node_id = row[0].value
            blank -= 1 # to account for ID column
        concept.save()
        if len(conceptstack) < blank:
            return handle_error(request, vocab,
                "Wrong indent on line %d. Fix it and try again." % (int(row_no) + 1))
        if len(conceptstack) > blank:
            for i in range(len(conceptstack) - blank):
                conceptstack.pop()
        if conceptstack:
            concept.parent.add(conceptstack[-1])
            concept.save()
        conceptstack.append(concept)

    messages.success(request, 'Success, taxonomy loaded.')
    msg = "First column had unique IDs, these were used." if id_col\
     else "First column didn't have unique IDs, created new ones."
    messages.info(request, msg)
    return vocab.get_absolute_url()