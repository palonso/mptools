import xml.etree.ElementTree as ET
import gzip
from argparse import ArgumentParser
from pathlib import Path


n_nodes = 0


def find_and_delete_nodes(root, node_name):
    global n_nodes

    for child in root:
        if child.tag == node_name:
            root.remove(child)
            n_nodes += 1

        child = find_and_delete_nodes(child, node_name)

    return root


parser = ArgumentParser(description="Convert a Live project to a Lite project")
parser.add_argument("input_file", type=Path, help="The input .als Ableton project file")

# read als file with argparse
args = parser.parse_args()
input_file = args.input_file

# uncompress als project (gzip format)
with gzip.open(input_file, "rb") as f_in:
    file_content = f_in.read()

# read xml file inside als project
root = ET.fromstring(file_content)

# find /lanes fiends in the xml file and remove them
print("Removing TakeLanes...")
root = find_and_delete_nodes(root, "TakeLanes")
print(f"Removed {n_nodes} TakeLanes")
n_nodes = 0

output_content = ET.tostring(root, xml_declaration=True, encoding="UTF-8")

# create a new xml file with the _lite suffix
output_file = input_file.with_suffix(".lite.als")
with gzip.open(output_file, "wb") as f_out:
    f_out.write(output_content)
