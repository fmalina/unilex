from vocabulary.models import Concept, Vocabulary
from django.template.defaultfilters import slugify
from django.contrib import messages
import xlrd
import csv

def has_unique_ids(col):
    return len(col) == len(set(col))

def last_full_cell(row_data):
    """Return last cell with text in and its column number"""
    rear_cells=[] # until full cell is found
    for x in reversed(row_data):
        rear_cells.append(x)
        if x != '':
            break
    last_full_cell = len(row_data) - len(rear_cells)
    return row_data[last_full_cell], last_full_cell

def handle_error(request, vocab, error):
    messages.error(request, error)
    vocab.delete()
    return '/vocabularies/load-xls'

def load_xls(request, file, title):
    """Import a hierarchy into the DB from Excel
    Adds messages and returns redirect URL"""
    vocab = Vocabulary(title=title)
    vocab.node_id = slugify(title)
    vocab.user = request.user
    vocab.save()
    try:
        book = xlrd.open_workbook(file_contents=file)
        sheet1 = book.sheet_by_index(0)
        col1 = [x.value for x in sheet1.col(0)]
        reader = [[x.value for x in sheet1.row(row_no)] for row_no in range(sheet1.nrows)]
    except xlrd.XLRDError:
        messages.info(request, "That wasn't XLS format. Trying CSV.")
        try:
            f = file.decode().splitlines()
        except UnicodeDecodeError:
            error = "Not a CSV."
            return handle_error(request, vocab, error)
        reader = [x for x in csv.reader(f)]
        try:
            col1 = [x[0] for x in reader]
        except IndexError:
            error = "Not a good CSV. Blank lines."
            return handle_error(request, vocab, error)
        
    id_col = has_unique_ids(col1)
    conceptstack = []
    for line, row in enumerate(reader):
        name, blank = last_full_cell(row)
        concept = Concept(vocabulary=vocab, order=line, name=name)
        if id_col:
            concept.node_id = row[0]
            blank -= 1 # to account for ID column
        concept.save()
        if len(conceptstack) < blank:
            return handle_error(request, vocab,
                "Wrong indent on line %d or non unique IDs. Fix it and try again." % (line + 1))
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