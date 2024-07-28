#!/usr/bin/python3

import sys
from common_io import read_input, write_output, read_file, write_file, get_file_paths_from_args
import convert_speech_level

def main():
    input_file, output_file = get_file_paths_from_args()
    src_che = sys.argv[1] if len(sys.argv) == 2 else None

    if input_file:
        content = read_file(input_file)
        sentence = ''.join(content)  # Assuming the input file contains a single sentence
    else:
        sentence = read_input()

    converted_sentence = convert_speech_level.haera(sentence, src_che)

    if output_file:
        write_file(output_file, [converted_sentence])
    else:
        write_output(converted_sentence)

if __name__ == "__main__":
    main()
