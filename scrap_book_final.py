import csv
from typing import List, Union, Any

import requests
from bs4 import BeautifulSoup

prefix_url_category = "https://books.toscrape.com/catalogue/category/books/"
suffix_url_category = "/index.html"
categorie = "fiction"
compteur: int
url_category = "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html"



def compteur_de_page(url_category):




# charger les données dans un fichier csv
def charger_donnees(nom_fichier, en_tete, compt, infos_livre_categorie):
    with open(nom_fichier, 'w') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=',')
        writer.writerow(en_tete)
        infos_livre_categorie: List
        cpt = compt
        for i in range(0, cpt):
            liste_livre_ligne: List[Any] = []
            for i1 in range(0, 4):
                liste_livre_ligne.append(infos_livre_categorie[i1][i])
            writer.writerow(liste_livre_ligne)

def extracteurdedonnees():

    url_prefix_category = url_category.replace('/index.html', '')
    reponse = requests.get(url_category)
    page_cat = reponse.content

    # transforme (parse) le HTML en objet BeautifulSoup
    soup_cat: BeautifulSoup = BeautifulSoup(page_cat, 'html.parser')

    # recuperation d'un objet soup contenant les <a> de la categorie product_pod
    soup_list_article = soup_cat.find("article", class_="product_pod")
    soup_list_a = soup_list_article.find_all_next('a')
    # hrefsextraits = soup_list_a['href']
    nbdeligne: int = len(soup_list_a)
    li_next = soup_cat.find(class_="next").next
    print(str(li_next['href']))
    if li_next != "":

        li_current: str = soup_cat.find(class_="current").text
        print(li_current)
        li_current_clean = li_current.replace("\n", "")
        li_current_cleantwo = li_current_clean.replace(" ", "")
        taille_chaine = len(li_current_cleantwo)
        placeof = li_current_cleantwo.index('of')
        nbpagenum = li_current_cleantwo[(placeof + 2):taille_chaine]
        cptpage = 1
        suffix_url_category_new = 'Page-' + cptpage + '.html'
        #url_category_new = str(url_category) + str(suffix_url_category_new)
    else:
        nbpagenum = 1
        print(nbpagenum)
    # creation des listes recevant les url des href
    list_href = []
    list_url_img = []
    list_titre = []
    list_categorie = []
    a = 1
    # boucle alimentant la liste d'url de livre
    while a < nbpagenum + 1:
        cptpage = a
        
        for j in range(0, nbdeligne):
            if ((j % 2 == 0) and (j < 40)):
                # nom de categorie
                list_categorie.append(categorie)
                # url du livre
                cleaner_url_livre: str = soup_list_a[j].get("href")
                url_livre_ok = cleaner_url_livre.replace('../../../', str(prefix_url_category))
                list_href.append(url_livre_ok)
                # titre du livre
                titrelivre: str = soup_list_a[j].find_next("img").get('alt')
                # print(titrelivre)
                list_titre.append(titrelivre)
                # url de l'image de couverture
                cleaner_url_img: str = soup_list_a[j].find_next("img").get("src")
                url_img_ok = cleaner_url_img.replace('../../../', str(prefix_url_category))
                # print(url_img_ok)
                list_url_img.append(url_img_ok)
    #construction de l'entete
    en_tete = ["categories", "urls", "titres", "url de l'image de couverture"]
    #construction des lignes par livre
    infos_livre_categorie = [list_categorie, list_href, list_titre, list_url_img]
    compteur: int = len(list_href)
    compt = compteur
    # Génération du fichier csv
    charger_donnees("donnees_par_categorie.csv", en_tete, compt, infos_livre_categorie)


# lanceur
extractionlistelivre()
