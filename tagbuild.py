#!/usr/bin/env python3
import shutil

for asset in ['file_path_1', 'file_path_2']:
    print('Copying %s.js' % asset)
    shutil.copy('static/%s' % asset, 'tag/build/')

print('Packing tag.zip ready for Chrome Web Store.')
shutil.make_archive('tag', 'zip', 'tag')
