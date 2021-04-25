# -*- coding: utf-8 -*-
#!usr/bin/env python3

"""
Ce script extrait les entités nommées et les met à la volée au format
universel. Pour ce faire, il s'appuie sur une base regex solide constituée d'un dict qui prend en clés les regex matchant pour les formes NLTK à remplacer 
et prend une clé contenant la valeur de l’étiquète universelle du NER ou du POS TAG. (voir fonction convert_format())
Par ailleurs, il affiche également les POS tags de chaque mot au format universel.
LEe fichier avec les étiquettes NER standards se nomme wsj_0010_sample.txt.ne.standard
Pour le pos tagging, j'ai fait le choix d'utiliser aussi tree2conlltags car cette fonction renvoie une liste de tuples et non un NLTK Tree, objet que nous trouvons plus
compliquer à manipuler pour notre tâche.
Les étiquètes NER tree2conlltags seront convertis au format universel grâce aux regex.
Pour le style, le script utilise beaucoup de lists et dicts comprehension.

ATTENTION : il n'est compatible qu'avec Python 3.8 voire 3.9

"""

from contextlib import ExitStack
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import ne_chunk, pos_tag
from nltk.chunk import tree2conlltags
import re
import sys

# dictionnaire : table de correspondance des étiquètes NER (conll to standard)
dict_ner = {'I-ORG':['I-ORGANIZATION','FACILITY'], 'B-ORG':'B-ORGANIZATION', 'I-PERS':'I-PERSON', 'B-PERS':'B-PERSON', 'I-LOC':'I-LOCATION', 'B-LOC':'B-LOCATION',
'MISC':['DATE','TIME', 'MONEY', 'PERCENT']}

# fonction qui charge le premier dictionnaire de données (valeurs particulières, valeurs universelles, étiquètes POS et NER)
# c'est ce qui va servir de base pour la construction de nos regex.
def load_pos_table():

    try:
         
        with open(sys.argv[1], 'r', encoding='utf-8') as universal:

            # on commence par charger notre dictionnaire avec la table des étiquettes POS Penn Treebank, POS NLTK
            dict_pos = {}
            for sent in universal.readlines():
                for line in sent.splitlines():
                    cut = line.strip().split()
                    dict_pos[cut[1]] = dict_pos.get(cut[1], list()) + [cut[0]]

        return dict_pos

    except Exception as erreur:
        print(f'load_pos_table : {erreur}')

# fonction qui utilise un module regex efficace pour supprimer les formes non standards (POS tag et NER) et les remplacer par les formes universelles
# cette fonction a l'avantage d’être générique et peut s’appliquer partout pour remplacer tout ce que l'on souhaite. Elle se base sur un dictionnaire.
def convert_format(line, dic):

    try:

        # comme il peut y avoir plusieurs formes non standards pour une forme universelle, on crée un regex d’agrégation en triant les valeurs par ordre décroissant de taille
        # pour éviter les conflits de remplacements. C'est la clé du dictionnaire. Sa valeur est l’étiquette universelle correspondante.
        # Cette correspondance est basée sur le dictionnaire pos_table que nous avons chargé avec POSTags_PTB_Universal_Linux.txt
        # si la valeur est une string on doit la concaténer pour éviter une itération caractère par caractère ''.join([t for t in val])
        rx_dctvals = {re.compile("|".join(sorted([to_regex(v) if not isinstance(val, str) else to_regex(''.join([t for t in val])) for v in val], key=len, reverse=True))):key for key, val in dic.items()}

        # on remplace séquentiellement nos valeurs non standards par leur équivalent universel avec notre liste de regex constituées précédemment
        # et on retourne le résultat, le dernier élément de notre liste (la ligne sans aucun POS et NER non standard)
        #Version 3.8+
        return [line := rx.sub(repl.replace('\\', '\\\\'), line) for rx, repl in rx_dctvals.items()][-1]
        """
        version 3.7-
        for rx, repl in rx_dctvals.items():
            line = rx.sub(repl.replace('\\', '\\\\'), line)
        return line
        """

    except Exception as erreur:
        print(f'convert_format: {erreur}')

# fonction pour bien définir les délimitations entre les mots dans les regex et pour échapper les caractères spéciaux.
def to_regex(x):

    r = []
    if x[0].isalnum() or x[0] == '_':
        r.append(r'(?<![^\W])')
    else:
        if any(l.isalnum() or l=='-' for l in x):
            r.append(r'\B')
    r.append(re.escape(x))
    if x[-1].isalnum() or x[-1] == '_':
        r.append(r'\b')
    else:
        if any(l.isalnum() or l=='-' for l in x):
            r.append(r'\B')
    return "".join(r)

# fonction qui extrait les entités nommées en se basant sur le package ne_chunk et qui pos tag tous les mots également
# elle renvoie le résultat sous forme d'une liste de tuples.
def extract_entities(doc):

    # on tokenise et on extrait les entités nommées avec ne_chunk pour chaque phrase.
    return list(map(lambda sent: tree2conlltags(ne_chunk(pos_tag(word_tokenize(sent)))), sent_tokenize(doc)))

def main():

    try:

        with ExitStack() as stack:
            
            file = stack.enter_context(open(sys.argv[2], 'r', encoding='utf-8'))
            # fichier d'extraction des entités nommées avec étiquettes non standards 

            result_file_ner_standard = stack.enter_context(open(sys.argv[3], 'w', encoding='utf-8'))

            pos_table = load_pos_table()
            content = file.read()

            # on écrit un mot par ligne dans le fichier de résultats avec son POS et son NER (séparés par une tabulation (format universel ou standard)
            # grâce à une list comprehension
            [[result_file_ner_standard.write(convert_format(f'{name}\t{tag}\t{ner}\n', {**pos_table, **dict_ner})) for name, tag, ner in tup] for tup in zip(*(extract_entities(content)))]  

    except Exception as error:       
        print(f'main error : {error}')

if __name__ == '__main__':
    main()
