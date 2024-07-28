import os
import sys
from common_io import read_file, write_file, get_file_paths_from_args

def load(fp, level, src_che=None):
    src_idx = ['hasipsio', 'haeyo', 'haera', 'hae'].index(src_che) if src_che else None

    tt = list()

    for line in fp[1:]:
        col = line.rstrip().split(',')  # hasipsio, haeyo, haera, hae
        if level == 'hasipsio':
            src_idx_list = [src_idx] if src_che else [1, 2, 3]
            dst_idx = 0
        elif level == 'haeyo':
            src_idx_list = [src_idx] if src_che else [0, 2, 3]
            dst_idx = 1
        elif level == 'haera':
            src_idx_list = [src_idx] if src_che else [0, 1, 3]
            dst_idx = 2
        elif level == 'hae':
            src_idx_list = [src_idx] if src_che else [0, 1, 2]
            dst_idx = 3
        
        for src_idx in src_idx_list:
            if col[src_idx] != '' and col[dst_idx] != '':
                tt.append((
                    col[src_idx].split('->')[0],
                    col[dst_idx].split('->')[-1]
                ))
    return tt

def convert(sentence, level, src_che=None):

    fp = read_file(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'ko_speech_level.txt'
        )
    )
    
    tt = load(fp, level, src_che)

    for src, dst in tt:
        for sb in " ,.!?":
            sentence = sentence.replace(src + sb, dst + sb)
        sentence = sentence.replace(src + ':', dst + '.')

    return sentence

def hasipsio(sentence, src_che=None):
    return convert(sentence, 'hasipsio', src_che)

def haeyo(sentence, src_che=None):
    return convert(sentence, 'haeyo', src_che)

def haera(sentence, src_che=None):
    return convert(sentence, 'haera', src_che)

def hae(sentence, src_che=None):
    return convert(sentence, 'hae', src_che)

if __name__ == "__main__":
    input_file, output_file = get_file_paths_from_args()
    content = read_file(input_file)
    level = "haeyo"  # 원하는 레벨로 변경
    src_che = None   # 필요 시 원하는 src_che 값으로 변경

    converted_content = [convert(line, level, src_che) for line in content]
    write_file(output_file, converted_content)
