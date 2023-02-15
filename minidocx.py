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


def _resize_images_in_zipfile(zip_path, scale):
    in_zip_path = os.path.abspath(zip_path)

    if not (os.path.isfile(in_zip_path) and Path(in_zip_path).suffix == '.docx'):
        print("Not a .docx file: " + in_zip_path)
        sys.exit(1)
    input_zip = zipfile.ZipFile(in_zip_path, 'r')
    out_zip_path = os.path.splitext(in_zip_path)[0] + '_mini.docx'

    working_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        tmp_zip_path = os.path.join(tmpdir, os.path.basename(in_zip_path))
        tmp_zip = zipfile.ZipFile(tmp_zip_path, 'w')
    
        for item in input_zip.infolist():
            filename = item.filename
            if filename.startswith('word/media/') and filename.split('.')[-1] in ['jpg', 'png']:
                input_zip.extract(item)
                img = Image.open(filename)
                resized_img = img.resize(
                    (int(img.width * scale), int(img.height * scale))
                )
                resized_img.save(filename)
                tmp_zip.write(filename)
            else:
                tmp_zip.writestr(item, input_zip.read(filename))
        
        input_zip.close()
        tmp_zip.close()
        shutil.copy(tmp_zip_path, out_zip_path)


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
