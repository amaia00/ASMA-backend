DROP DATABASE TER;

CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin123'; 

CREATE DATABASE TER CHARACTER SET UTF8;

GRANT ALL PRIVILEGES ON TER.* TO admin@localhost;

FLUSH PRIVILEGES;


./manage.py makemigrations services
./manage.py migrate

Execute test algo
./manage.py import --skip-geonames --skip-osm  ""


Execute osm importation
./manage.py import TER/xml_files/andorra-latest.xml  --skip-geonames


Execute geonames importation
./manage.py import TER/xml_files/AD.txt  --skip-osm -file3 TER/xml_files/featureCodes_en.txt 


./manage.py correspondance 8224609
