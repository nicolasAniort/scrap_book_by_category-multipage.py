import csv
import urllib
import urlopen
import requests
import os

from bs4 import BeautifulSoup


# charger la donnée dans un fichier csv
def charger_donnees(nom_fichier, en_tete, infos_livre):

    with open(nom_fichier, 'w') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=',')
        writer.writerow(en_tete)
        writer.writerow(infos_livre)

def etl():
    # lien de la page à scrapper
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    reponse = requests.get(url)
    page = reponse.content

    # transforme (parse) le HTML en objet BeautifulSoup
    soup = BeautifulSoup(page, 'html.parser')

    # récupération de L'url de la page du produit
    #print(url)
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
    # print(div_img_tag)
    image = div_img_tag.img
    # print(image['src']
    image_url_brute = image['src']
    image_url = image_url_brute.replace('../..', 'https://books.toscrape.com')
    #telechargement de l'image dans un dossier
    prefixe_dir = 'img_livre/'
    dir_img_livre = prefixe_dir + upc +'/'
    file_img_libre = dir_img_livre + upc + '.jpg'
    #os.mkdir(prefixe_dir)
    os.mkdir(prefixe_dir + upc +'/')
    #telechargement de l'image et creation du fichier en local
    urllib.request.urlretrieve(image_url, file_img_libre)

    en_tete = ["urls", "upcs", "titre", "prix TTC", "prix HT", "nombre de livres disponibles", "description",
               "categories", "nombre d'étoile", "url de l'image de couverture"]

    urls = product_page_urls
    upcs = upc
    titres = title
    prixttc = price_including_tax
    prixht = price_excluding_tax
    nombre_disponible = number_available
    # si descriptions_vrac est vide titres ne sse chargera pas dans le csv
    descriptions = product_description
    categories = category
    etoiles = review_rating
    url_de_limage_de_couverture = image_url
    infos_livre = [product_page_urls, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url]

    charger_donnees("donnees.csv", en_tete, infos_livre)


etl()