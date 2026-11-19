from glob import glob, iglob
import win32com.client as win32
import os
import argparse

from natsort import natsorted

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--recursive", action="store_true")
args = parser.parse_args()

if args.recursive:
    files = list(iglob(r'**/*.docx', recursive=True)) + list(iglob(r'**/*.doc', recursive=True))
else:
    files = glob(r'*.docx') + glob(r'*.doc')

# Don't launch Word when there is nothing to open; it would leave an empty frame behind.
if not files:
    where = '현재 폴더와 하위 폴더' if args.recursive else '현재 폴더'
    print(f'{where}에 열 Word 파일(.docx, .doc)이 없습니다: {os.getcwd()}')
    raise SystemExit(1)

word = win32.Dispatch('Word.Application')
word.Visible = True

for f in natsorted(files):
    p = os.getcwd() + os.sep + f
    print(f'Opening {p}...')
    word.Documents.Open(p)
