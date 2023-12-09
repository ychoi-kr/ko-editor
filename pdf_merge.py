import argparse
import re
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
    
    pattern = re.compile(rf'{re.escape(book_title)}.*\.pdf')
    file_list = [file for file in os.listdir(directory) if pattern.match(file)]
    sorted_file_list = natsorted(file_list)

    for f in sorted_file_list:
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
