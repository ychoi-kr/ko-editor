import os
import sys

def load(fp, level, src_che=None):
    src_idx = ['hasipsio', 'haeyo', 'haera', 'hae'].index(src_che) if src_che else None

    tt = list()

    for line in fp.readlines()[1:]:
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

    fp = open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'ko_speech_level.txt'
        ),
        "rt",
        encoding="UTF8"
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

