import csv

classe = []
annee = []
code_region = []
unite_de_compte = []
millPOP = []
millLOG = []
faits = []
POP = []
LOG = []
tauxpourmille = []


with open('fichier.csv', mode='r', encoding='utf-8') as fichier:
    csvreader = csv.reader(fichier, delimiter=';')
    header = next(csvreader)

    # Implémente les valeurs dans leurs listes respectives
    for ligne in csvreader:
        classe.append(ligne[0])
        annee.append(ligne[1])
        code_region.append(ligne[2])
        unite_de_compte.append(ligne[3])
        millPOP.append(ligne[4])
        millLOG.append(ligne[5])
        faits.append(ligne[6])
        POP.append(ligne[7])
        LOG.append(ligne[8])
        tauxpourmille.append(ligne[9])
    #-----------------------------------------------------


#-------------------------------------------------------------------------------------------------------------------------------------------------

Nb_classe = {}
for i in range(len(classe)) :
    if classe[i] in Nb_classe:
        Nb_classe[classe[i]] += int(faits[i])
    else:
        Nb_classe[classe[i]] = int(faits[i])

Nb_classe = dict(sorted(Nb_classe.items(), key=lambda item: item[1], reverse=True)) #Trie le dictionnaire en fonction de la valeur du dico 

#-------------------------------------------------------------------------------------------------------------------------------------------------

region_touche = {}

for i in range(len(code_region)):
    region = code_region[i]
    nb_faits = int(faits[i])
    if region in region_touche:
        region_touche[region] += nb_faits
    else:
        region_touche[region] = nb_faits


region_touche = dict(sorted(region_touche.items(), key=lambda item: item[1], reverse=True)) #Trie le dictionnaire en fonction de la valeur du dico

#-------------------------------------------------------------------------------------------------------------------------------------------------

faits_par_annee = {}

for i in range(len(annee)):
    annee_complete = annee[i]
    if annee_complete in faits_par_annee:
        faits_par_annee[annee_complete] += int(faits[i])
    else:
        faits_par_annee[annee_complete] = int(faits[i])

faits_par_annee = dict(sorted(faits_par_annee.items())) # Trier les données par année

#-------------------------------------------------------------------------------------------------------------------------------------------------


# HTML
html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Endroits en France à éviter</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- NAV BAR -->
    <nav class="navbar">
        <ul>
            <li><a href="#faits/classe">Faits/Classe</a></li>
            <li><a href="#faits/region">Faits/Région</a></li>
            <li><a href="#faits/region(graph)">Faits/Région (Graph)</a></li>
            <li><a href="#Faits/Annuelle">Faits/Annuelle</a></li>
        </ul>
    </nav>
    <!-- FIN NAV BAR -->
    <h1>Quels sont les endroits en France qui sont dangereux ?</h1>
    <p>Avant d'aborder cela, il est essentiel de déterminer si une région est considérée comme <span style="color: rgb(202, 2, 119);">dangereuses</span> ou pas. Pour cela il faut analyser le/les faits le plus commis</p>
    <h2 id="faits/classe">Nombre de faits par classe</h2>
    <table>
        <tr>
            <th>Classe</th>
            <th>Nombre de faits</th>
        </tr>
"""

# Ajouter les données de Nb_classe
for classe, nb_faits in Nb_classe.items():
    html += f"""
        <tr>
            <td>{classe}</td>
            <td>{nb_faits}</td>
        </tr>
    """

html += """
    </table>
    <hr>
    <h2 id="faits/region">Nombre de faits par région</h2>
    <p>Ainsi, dans quelles régions ces <span style="color: rgb(202, 2, 119);">incidents</span> sont-ils principalement observés ? </p>
    <table>
        <tr>
            <th>Code Région</th>
            <th>Nombre de faits</th>
        </tr>
"""

# Ajouter les données de region_touche
for region, nb_faits in region_touche.items():
    html += f"""
        <tr>
            <td>{region}</td>
            <td>{nb_faits}</td>
        </tr>
    """

html += """
    </table>
    <hr>
    <h2 id="faits/region(graph)">Graphique : Nombre de faits par région</h2>
    <p>Les données numériques peuvent parfois être difficiles à interpréter. Il est donc pertinent de recourir à des <span style="color: rgb(202, 2, 119);">représentations visuelles </span>pour mieux comprendre la répartition des faits par région.</p>
    <canvas id="regionChart" width="800" height="400"></canvas>

    <script>
        const ctx = document.getElementById('regionChart').getContext('2d');
        const regionChart = new Chart(ctx, {
            type: 'doughnut', // Type de graphique circulaire
            data: {
                labels: [""" + ', '.join([f'"{region}"' for region in region_touche.keys()]) + """],
                datasets: [{
                    label: 'Nombre de faits',
                    data: [""" + ', '.join(map(str, region_touche.values())) + """],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                    ],
                    borderColor: '#000',  
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff'  // Couleur des labels dans la légende
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                const region = tooltipItem.label; // Obtenir la région
                                const value = tooltipItem.raw; // Obtenir la valeur
                                return `Code région : ${region}, Nombre de faits : ${value}`;
                            }
                        },
                        backgroundColor: '#0f1a25',  // Fond de l'infobulle
                        titleColor: '#ffffff',       // Couleur du titre
                        bodyColor: '#ffffff'         // Couleur du texte
                    }
                }
            }
        });
    </script>
    """


html += """
    <hr>
    <h2 id="Faits/Annuelle">Évolution annuelle du nombre de faits</h2>
    <p>Il est important d'analyser l'évolution des faits pour déterminer si leur fréquence <span style="color: rgb(202, 2, 119);">baissé</span> ou <span style="color: rgb(202, 2, 119);">augmenté</span>.</p>
    <canvas id="anneeEvolutionChart" width="800" height="400"></canvas>

    <script>
        const anneeCtx = document.getElementById('anneeEvolutionChart').getContext('2d');

        new Chart(anneeCtx, {
            type: 'line',  // Graphique en ligne
            data: {
                labels: [""" + ', '.join([f'"{annee}"' for annee in faits_par_annee.keys()]) + """],
                datasets: [{
                    label: 'Nombre de faits',
                    data: [""" + ', '.join(map(str, faits_par_annee.values())) + """],
                    borderColor: 'rgba(255, 255, 255, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.4  // Courbe lissée
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Nombre de faits'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Année'
                        }
                    }
                }
            }
        });
    </script>
    <div id="watermark"><u><b>Réalisé par :</b></u> <br><br> SINGH Mankarn <br> MOUGAMADOU K. Fadil</div>
</body>
</html>
"""

# Sauvegarder le fichier HTML
with open("index.html", "w", encoding="utf-8") as html_f:
    html_f.write(html)