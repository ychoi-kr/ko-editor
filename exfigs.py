#!/usr/bin/python3

import os
import pathlib
import sys
import zipfile
import fitz  # pip install --upgrade pip; pip install --upgrade pymupdf
from tqdm import tqdm # pip install tqdm


def extract_figs(path):
    if os.path.isfile(path) and path.endswith('.docx'):
        z = zipfile.ZipFile(path, 'r')
        for name in z.namelist():
            if name.startswith('word/media/') and name.split('.')[-1] in ['jpg', 'png']:
                print(f"extracting {name} ...")
                p = pathlib.Path(path).parents[0] / pathlib.Path(name).name
                p.write_bytes(z.read(name))
        z.close()


def extract_figs_from_PDF(path):
    if os.path.isfile(path) and path.endswith('.pdf'):
        doc = fitz.Document(path)
        for i in tqdm(range(len(doc)), desc="pages"):
            for img in tqdm(doc.get_page_images(i), desc="page_images"):
                xref = img[0]
                image = doc.extract_image(xref)
                pix = fitz.Pixmap(doc, xref)
                pix.save("%s_p%s-%s.png" % (path[:-4], i, xref))
    print("Done!")


if __name__ == '__main__':
    arg1 = sys.argv[1]
    if not os.path.isfile(arg1):
        sys.exit(1)
    elif arg1.endswith('.docx'):
        extract_figs(arg1)
    elif arg1.endswith('.pdf'):
        extract_figs_from_PDF(arg1)
    else:
        sys.exit(1)
