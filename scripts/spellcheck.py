#!/usr/bin/env python3
"""
Scanne un dossier de fichiers .tsv (col1 = original, col2 = modernisé)
et liste, via hunspell (fr_FR), les mots de la colonne modernisée absents
du dictionnaire ET absents de la whitelist. Ne corrige RIEN automatiquement.

v3 :
  - normalisation Unicode NFC systématique (mots de la whitelist, mots
    extraits des fichiers, sortie de hunspell) pour éviter les faux
    "doublons"/"non-matchs" dus à des formes NFC vs NFD (fréquent sur Mac).
  - la whitelist est nettoyée à chaque run : dédoublonnée (après
    normalisation) et triée alphabétiquement, en place.

Usage :
    python3 spellcheck_tsv_v3.py [dossier_tsv] [sortie.csv] [whitelist.txt]
"""
import csv
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

TOKEN_RE = re.compile(r"[^\s]+", re.UNICODE)
STRIP_CHARS = " \t«»\"“”‘’'.,;:!?…()[]{}—–-"

def norm(s):
    return unicodedata.normalize("NFC", s)

def clean_token(tok):
    return norm(tok.strip(STRIP_CHARS))

def run_hunspell_list(text):
    proc = subprocess.run(
        ["hunspell", "-d", "fr_FR", "-i", "utf-8", "-l"],
        input=text, capture_output=True, text=True,
    )
    return {norm(w) for w in proc.stdout.splitlines() if w}

def load_and_clean_whitelist(path):
    p = Path(path)
    if not p.exists():
        p.write_text("", encoding="utf-8")
        print(f"Whitelist créée (vide) : {p}")
        return set()

    raw_words = [w.strip() for w in p.read_text(encoding="utf-8").splitlines() if w.strip()]
    normalized = sorted({norm(w) for w in raw_words}, key=lambda w: w.lower())

    n_before = len(raw_words)
    n_after = len(normalized)
    if raw_words != normalized:
        p.write_text("\n".join(normalized) + "\n", encoding="utf-8")
        msg = f"Whitelist nettoyée : {n_before} -> {n_after} mot(s) (doublons/normalisation Unicode retirés, triée)"
    else:
        msg = f"Whitelist chargée : {n_after} mot(s), déjà propre"
    print(msg)
    return set(normalized)

def process_folder(folder, out_csv, whitelist_path):
    whitelist = load_and_clean_whitelist(whitelist_path)

    rows = []
    files = sorted(Path(folder).glob("*.tsv"))
    if not files:
        print(f"Aucun .tsv trouvé dans {folder}")
        return

    for n, fp in enumerate(files, start=1):
        parsed = []
        with open(fp, encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                parsed.append((i, parts[0], norm(parts[1])))

        if not parsed:
            continue

        full_text = "\n".join(p[2] for p in parsed)
        misspelled = run_hunspell_list(full_text)
        misspelled -= whitelist
        if not misspelled:
            continue

        for i, original, modernise in parsed:
            for raw_tok in TOKEN_RE.findall(modernise):
                tok = clean_token(raw_tok)
                if tok in misspelled:
                    rows.append({
                        "fichier": fp.name,
                        "ligne": i,
                        "mot_suspect": tok,
                        "original": original,
                        "modernise": modernise,
                    })

        if n % 20 == 0 or n == len(files):
            print(f"  ... {n}/{len(files)} fichiers traités", file=sys.stderr)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["fichier", "ligne", "mot_suspect", "original", "modernise"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} candidat(s) restant(s) dans {len(files)} fichier(s) -> {out_csv}")

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else "candidats_orthographe.csv"
    whitelist = sys.argv[3] if len(sys.argv) > 3 else "mots_valides.txt"
    process_folder(folder, out, whitelist)
