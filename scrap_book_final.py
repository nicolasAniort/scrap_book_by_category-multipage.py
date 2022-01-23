import csv
import shutil
import urllib
import datetime
import requests
import os
from typing import List, Union, Any
from bs4 import BeautifulSoup

prefix_url_category = "https://books.toscrape.com/catalogue/category/books/"
suffix_url_category = "/index.html"
compteur: int
url_prefix_livre: str = "https://books.toscrape.com/catalogue"
infos_livre_tr = []
infos_livre_categorie = []
url_rec: str
cpt_page: str

"""
interface de recuperation durl
"""
def recuperation_url():
    url_rec = input('Entrez l\'url à traiter : ')
    return url_rec
"""
creation de l'horodatage
"""
def horodater():
    horodate = datetime.datetime.now()
    annee = horodate.strftime("%A")
    heure = horodate.strftime("%H")
    mois = horodate.strftime("%m")
    #seconde = horodate.strftime("%S")
    horodatage_fichier: str = annee + heure + mois
    return horodatage_fichier

"""
creation d'un objet soup à partir de lurl saisie
renvoi de l'objet à la def compteur_de_page
"""
def extraction_de_page(url_rec):
    # lien de la page à scrapper
    retour = requests.get(url_rec)
    page_cat = retour.content
    # transforme (parse) le HTML en objet BeautifulSoup
    soup_cat: BeautifulSoup = BeautifulSoup(page_cat, 'html.parser')
    compteur_de_page(soup_cat, url_rec)
    return url_rec

def compteur_de_page(soup_cat: BeautifulSoup, url_rec):
    """
    Si la classe pager existe, il y a plusieurs pages, on va donc
    compter le nombre de pages à traiter pour la categorie concernée
    """
    vide=[]
    pager = soup_cat.select(".pager")
    if pager != vide:
        li_current: str = soup_cat.find(class_="current").text.replace("\n", "").replace(" ", "")
        taille_chaine = len(li_current)
        placeof = li_current.index('of')
        nbpagenum: int = li_current[(placeof + 2):taille_chaine]
        extractionlistelivre(nbpagenum, soup_cat, url_rec)
    else:
        nbpagenum = 1
        extractionlistelivre(nbpagenum, soup_cat, url_rec)

def extractionlistelivre(nombrepagenum: int, soup_cat, url_rec: str):
    """
        recuperation d'un objet soup contenant les <a> de la categorie product_pod
    """
    soup_list_a: BeautifulSoup = soup_cat.find("div", class_="image_container").find_all_next("a")
    if int(nombrepagenum) > 1 :
        #initalisation du compteur de boucle
        a = 1
        """
        tant que le compteur de boucle est inférieur au nombre de page  + 1
        """
        while a < (int(nombrepagenum) + 1):

            cptpage = a
            # lien de la page à scrapper
            reponse = requests.get(url_rec.replace("index.html","page-" + str(cptpage) + ".html"))
            page_cat = reponse.content
            # transforme (parse) le HTML en objet BeautifulSoup
            soup_cat: BeautifulSoup = BeautifulSoup(page_cat, 'html.parser')
            # recuperation d'un objet soup contenant les <a> de la categorie product_pod
            soup_list_article = soup_cat.find("article", class_="product_pod")
            soup_list_a_multi = soup_list_article.find_all_next('a')
            nombredeligne: int = len(soup_list_a_multi)

            if (int(nombrepagenum) > a):
                """
                boucles de recuperation de la liste de livres et des information des livres
                """
                for j in range(0, nombredeligne):
                    """
                    Condition si la liste est inferieure à 40 lignes récupérés ( soit inférieurs à 20 livres)
                    """
                    if ((j % 2 == 0) and (j < 40)):
                        print("boucle pmultiple")
                        # nom de categorie
                        categorie: str = url_rec.replace("https://books.toscrape.com/catalogue/category/books/", "").replace(
                            "/index.html", "")
                        print(str(nombrepagenum) + "_" +str(a) + "_" + str(cptpage) + url_rec + "_" + str(j) + "_" + str(categorie) + "_" +str(nombredeligne))
                        categories = categorie
                        # creation de l\'url du livre
                        cleaner_url_livre: str = soup_list_a_multi[j].get("href")
                        product_page_urls = cleaner_url_livre.replace('../../..', str(url_prefix_livre))
                        reponse = requests.get(product_page_urls)
                        page_cat = reponse.content
                        # transforme (parse) le HTML en objet BeautifulSoup
                        soup = BeautifulSoup(page_cat, 'html.parser')
                        information_livre = []
                        #appel de la definition d'extraction des informations du livre
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
                        # construction des lignes par livre
                        infos_livre_categorie.append([categories, product_page_urls, upc, title, price_including_tax,
                                                 price_excluding_tax, number_available, product_description, category,
                                                 review_rating, image_url])

                a =  cptpage + 1
            else:
                for j in range(0, nombredeligne-1):
                    print("boucle derniere page")
                    if ((j % 2 == 0) and (j < (nombredeligne-1))):
                        # nom de categorie
                        categorie: str = url_rec.replace("https://books.toscrape.com/catalogue/category/books/",
                                                         "").replace(
                            "/index.html", "")
                        print(
                            str(nombrepagenum) + "_" + str(a) + "_" + str(cptpage) + url_rec + "_" + str(j) + "_" + str(
                                categorie) + "_" + str(nombredeligne))
                        categories = categorie
                        # url du livre
                        cleaner_url_livre: str = soup_list_a_multi[j].get("href")
                        product_page_urls = cleaner_url_livre.replace('../../..', str(url_prefix_livre))
                        reponse = requests.get(product_page_urls)
                        page_cat = reponse.content
                        # transforme (parse) le HTML en objet BeautifulSoup
                        soup = BeautifulSoup(page_cat, 'html.parser')
                        information_livre = []
                        information_livre = etl(product_page_urls, soup)
                        upc = information_livre[1]
                        title = information_livre[2]
                        price_including_tax = information_livre[3]
                        price_excluding_tax = information_livre[4]
                        number_available = information_livre[5]
                        product_description = information_livre[6]
                        category = information_livre[7]
                        review_rating = information_livre[8]
                        image_url = information_livre[9]
                        # construction des lignes par livre
                        infos_livre_categorie.append([categories, product_page_urls, upc, title, price_including_tax,
                                                      price_excluding_tax, number_available, product_description,
                                                      category,
                                                      review_rating, image_url])
                        a = cptpage + 1
            #construction de l'entete
            en_tete = ["categories", "urls", "upcs", "titre", "prix TTC", "prix HT", "nombre de livres disponibles", "description",
                       "categories", "nombre d'étoile", "url de l'image de couverture"]
            #construction des lignes par livre
            compt = len(infos_livre_categorie)

    else:
            # lien de la page à scrapper
            reponse = requests.get(url_rec)
            page_cat = reponse.content
            # transforme (parse) le HTML en objet BeautifulSoup
            soup_cat: BeautifulSoup = BeautifulSoup(page_cat, 'html.parser')
            # recuperation d'un objet soup contenant les <a> de la categorie product_pod
            soup_list_article = soup_cat.find("article", class_="product_pod")
            soup_list_a_multi = soup_list_article.find_all_next('a')
            nombredeligne: int = len(soup_list_a_multi)

            for j in range(0, nombredeligne):
                print("boucle psimple")
                if ((j % 2 == 0) and (j < (nombredeligne + 1))):
                    # nom de categorie
                    categorie: str = url_rec.replace("https://books.toscrape.com/catalogue/category/books/", "").replace(
                        "/index.html", "")
                    categories = categorie
                    # url du livre
                    cleaner_url_livre: str = soup_list_a_multi[j].get("href")
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
                    # construction des lignes par livre
                    infos_livre_categorie.append([categories, product_page_urls, upc, title, price_including_tax,
                                             price_excluding_tax, number_available, product_description, category,
                                             review_rating, image_url])


        #construction de l'entete
            en_tete = ["categories", "urls", "upcs", "titre", "prix TTC", "prix HT", "nombre de livres disponibles", "description",
                   "categories", "nombre d'étoile", "url de l'image de couverture"]
        #construction des lignes par livre

            compt = len(infos_livre_categorie)
            #horodate = datetime.datetime.now()
            #annee = horodate.strftime("%A")
            #heure = horodate.strftime("%H")
            #minute = horodate.strftime("%M")
            #seconde = horodate.strftime("%S")
        # Génération du fichier csv
    charger_donnees("donnees_categorie_"+categorie+"-"+horodater()+".csv", en_tete, compt, infos_livre_categorie)
# charger les données dans un fichier csv
def charger_donnees(nom_fichier, en_tete, compt, infos_livre_categorie):
    print(len(infos_livre_categorie))
    with open(nom_fichier, 'w') as fichier_csv:
        try:
            #creation du csv
            writer = csv.writer(fichier_csv, delimiter=',')
            #creation de la ligne d'entete du fichier
            writer.writerow(en_tete)
            #compteur recevant le nombre de livre
            cpt = int(compt)
            for i in range(0, cpt):
             writer.writerow(infos_livre_categorie[i])
        except:
            print("ce fichier existe dèjà!veuillez supprimer le fichier ou attendre 1 minutes avant de relancer le script. Merci")
#recuperation des infos d'un livre
def etl(url,soup):
    # transforme (parse) le HTML en objet BeautifulSoup
    soup = soup

    # récupération de L'url de la page du produit
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
    prefixe_dir = 'img_livre' + '_'+ horodater() + '/'
    dir_img_livre = prefixe_dir + category +'_'+ upc +'/'
    file_img_libre = dir_img_livre + upc + '.jpg'
    try:
        os.mkdir(dir_img_livre)
    except:
        os.mkdir(prefixe_dir)
        os.mkdir(dir_img_livre)
    else:
        # suppression du dossier image existant avec fichiers contenus
        shutil.rmtree(prefixe_dir)
        os.mkdir(prefixe_dir)
        os.mkdir(dir_img_livre)
    #telechargement de l'image et creation du fichier en local
    urllib.request.urlretrieve(image_url, file_img_libre)
    infos_livre = [product_page_urls, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url]

    return infos_livre

# lanceur
extraction_de_page(recuperation_url())