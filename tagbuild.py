#!/usr/bin/env python3
import shutil

def make_icons():
    """Generate icons
    # brew install imagemagick
    # sudo pip3 install Wand
    """
    from wand.image import Image
    
    svg = 'tag/img/tag.svg'
    out = 'tag/img/icon.png'
    
    with Image(filename=svg) as img:
        img.format = 'png'
        img.save(filename=out)

for asset in 'autocomplete jquery.formset vocab_set'.split():
    shutil.copy('static/js/%s.js' % asset, 'tag/js.build/')

make_icons()

shutil.make_archive('tag', 'zip', 'tag')
