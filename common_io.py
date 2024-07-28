import sys

def read_input():
    if sys.stdin.isatty():
        return input()
    else:
        return sys.stdin.read()

def write_output(output):
    if sys.stdout.isatty():
        print(output)
    else:
        sys.stdout.write(output)

def read_file(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    return content

def write_file(output_file, content):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(content)

def get_file_paths_from_args():
    if len(sys.argv) < 2:
        return None, None
    elif len(sys.argv) == 2:
        return sys.argv[1], None
    elif len(sys.argv) == 3:
        return sys.argv[1], sys.argv[2]
    else:
        print(f"Usage: python {sys.argv[0]} [input_file] [output_file]")
        sys.exit(1)
