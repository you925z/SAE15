import csv

with open("C:/Users/ouamr/SAE15/enquete-police-municipal.csv", newline='', encoding='utf-8') as f:
    csvreader = csv.reader(f, delimiter=',') 
    header = next(csvreader)  # saute la première ligne (les titres des colonnes)

#             CREER DES DICTIONNAIRE POUR CHAQUE DONNE
    departement = []
    communes = []
    habitants = []
    mise_en_commun_agent_municipal_commune = []
    agents_police = []
    asvp = []
    gardes_champetres = []
    maitre_chien = []
    chien_police = []
    commune_brigade_cynophile = []

#               DEFINIT CHAQUE LIGNE A CHAQUE DONNEES 

    for ligne in csvreader:
        departement.append(ligne[0])
        communes.append(ligne[1])
        habitants.append(ligne[2])
        mise_en_commun_agent_municipal_commune.append(ligne[3])
        agents_police.append(ligne[4])
        asvp.append(ligne[5])
        gardes_champetres.append(ligne[6])
        maitre_chien.append(ligne[7])
        chien_police.append(ligne[8])
        commune_brigade_cynophile.append(ligne[9])
    
#                  VOIR N PREMIERE LIGNES 

#    for i, ligne in enumerate(lecteur, start=1):
#        print(ligne)
#        if i >= 5:  # ici on en a 5 
#            break 


#                  NOMBRE DE VILLE DANS UN DEPARTEMENT 

# def nb_ville_dep(filename):
    #res = {}

#    with open(filename, newline='', encoding='utf-8') as f:
#        lecteur = csv.DictReader(f, delimiter=',')

#        for row in lecteur:
#            dep = row.get('departement')

#            if dep:
#                dep = dep.strip().upper()  # retire les espaces et met tout en majuscule
#                if dep.isdigit():          # si c’est un numéro
#                    dep = dep.zfill(2)     # ajoute un 0 devant (ex: '1' → '01')
#                res[dep] = res.get(dep, 0) + 1

#    return res

#fichier_csv = r"C:\Users\ouamr\SAE15\enquete-police-municipal.csv"

#resultat = nb_ville_dep(fichier_csv)

#print("Nombre de villes par département :")
#for dep, nb in sorted(resultat.items()):
#    print(f"Département {dep} : {nb} villes")