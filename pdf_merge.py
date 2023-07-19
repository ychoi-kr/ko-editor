import argparse
from glob import glob
import os

from natsort import natsorted


try:
    from PyPDF2 import PdfMerger as Merger
except ImportError:
    from PyPDF2 import PdfFileMerger as Merger
finally:
    from PyPDF2 import PdfFileReader


def main(book_title, directory, sub_dir='merged'):
    merger = Merger()
    current_page = 0
    
    for f in natsorted(glob(f"{directory}/{book_title}*.pdf")):
        reader = PdfFileReader(f)
        bookmark_title = os.path.splitext(os.path.basename(f))[0]
        merger.append(f)
        merger.addBookmark(bookmark_title, pagenum=current_page)
        current_page += reader.getNumPages()

    os.chdir(directory)
    if not os.path.isdir(sub_dir):
        os.mkdir(sub_dir)

    merger.write(f"{directory}/{sub_dir}/{bookname}.pdf")
    merger.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", default=".", help="directory where files to be merged live")
    parser.add_argument("bookname")
    args = parser.parse_args()
    directory = args.directory
    bookname = args.bookname
    
    main(args.bookname, args.directory)
