import argparse
import re
import os
import shutil
import tempfile

from natsort import natsorted

import PyPDF2

if PyPDF2.__version__ < '3.0.0':
    from PyPDF2 import PdfFileMerger as PdfMerger
    PdfMerger.add_outline_item = PdfMerger.addBookmark
    from PyPDF2 import PdfFileReader as PdfReader
else:
    from PyPDF2 import PdfMerger
    from PyPDF2 import PdfReader


def getnumpages(reader):
    if PyPDF2.__version__ < '3.0.0':
        return reader.getNumPages
    else:
        return len(reader.pages)


def main(book_title, directory, sub_dir='merged'):
    pattern = re.compile(rf'{re.escape(book_title)}.*\.pdf')
    file_list = [file for file in os.listdir(directory) if pattern.match(file)]
    sorted_file_list = natsorted(file_list)
    if not sorted_file_list:
        all_pdfs = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
        print(f"'{book_title}'로 시작하는 PDF를 찾지 못했습니다.")
        if all_pdfs:
            print(f"디렉토리 내 PDF 파일: {natsorted(all_pdfs)[:10]}")
        return
    print(f"{len(sorted_file_list)}개 파일 발견")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 원본 파일들을 로컬 임시 폴더로 복사
        for f in sorted_file_list:
            src = os.path.join(directory, f)
            print(f"복사 중: {f}")
            shutil.copy2(src, tmp_dir)

        # 로컬에서 merge
        merger = PdfMerger()
        current_page = 0
        for f in sorted_file_list:
            local_f = os.path.join(tmp_dir, f)
            reader = PdfReader(local_f)
            bookmark_title = os.path.splitext(f)[0]
            merger.append(local_f)
            merger.add_outline_item(bookmark_title, pagenum=current_page)
            current_page += getnumpages(reader)

        tmp_output = os.path.join(tmp_dir, f"{book_title}.pdf")
        merger.write(tmp_output)
        merger.close()
        print("병합 완료. 파일 이동 중...")

        # 결과를 원래 경로로 이동
        output_dir = os.path.join(directory, sub_dir)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        shutil.copy2(tmp_output, os.path.join(output_dir, f"{book_title}.pdf"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", default=".", help="directory where files to be merged live")
    parser.add_argument("bookname")
    args = parser.parse_args()
    main(args.bookname, args.directory)
