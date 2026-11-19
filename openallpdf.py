import os
import subprocess

def open_pdf_with_acrobat(file_path):
    acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
    subprocess.Popen([acrobat_path, file_path])

def search_and_open_pdfs(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                open_pdf_with_acrobat(file_path)

current_directory = os.getcwd()
search_and_open_pdfs(current_directory)
