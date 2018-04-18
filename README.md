# ASMA BackEnd
### Unité d'Enseignement

- MIF11 - Projet d'Orientation en M2
- Encadrant: Fabien DUCHATEAU
- [Page du sujet](http://liris.cnrs.fr/~fduchate/ens/MIF20/sujets/2016-2017/sujet-integration.pdf)

## Requeriments

* Python 3.5
* Django 1.10.5
* MySQL 5.7.17

# Démarrage

Rentrer dans la BD Mysql et exécuter. À vous de modifier le nom et le pass de l'utilisateur, si c'est le cas vous pouvez modifier le fichier `TER/settings.py` pour indiquer le nom, password et nom de la BD.

```mysql
CREATE DATABASE TER;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin123'; 
CREATE DATABASE TER CHARACTER SET UTF8;
GRANT ALL PRIVILEGES ON TER.* TO admin@localhost;
FLUSH PRIVILEGES;
```

Rentrer dans le dossier du projet et exécuter

```bash
> cd TER_BACK_END
> ./manage.py makemigrations services
> ./manage.py migrate
> ./manage createsuperuser
```
Éxecutez dans la BD:
```mysql

ALTER TABLE TER.services_geoname MODIFY COLUMN name VARCHAR(10000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE TER.services_geoname
    CONVERT TO CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
    

ALTER TABLE TER.services_tag MODIFY COLUMN `value` VARCHAR(300)
    CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE TER.services_tag
    CONVERT TO CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

```

# Getting started
### Pour exécuter le serveur:
```bash
./manage.py runserver
```
Ça lance l'application dans [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Pour exécuter l'importation:
#### OpenStreetMap
```bash
./manage.py importation --skip-geonames fichier.xml
```
#### GeoNames
```bash
./manage.py importation --skip-osm fichier.txt 
./manage.py importation fichier.txt  --skip-osm -file3 featureCode.txt
```

### Pour exécuter une correspondance pour une entité specifique GN
```bash
./manage.py correspondance [geoname_id]
```






