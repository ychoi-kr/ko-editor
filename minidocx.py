#!/usr/bin/python3

import os
import sys
from pathlib import Path
import shutil
import zipfile
from PIL import Image
from io import StringIO
import tempfile


def minimize(docx):
    scale = 0.25
    return _resize_images_in_zipfile(docx, scale)


def _resize_images_in_zipfile(zipfile_path, scale):
    if not (os.path.isfile(zipfile_path) and Path(zipfile_path).suffix == '.docx'):
        print("Not a .docx file: " + zipfile_path)
        sys.exit(1)

    input_zip = zipfile.ZipFile(zipfile_path, 'r')
    output_zip = zipfile.ZipFile(
        os.path.splitext(zipfile_path)[0] + '_mini.docx',
        'w'
    )

    for item in input_zip.infolist():
        filename = item.filename
        if filename.startswith('word/media/') and filename.split('.')[-1] in ['jpg', 'png']:
            input_zip.extract(item)
            img = Image.open(filename)
            resized_img = img.resize(
                (int(img.width * scale), int(img.height * scale))
            )
            resized_img.save(filename)
            output_zip.write(filename)
        else:
            output_zip.writestr(item, input_zip.read(filename))
    
    input_zip.close()
    output_zip.close()


if __name__ == '__main__':
    arg1 = sys.argv[1]
    if not os.path.isfile(arg1):
        print("Not a file: " + arg1)
        sys.exit(1)
    elif arg1.endswith('.docx'):
        docx = arg1
        minimize(docx)
    else:
        print("Not a .docx file: " + arg1)
        sys.exit(1)
