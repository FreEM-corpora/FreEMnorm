import os
import shutil

# Créer le dossier "data" s'il n'existe pas déjà
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Liste des dossiers source et destination
source_folders = ["split/dev", "split/test", "split/train"]
dest_folders = ["data/dev", "data/test", "data/train"]

# Parcourir les dossiers source et destination
for source_folder, dest_folder in zip(source_folders, dest_folders):
    # Récupérer la liste des fichiers .tsv dans le dossier source
    files = [file for file in os.listdir(source_folder) if file.endswith('.tsv')]

    # Fusionner les contenus des fichiers .tsv
    merged_data = []
    for file in files:
        with open(os.path.join(source_folder, file), 'r') as f:
            merged_data.extend(f.readlines())

    # Trier les lignes par ordre alphabétique
    merged_data.sort()

    # Séparer chaque ligne en deux parties (avant et après le caractère de tabulation)
    src_data = [line.split('\t')[0] for line in merged_data]
    trg_data = [line.split('\t')[1] for line in merged_data]


    # Enregistrer les données dans les fichiers .src et .trg respectivement
    with open(os.path.join(dest_folder + ".src"), 'w') as src_file:
        src_file.write('\n'.join(src_data))

    with open(os.path.join(dest_folder + ".trg"), 'w') as trg_file:
        trg = ''.join(trg_data)[0:-2]
        trg_file.write(trg)
