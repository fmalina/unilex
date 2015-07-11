#!/usr/bin/env python3
import shutil

for asset in 'autocomplete jquery.formset vocab_set'.split():
    print('Copying %s.js' % asset)
    shutil.copy('static/js/%s.js' % asset, 'tag/js.build/')

print('Packing tag.zip')
shutil.make_archive('tag', 'zip', 'tag')
