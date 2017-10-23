# Mairies
Base de données sur les mairies de France

... in progress ...

### Lancer le code 

Enter dans le bon directory d'abord

Lancer mairies_V2.py : création de la base de données 
1. Dans le terminal, écrire : python3 mairies_V2
2. Output : le fichier database.csv et son homologue database.db sont mis à jour, et disponibles dans le folder static 

Lancer app.py : lance l'application Flask pour afficher la base sur un serveur local
1. Dans le terminal, écrire : python3 app.py
2. Output : une url s'affiche
3. Copier/coller l'url dans votre navigateur internet

### Important
- La base est grande, mais vous pouvez tester sur une base restreinte au département 01. Par défaut, le programme proposé ne construit la base que pour ce département. Si vous voulez tester pour la France entière, reprenez la section "Lancer le code" en remplaçant :
		- insee_01.csv PAR insee.csv (ligne 70 mairies_V2.py)
		- dpt01_db.csv PAR database.csv (ligne 98 mairies_V2.py ET ligne 36 index_mairies.html)

- La base de donnée est déja construite et disponible dans le folder static, vous pouvez l'afficher direcetment par le programme app.py 

### Description détaillée

0. Prérequis
	0.1. Base insee.csv de l'INSEE sur les mairies de France (code commune, ville, nom, 	prénom, date de naissance du maire) 
	0.2. Base code_postaux_insee.csv utilisée par La Poste (correspondance code 	commune avec code postal et coordonnées géographiques)

1. Fichier mairies_V2.py : création de la base de données 

	1.1. Définition de la base
		- classe Mairies, colonnes (code commune, code postal, ville, latitude, longitude, prénom maire, nom maire, naissance maire, date de premier mandat du maire, parti politique)

	1.2. Construction des lignes de la base
		- fonction build_db() : réupère les 7 premières colonne dans les base de l'INSEE
		- fonction scrap_party_date() : cherche dans les pages Wikipedia des communes les 2 colonnes date de premier mandat et parti politique

	1.3. Ecriture du .csv 
		- fonciton write_csv()

	1.4 Gestion des exceptions/erreurs
		- classe TableError : Wikipedia ne contient pas l'information à scraper
		- fonction no_accent() : contre les différences d'encodage


2. Fichier app.py : lance l'application Flask pour afficher la base sur un serveur local



### Notes
- Séparation des programmes de création et d'affichage de la base plus pratique pour le stockage de la base et pour travailler de manière séparée sur ces deux parties 
- Le scraping des 3 premiers résultats Google par reconnaissace du parti dans un large texte vient en complément de Wikipédia, car cette méthode est encore longue et couteuse à ce stade de développement.
