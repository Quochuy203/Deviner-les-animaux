#Ajoute un nouvel animal dans zoo_etendu.csv en posant les questions une par une.
#Utilisation (dans le terminal, dossier du projet) :
#     python3 ajouter_animal.py                  -> modifie zoo_etendu.csv
#     python3 ajouter_animal.py autre_fichier.csv
#
# A tout moment, tapez 'q' pour quitter sans rien enregistrer.

import shutil
import sys
from pathlib import Path

import pandas as pd

CSV_PAR_DEFAUT = 'zoo_etendu.csv'

CLASSES_FR = {1: 'Mammifère', 2: 'Oiseau', 3: 'Reptile', 4: 'Poisson',
              5: 'Amphibien', 6: 'Insecte', 7: 'Invertébré'}

# Mêmes questions que dans le notebook. Si vous ajoutez une colonne au CSV, ajoutez-la ici aussi
# (sinon une question générique sera posée).
QUESTIONS = {
    'hair':     "A-t-il des poils ?",
    'feathers': "A-t-il des plumes ?",
    'eggs':     "Pond-il des œufs ?",
    'milk':     "Produit-il du lait (allaite-t-il ses petits) ?",
    'airborne': "Peut-il voler ?",
    'aquatic':  "Vit-il dans l'eau ?",
    'predator': "Est-ce un prédateur ?",
    'toothed':  "A-t-il des dents ?",
    'backbone': "A-t-il une colonne vertébrale ?",
    'breathes': "Respire-t-il de l'air (poumons) ?",
    'venomous': "Est-il venimeux ?",
    'fins':     "A-t-il des nageoires ?",
    'legs':     "Combien de pattes a-t-il ?",
    'tail':     "A-t-il une queue ?",
    'domestic': "Est-il domestique ?",
    'catsize':  "Est-il de la taille d'un chat ou plus grand ?",
    'herbivore':  "Mange-t-il surtout des végétaux (herbe, feuilles, graines, fruits, nectar) ?",
    'omnivore':   "Mange-t-il à la fois des végétaux et des animaux (omnivore) ?",
    'social':     "Vit-il en groupe (troupeau, banc, meute, colonie, volée) ?",
    'heavy':      "Pèse-t-il plus qu'un humain adulte (plus de 70 kg) ?",
    'small':      "Pèse-t-il moins de 2 kg ?",
    'tropical':   "Vit-il surtout dans les régions chaudes (tropiques, savane) ?",
    'cold':       "Vit-il surtout dans les régions froides (pôles, toundra, mers froides) ?",
    'desert':     "Vit-il dans les déserts ou les régions arides ?",
    'nocturnal':  "Est-il surtout actif la nuit ?",
    'arboreal':   "Vit-il ou se perche-t-il dans les arbres ou les buissons ?",
    'burrows':    "Vit-il sous terre ou enfoui dans le sol / le sable / la vase (terrier) ?",
    'freshwater': "Vit-il en eau douce (rivières, lacs, étangs) ?",
    'horns':      "A-t-il des cornes ou des bois ?",
    'long_neck':  "A-t-il un cou très long ?",
    'ruminant':   "Rumine-t-il (remâche-t-il son herbe, comme une vache) ?",
    'songbird':   "Est-ce un petit oiseau chanteur (passereau) ?",
}

OUI = ('oui', 'o', 'yes', 'y', '1')
NON = ('non', 'n', 'no', '0')


class Quitter(Exception):
    pass


def saisir(invite):
    rep = input(invite).strip()
    if rep.lower() in ('q', 'quitter'):
        raise Quitter
    return rep


def demander_nom():
    while True:
        nom = saisir("Nom de l'animal (en minuscules, ex. tiger) : ").lower()
        if nom and nom.replace(' ', '').replace('-', '').isalpha():
            return nom
        print("   Nom invalide : utilisez seulement des lettres (a-z).")


def demander_oui_non(question):
    while True:
        rep = saisir(f"{question}  (oui / non) -> ").lower()
        if rep in OUI:
            return 1
        if rep in NON:
            return 0
        print("   Répondez par oui ou non.")


def demander_pattes(question):
    while True:
        rep = saisir(f"{question}  (nombre entier, ex. 0, 2, 4, 6, 8) -> ")
        if rep.isdigit() and int(rep) <= 100:
            return int(rep)
        print("   Entrez un nombre entier (0 ou plus).")


def demander_classe():
    print("Classe de l'animal :")
    for k, v in CLASSES_FR.items():
        print(f"   {k} = {v}")
    while True:
        rep = saisir("Numéro de la classe (1 à 7) -> ")
        if rep.isdigit() and int(rep) in CLASSES_FR:
            return int(rep)
        print("   Entrez un nombre entre 1 et 7.")


def ajouter_un_animal(chemin):
    df = pd.read_csv(chemin)
    colonnes = list(df.columns)
    features = [c for c in colonnes if c not in ('animal_name', 'class_type')]

    nom = demander_nom()
    if nom in set(df['animal_name']):
        print(f"\n« {nom} » existe déjà dans {chemin.name}.")
        if demander_oui_non("Ajouter quand même une variante avec le même nom ?") == 0:
            print("Rien n'a été modifié.")
            return False

    print(f"\nRépondez aux questions pour « {nom} » :\n")
    valeurs = {'animal_name': nom}
    for col in colonnes:
        if col in ('animal_name', 'class_type'):
            continue
        question = QUESTIONS.get(col, f"Valeur de « {col} » (oui = 1 / non = 0) ?")
        valeurs[col] = demander_pattes(question) if col == 'legs' else demander_oui_non(question)
    print()
    valeurs['class_type'] = demander_classe()

    # Résumé
    print("\n--- Résumé ---")
    print(f"Animal : {nom}   |   Classe : {CLASSES_FR[valeurs['class_type']]}")
    print("Caractéristiques à 1 :", ", ".join(f for f in features if f != 'legs' and valeurs[f] == 1) or "(aucune)")
    print(f"Pattes : {valeurs['legs']}")

    # Attention : animaux identiques ? Le jeu ne pourra pas les distinguer.
    meme = (df[features] == pd.Series({f: valeurs[f] for f in features})).all(axis=1)
    jumeaux = df.loc[meme, 'animal_name'].tolist()
    if jumeaux:
        print(f"\nAttention : {jumeaux} ont exactement les mêmes caractéristiques.")
        print("Le jeu ne pourra pas les distinguer de « " + nom + " ».")

    if demander_oui_non("\nEnregistrer cet animal dans le fichier ?") == 0:
        print("Annulé, rien n'a été modifié.")
        return False

    # Sauvegarde de sécurité puis écriture
    sauvegarde = Path(str(chemin) + '.bak')
    shutil.copy(chemin, sauvegarde)
    nouvelle_ligne = pd.DataFrame([valeurs], columns=colonnes)
    df = pd.concat([df, nouvelle_ligne], ignore_index=True)
    df = df.sort_values('animal_name', kind='stable').reset_index(drop=True)   # garde l'ordre alphabétique
    df.to_csv(chemin, index=False, encoding='utf-8')
    print(f"\n« {nom} » ajouté ({len(df)} animaux au total). Copie de sécurité : {sauvegarde.name}")
    return True


def main():
    chemin = Path(sys.argv[1] if len(sys.argv) > 1 else CSV_PAR_DEFAUT)
    if not chemin.exists():
        print(f"Fichier introuvable : {chemin}  (lancez le script dans le dossier du projet)")
        return 1
    try:
        while True:
            ajouter_un_animal(chemin)
            if demander_oui_non("\nAjouter un autre animal ?") == 0:
                break
    except Quitter:
        print("\nInterrompu, rien n'a été enregistré pour l'animal en cours.")
    except (EOFError, KeyboardInterrupt):
        print("\nInterrompu.")
    print("Au revoir ! Relancez les cellules du notebook pour prendre en compte les nouveaux animaux.")
    return 0


if __name__ == '__main__':
    sys.exit(main())