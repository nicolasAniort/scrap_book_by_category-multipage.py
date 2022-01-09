import csv
import shutil
import urllib
import datetime
#import urlopen
import requests
import os
from typing import List, Union, Any
from bs4 import BeautifulSoup


prefix_url_category = "https://books.toscrape.com/catalogue/category/books/"
suffix_url_category = "/index.html"
categorie = "fiction"
compteur: int
url_category = "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
url_prefix_livre: str = "https://books.toscrape.com/catalogue"
#infos_livre_tr: List
infos_livre_tr = []
infos_livre_categorie = []
url_recup: str
cpt_page: str

def recuperation_url():
    url_recup = input('Entrez l\'url à traiter : ')
    #print (url_recup)
    return url_recup

def extractiondepage(url_recup):
    # lien de la page à scrapper
    reponse = requests.get(url_category)
    page_cat = reponse.content
    # transforme (parse) le HTML en objet BeautifulSoup
    soup_cat: BeautifulSoup = BeautifulSoup(page_cat, 'html.parser')
    compteur_de_page(soup_cat)


def compteur_de_page(soup_cat: BeautifulSoup):
    # recuperation d'un objet soup contenant les <a> de la categorie product_pod
    #soup_cat: BeautifulSoup = soup_cat
    soup_list_article = soup_cat.find("article", class_="product_pod")
    soup_list_a = soup_list_article.find_all_next('a')
    nbdeligne: int = len(soup_list_a)
    #li_next recoit la valeur de la balise next si elle existe dans la page
    li_next = soup_cat.find(class_="next").next
    #print(str("compteur de page " + li_next['href']))
    #
    if li_next != "":
        li_current: str = soup_cat.find(class_="current").text
        li_current_clean = li_current.replace("\n", "")
        li_current_cleantwo = li_current_clean.replace(" ", "")
        taille_chaine = len(li_current_cleantwo)
        placeof = li_current_cleantwo.index('of')
        nbpagenum = li_current_cleantwo[(placeof + 2):taille_chaine]
        cpt_page = nbpagenum
        extractionlistelivre(cpt_page, nbdeligne, soup_list_a)
    else:
        nbpagenum = 1
        extractionlistelivre(nbpagenum, nbdeligne, soup_list_a)

def extractionlistelivre(nombrepagenum, nombredeligne, soup_liste_a):
    a = 0
    # boucle alimentant la liste d'url de livre
    while a < (int(nombrepagenum)):
        cptpage = a
        for j in range(0, nombredeligne):
            if ((j % 2 == 0) and (j < 40)):
                # nom de categorie
                categories = categorie
                # url du livre
                cleaner_url_livre: str = soup_liste_a[j].get("href")
                #url_livre_ok = cleaner_url_livre.replace('../../..', str(url_prefix_livre))
                product_page_urls = cleaner_url_livre.replace('../../..', str(url_prefix_livre))
                reponse = requests.get(product_page_urls)
                page_cat = reponse.content
                # transforme (parse) le HTML en objet BeautifulSoup
                soup = BeautifulSoup(page_cat, 'html.parser')
                information_livre = []
                information_livre = etl(product_page_urls,soup)
                upc = information_livre[1]
                title =information_livre[2]
                price_including_tax = information_livre[3]
                price_excluding_tax = information_livre[4]
                number_available = information_livre[5]
                product_description = information_livre[6]
                category = information_livre[7]
                review_rating = information_livre[8]
                image_url = information_livre[9]

                infos_livre_categorie.append([categories, product_page_urls, upc, title, price_including_tax,
                                         price_excluding_tax, number_available, product_description, category,
                                         review_rating, image_url])

        a =  cptpage + 1
    #construction de l'entete
    en_tete = ["categories", "urls", "titres", "url de l'image de couverture", "urls", "upcs", "titre", "prix TTC", "prix HT", "nombre de livres disponibles", "description",
               "categories", "nombre d'étoile", "url de l'image de couverture"]
    #construction des lignes par livre
    #infos_livre_categorie = [list_categorie, list_href, list_titre, list_url_img]
    #infos_livre_categorie = [categories,product_page_urls, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url]

    compt = len(infos_livre_categorie)
    horodate = datetime.datetime.now()
    annee = horodate.strftime("%A")
    heure = horodate.strftime("%H")
    minute = horodate.strftime("%M")
    seconde = horodate.strftime("%S")
    # Génération du fichier csv
    charger_donnees("donnees_categorie_"+categorie+"-"+annee+heure+minute+seconde+".csv", en_tete, compt, infos_livre_categorie)
# charger les données dans un fichier csv
def charger_donnees(nom_fichier, en_tete, compt, infos_livre_categorie):

    with open(nom_fichier, 'w') as fichier_csv:
        try:
            #creation du csv
            writer = csv.writer(fichier_csv, delimiter=',')
            #creation de la ligne d'entete du fichier
            writer.writerow(en_tete)
            #compteur recevant le nombre de livre
            cpt = int(compt/2)
            for i in range(0, cpt):
             writer.writerow(infos_livre_categorie[i])
        except:
            print("ce fichier existe dèjà!veuillez supprimer le fichier ou attendre 1 minutes avant de relancer le script. Merci")
#recuperation des infos d'un livre
def etl(url,soup):
    # lien de la page à scrapper
    #reponse = requests.get(url)
    #page = reponse.content

    # transforme (parse) le HTML en objet BeautifulSoup
    soup = soup

    # récupération de L'url de la page du produit
    #print("url utilisée pour le livre" + url)
    product_page_urls = url
    # récupération de l'upc
    upc = soup.find("th", text="UPC").find_next_sibling("td").text
    # récupération du titres ok
    title = soup.find("h1").text
    # récupération du prix TTC
    price_including_tax = soup.find("th", text="Price (incl. tax)").find_next_sibling("td").text
    price_including_tax: str = price_including_tax
    # récupération du prix HT
    price_excluding_tax = soup.find("th", text="Price (excl. tax)").find_next_sibling("td").text
    price_excluding_tax: str = price_excluding_tax
    # récupération du nombre disponible
    chaine_nombre_stock: str = soup.find("th", text="Availability").find_next_sibling("td").text
    loc_debut_chaine: int = chaine_nombre_stock.find('(') + 1
    loc_fin_chaine: int = chaine_nombre_stock.find(' available)')
    number_available: int = chaine_nombre_stock[loc_debut_chaine: loc_fin_chaine]
    number_available: str = number_available
    # récupération de la descriptions ok
    product_description = soup.find("p", class_="").text
    # récupération de la categorie du produit prendre les li à l'envers
    category = soup.find("a", text="Books").find_next("a").text
    # récupération de review rating
    balise_etoile = soup.find("p", class_="instock availability").find_next("p").attrs
    class_etoile: str = balise_etoile['class']
    chaine_class_etoile = class_etoile[1]
    if chaine_class_etoile == 'Five':
        review_rating = 5
    elif chaine_class_etoile == "Four":
            review_rating = 4
    elif chaine_class_etoile == 'Three':
            review_rating = 3
    elif chaine_class_etoile == 'Two':
            review_rating = 2
    elif chaine_class_etoile == 'One':
            review_rating = 1
    else:
        review_rating = 0
    review_rating: str = review_rating
    # récupération de l'url de l'image
    div_img_tag = soup.find("div", class_="item active")
    image = div_img_tag.img
    image_url_brute = image['src']
    image_url = image_url_brute.replace('../..', 'https://books.toscrape.com')
    #telechargement de l'image dans un dossier
    prefixe_dir = 'img_livre/'
    dir_img_livre = prefixe_dir + upc +'/'
    file_img_libre = dir_img_livre + upc + '.jpg'

    try:
        os.mkdir(prefixe_dir + upc +'/')
    except:

        shutil.rmtree(dir_img_livre)
        os.mkdir(dir_img_livre)
    #telechargement de l'image et creation du fichier en local
    urllib.request.urlretrieve(image_url, file_img_libre)
    infos_livre = [product_page_urls, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url]

    return infos_livre


    '''for i in range(len(infos_livre)):
        if infos_livre[i] == '':
            infos_livre[i].replace('', "champ vide")
            print(infos_livre[i])
            infos_livre_tr.append(infos_livre[i])
'''

# lanceur
extractiondepage(recuperation_url())