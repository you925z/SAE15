import csv

with open("C:/Users/ouamr/SAE15/enquete-police-municipal.csv", newline='', encoding='utf-8') as f:

    lecteur = csv.reader(f, delimiter=';')
    for i, ligne in enumerate(lecteur, start=1):
        print(ligne)
        if i >= 1:
            break
