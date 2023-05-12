import sys

def change_indentation(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.readlines()

    new_content = []
    for line in content:
        if line.startswith("   "):
            new_content.append("    " + line[3:])
        else:
            new_content.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(new_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python change_indentation.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    change_indentation(input_file, output_file)
