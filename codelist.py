import docx
import re
from typing import List, Tuple
import sys

def extract_examples(docx_path: str) -> List[Tuple[str, str, str, str, str]]:
    doc = docx.Document(docx_path)
    examples = []
    current_chapter = ""
    current_section = ""
    current_subsection = ""
    chapter_num = 0
    section_num = 0
    subsection_num = 0
    
    for paragraph in doc.paragraphs:
        if paragraph.style.name == 'Heading 1':
            chapter_num += 1
            section_num = 0
            subsection_num = 0
            current_chapter = f"{chapter_num}. {paragraph.text}"
            current_section = ""
            current_subsection = ""
        elif paragraph.style.name == 'Heading 2':
            section_num += 1
            subsection_num = 0
            current_section = f"{chapter_num}.{section_num}. {paragraph.text}"
            current_subsection = ""
        elif paragraph.style.name == 'Heading 3':
            subsection_num += 1
            current_subsection = f"{chapter_num}.{section_num}.{subsection_num}. {paragraph.text}"
        
        example_match = re.match(r'^예제 (\d+\.\d+)\s*(.+)', paragraph.text)
        if example_match:
            example_number = example_match.group(1)
            example_title = example_match.group(2)
            examples.append((current_chapter, current_section, current_subsection, example_number, example_title))
    
    return examples

def save_to_tsv(examples: List[Tuple[str, str, str, str, str]], output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("장\t절\t항\t예제 번호\t예제 제목\n")
        for example in examples:
            f.write("\t".join(example) + "\n")

if __name__ == "__main__":
    docx_path = sys.argv[1]
    output_path = "codelist.tsv"  # 출력 TSV 파일 경로를 지정하세요
    
    examples = extract_examples(docx_path)
    save_to_tsv(examples, output_path)
    print(f"예제 목록이 {output_path}에 저장되었습니다.")
