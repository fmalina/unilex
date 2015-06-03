#!/usr/bin/env python3
import shutil

for asset in 'autocomplete jquery.formset vocab_set'.split():
    shutil.copy('static/js/%s.js' % asset, 'tag/js.build/')

shutil.make_archive('tag', 'zip', 'tag')
