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


./manage.py correspondance 8224609


ps aux | grep mysql
kill -9 8922
mysql.server stop
mysql.server start