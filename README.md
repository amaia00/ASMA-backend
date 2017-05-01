DROP DATABASE TER;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin123'; 
CREATE DATABASE TER CHARACTER SET UTF8;
GRANT ALL PRIVILEGES ON TER.* TO admin@localhost;
FLUSH PRIVILEGES;


./manage.py makemigrations services
./manage.py migrate

Execute test algo
./manage.py importation --skip-geonames --skip-osm  ""


Execute osm importation
./manage.py importation TER/xml_files/andorra-latest.xml  --skip-geonames


Run server
python manage.py runserver

Execute geonames importation
./manage.py import TER/xml_files/AD.txt  --skip-osm -file3 TER/xml_files/featureCodes_en.txt 
./manage.py importation TER/xml_files/FR.txt  --skip-osm


./manage.py correspondance 8224609


ps aux | grep mysql
kill -9 8922
mysql.server stop
mysql.server start


--> Pour lancer le processus de correspondance global
TRUNCATE TABLE services_correspondencevalide
TRUNCATE TABLE services_correspondenceinvalide
TRUNCATE TABLE services_correspondenceentity


ALTER TABLE TER.services_geoname MODIFY COLUMN name VARCHAR(10000)
    CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE
    TER.services_geoname
    CONVERT TO CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

DELETE FROM services_geoname
WHERE correspondence_check = 0
    
    var1 varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
    
    

ALTER TABLE TER.services_tag MODIFY COLUMN value VARCHAR(300)
    CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE
    TER.services_tag
    CONVERT TO CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;




DELETE FROM services_tag;
DELETE FROM services_node;
DELETE FROM services_way;
DELETE FROM services_relation;


TRUNCATE TABLE services_geonames;



TRUNCATE TABLE services_correspondenceentity;

TRUNCATE TABLE services_correspondencevalide;

TRUNCATE TABLE services_correspondenceinvalide;




