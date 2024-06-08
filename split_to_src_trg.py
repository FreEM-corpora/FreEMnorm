import os
import shutil
import sys
import argparse

#For colab or other notebook
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--colab", action='store_true', required=False, default='', help="Use this if you use colab")
args = parser.parse_args()

if args.colab:
    folder="/content/FreEMnorm/"
    print("Your are using colab!")
else:
    folder = os.path.abspath(os.path.dirname(sys.argv[0]))
    print("Your are not using colab!")


#Check if data folder exists
data_dir = os.path.join(folder,"data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

#Setting variables
source_folders = [os.path.join(folder,"split/dev"), os.path.join(folder,"split/test"), os.path.join(folder,"split/train")]
new_files = [os.path.join(folder,"data/dev"), os.path.join(folder,"data/test"), os.path.join(folder,"data/train")]

# Looping over the source directory
for source_folder, new_file in zip(source_folders, new_files):
    # Get the list of .tsv files in the source_folders
    files = [file for file in os.listdir(source_folder) if file.endswith('.tsv')]

    # FMerge the content of the .tsv files
    merged_data = []
    for file in files:
        with open(os.path.join(source_folder, file), 'r') as f:
            merged_data.extend(f.readlines())

    # Sort alphabetically the data
    #merged_data.sort()

    # Split line into two (before and after the tab)
    src_data = [line.split('\t')[0] for line in merged_data]
    trg_data = [line.split('\t')[1] for line in merged_data]


    # savec the new files with .src and .trg extentions depending of the use
    with open(os.path.join(new_file + ".src"), 'w') as src_file:
        src_file.write('\n'.join(src_data))

    with open(os.path.join(new_file + ".trg"), 'w') as trg_file:
        trg = ''.join(trg_data)[0:-2]
        trg_file.write(trg)