# -*- coding: utf-8 -*-
#!usr/bin/env python3

import nltk
from nltk import pos_tag, word_tokenize
import sys

"""
Question 2.1
programme Python utilisant le package parse et la fonction pos_tag pour désambiguïser morpho-syntaxiquement le texte du fichier sys.argv[1]
en appliquant une règle morpho-syntaxique particulière <DT>?<JJ>*<NN> ou plusieurs sous la forme d'un dictionnaire. 
Le résultat de ce module sera mis dans le fichier sys.argv[2] en affichant le chunk + POS et le chunk sous forme de string.
sys.argv[1] = input file
sys.argv[2] = output file
"""

# si il n'y a pas deux arguments définis, on met fin au script
if len(sys.argv[1:]) != 2:
    print('Nombre d\'arguments incorrect ! 2 requis')
    sys.exit()

# dictionnaire des regles strites pour le RegexpParser pour généraliser
rules = {'Determinant-Adjectif-Nom': 'Compound : {<DT><JJ><NN>}', 'Adjectif-Nom':'Compound : {<JJ><NN>}', 'Nom-Nom':'Compound : {<NN><NN>}',
'Adjectif-Nom-Nom': 'Compound : {<JJ><NN><NN>}', 'Adjectif-Adjectif-Nom': 'Compound : {<JJ><JJ><NN>}'}

# fonction qui parse une phrase en appliquant une règle au RegexpParser
def parse_sentence(text, rule):
    
    pos_sentence = pos_tag(word_tokenize(text))
    if pos_sentence:
        parser = nltk.RegexpParser(rule)
        # on utilise le module nltk.parse pour parser la phrase
        return parser.parse(pos_sentence)
        # si aucun chunk n'a été trouvé, on retourne None sinon on, retourne le tree du chunk.
    else:
        return None

# fonction qui extrait sous forme de string les trees des chunks en question avec leur TAG
# sous forme d'une liste de tuples (word, pos)
# fonction générique qui marche pour plusieurs tokens respectant une règle. Ici, il n'y a qu'une règle.
def extract_phrases(my_tree, phrase):
    
    my_phrases = []
    if my_tree.label() == phrase:
        my_phrases.append(my_tree.copy(True))

    # recursivité pour parcourir les subtrees du child du token
    for child in my_tree:
        if type(child) is nltk.Tree:
            list_of_phrases = extract_phrases(child, phrase)
            if len(list_of_phrases) > 0:
                my_phrases.extend(list_of_phrases)
    return my_phrases

# fonction principale, on va extraire les chunks respectant les différentes règles en les triant par règle
def main():


    try:

        with open(sys.argv[1], 'r', encoding='utf-8') as source, open(sys.argv[2], 'w', encoding='utf-8') as result:

            # on lit le fichier dans sa totalité
            text = source.read()
            # pour chacune des regles que nous avons à appliquer
            for name, rule in rules.items():
                result.write(f'\nRègle : {name}\n\n')
                # on extrait la liste des chunks sous forme de Tree
                chunked = parse_sentence(text, rule)
                if chunked:
                    # on ne garde que les chunks respectant la règle 'Compound' actuelle
                    list_of_noun_phrases = extract_phrases(chunked, 'Compound')
                    # on affiche les chunks avec POS puis sans POS dans le fichier de sortie
                    # une séquence de tokens par ligne
                    for phrase in list_of_noun_phrases:
                        result.write(f'{phrase} {"_".join([x[0] for x in phrase.leaves()])}\n')

    except Exception as error:
        print(f'main error : {error}')

if __name__ == '__main__':
    main()
