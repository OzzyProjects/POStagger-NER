# -*- coding: utf-8 -*-
#!usr/bin/env python3

# module pour les expressions régulières
import re

"""
script python basé uniquement sur les expressions régulières pour remplacer les étiquettes Penn TreeBank
par les étiquettes universelles d'un fichier en utilisant la table de correspondance POSTags_PTB_Universal.txt
Pour cela le script va générer des expressions régulières pour chaque pos Penn TreeBank à modifier et les appliquer
séquentiellement à la fin de chaque ligne du fichier.
Les résultats sont sauvegardés au fur et à mesure dans un fichier de sortie.
"""

# fonction qui charge le fichier POSTags_PTB_Universal_Linux.txt en mémoire en plaçant les données dans un dictionnaire
# les pos universels sont les clés et les pos Penn TreeBank sont les valeurs (sous forme de liste)
# car il peut y avoir plusieurs pos Penn TreeBank pour une seule étiquette universelle.
def load_pos_table():

    try:
         
        # on ouvre en lecture notre table de correspondances des étiquettes
        with open('POSTags_PTB_Universal_Linux.txt', 'r', encoding='utf-8') as universal:

            dict_pos = {}
            # on lit le contenu du fichier ligne par ligne
            for sent in universal.readlines():
                for line in sent.splitlines():
                    # on ajoute les clé/valeurs dans un dict en splittant en 2 chaque ligne
                    # cut[0] = pos Penn TreeBank et cut[1] = étiquettes universelles sous forme de listes
                    cut = line.strip().split()
                    dict_pos[cut[1]] = dict_pos.get(cut[1], list()) + [cut[0]]

        return dict_pos

    # si une exception se produit
    except Exception as erreur:
        print(f'load_pos_table : {erreur}')

# fonction qui convertit chaque fichier au format POS universel et écrit le résultat dans un autre fichier à partir d'un fichier
# étiqueté au format Penn Treebank
def convert_tag(source_file, target_file, pos_table):

    try:

        # on ouvre le fichier source et le fichier cible (fichier de résultat)
        with open(source_file, 'r', encoding='utf-8') as sample_stan, open(target_file, 'w', encoding='utf-8') as result_file:

            # on lit le fichier etiqueté au format Pen Treebank ligne par ligne
            for line in sample_stan.readlines():

                rx_dctvals = {}
                # on construit une expression régulière pour l'ensemble de la ligne pour chaque pos Penn Treebank à remplacer
                # la valeur de ce dictionnaire est le pos universel par lequel remplacer l'autre et l'expression régulière pour les modifier
                # est la clé de ce dictionnaire
                for key, val in pos_table.items():
                    # on génère et compile notre expression régulière pour remplacer un pos Penn Treebank particulier (noms, adj, pronoms)
                    # par son équivalent universel (on regroupe les pos Penn Treebank du même type (les noms, les adjs etc...))
                    # car pour un pos universel, il peut y avoir plusieurs étiquettes Penn Treebank
                    # il faut aussi trier les pos par ordre decroissant de taille pour éviter les conflits de remplacement
                    rx_dctvals[re.compile("|".join(sorted([to_regex(v) for v in val], key=len, reverse=True)))] = key

                # on remplace séquentiellement chaque pos Penn Treebank avec nos regexp par les pos universels pour l'ensemble de la ligne
                for rx, repl in rx_dctvals.items():
                    line = rx.sub(repl.replace('\\', '\\\\'), line)

                # on écrit dans le fichier cible la ligne modifiée et correctement étiquetée
                result_file.write(line)

    except Exception as erreur:
        print(f'convert_tag: {erreur}')

# fonction qui prend chaque string x en ne tenant pas compte du '_' au début et ajoute un leeding word boundary
# avant chaque item qui commence par un caractère et ajoute soit un word boundary soit \B
# à la fin de chaque item. Tous les caractères spéciaux sont aussi échappés. C'est important pour la constitution
# de nos regexp de constituer des blocs de chaque mots séparés par des boundaries et d'échapper les caractères spéciaux.
def to_regex(x):

    r = []
    if x[0].isalnum() or x[0] == '_':
        r.append(r'(?<![^\W_])')
    else:
        if any(l.isalnum() or l=='_' for l in x):
            r.append(r'\B')
    r.append(re.escape(x))
    if x[-1].isalnum() or x[-1] == '_':
        r.append(r'\b')
    else:
        if any(l.isalnum() or l=='_' for l in x):
            r.append(r'\B')
    return "".join(r)

# fonction principale
def main():

    pos_table = load_pos_table()

    convert_tag('wsj_0010_sample.txt.pos.stanford', 'wsj_0010_sample.txt.pos.univ.stanford', pos_table)

    convert_tag('wsj_0010_sample.pos.stanford.ref', 'wsj_0010_sample.txt.pos.univ.ref', pos_table)

if __name__ == '__main__':
    main()