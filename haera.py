#!/usr/bin/python3

import sys
import convert_speech_level

src_che = sys.argv[1] if len(sys.argv) == 2 else None
sentence = input()
print()
print(convert_speech_level.haera(sentence, src_che))
