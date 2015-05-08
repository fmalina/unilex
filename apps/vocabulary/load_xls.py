from vocabulary.models import Concept, Vocabulary
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import xlrd

def load_xls(request, file):
    """Import a hierarchy into the DB from Excel
    Adds messages and returns redirect URL"""
    vocab = Vocabulary(title=file.name.split('.')[0])
    vocab.save()
    xls = file.read()
    try:
        book = xlrd.open_workbook(file_contents=xls)
    except:
        messages.error(request, 'Sorry, that wasn\'t Excel spreadsheet. Try again.')
        vocab.delete()
        return '/vocabularies/load-xls'
        
    firstSheet = book.sheet_by_index(0)
    conceptstack = []
    for row in range(firstSheet.nrows):
        blank = 0
        while True:
            cell = firstSheet.cell(row, blank)
            if cell.value:
                break
            blank += 1
        concept = Concept(vocabulary=vocab, order=0, name=cell.value)
        concept.save()
        if len(conceptstack) < blank:
            line = int(row)
            line = line + 1
            messages.error(request, 
                "Wrong indentation on line %d. Fix it and try again." % line)
            vocab.delete()
            return '/vocabularies/load-xls'
        if len(conceptstack) > blank:
            for i in range(len(conceptstack) - blank):
                conceptstack.pop()
        if conceptstack:
            concept.parent.add(conceptstack[-1])
            concept.save()
        conceptstack.append(concept)
    messages.success(request, 'Success. Loading vocabulary.')
    return vocab.get_absolute_url()