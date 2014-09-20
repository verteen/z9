#!/bin/bash

if ! [ -n "$1" ]; then
	echo "Ошибка! Нет имени проекта"
	exit 1
fi

if [ $1 == "default" ]; then
	echo "Ошибка! test"
	exit 1
fi

# make new copy of directories
cd /var/z9/core/
cp -r default_app $1
mv $1 /var/z9/apps/
cd /var/z9/apps/$1

# configure conf-files for nginx and uwsgi
cd conf/
sed -e "s/{default}/$1/g" default.nginx.conf > $1.nginx.conf
sed -e "s/{default}/$1/g" default.uwsgi.ini > $1.uwsgi.ini
rm -f default.nginx.conf
rm -f default.uwsgi.ini
cd ../

# configure exceptions directory
cd exceptions/
sed -e "s/{default}/$1/g" default_exceptions.py > common.py
rm -f default_exceptions.py
cd ../

# configure default mappers.py in default project database
cd mappers/
sed -e "s/{default}/$1/g" default_mappers.py > common.py
rm -f default_mappers.py
cd ../

# configure default models module
cd models/
sed -e "s/{default}/$1/g" default_models.py > common.py
rm -f default_models.py
cd ../

# configure application.py and launcher
sed -e "s/{default}/$1/g" default_application.py > application.py
sed -e "s/{default}/$1/g" default_launcher.sh > launcher.sh
rm -f default_application.py
rm -f default_launcher.sh
chmod +x launcher.sh

# configure default bootstrap template
cd views/
sed -e "s/{default}/$1/g" default_bootstrap.html > bootstrap.html
rm -f default_bootstrap.html
cd ../

# setting up rights for the app directory
sudo chown www-data:www-data -R /var/z9/apps/$1

#TODO: solve problem with permission when this directory is mounted via sshfs - I can't get it work for now
sudo chmod 777 -R /var/z9/apps/$1


# make soft-links for uwsgi launcher and nginx-conf
sudo ln -s /var/z9/apps/$1/launcher.sh /etc/init.d/$1-app
sudo ln -s /var/z9/apps/$1/conf/$1.nginx.conf /etc/nginx/conf.d/$1.conf

sudo ln -s /var/z9/apps/$1/views/__css__/all.css /var/z9/apps/$1/static/css/all.css
sudo ln -s /var/z9/apps/$1/views/__js__/all.js /var/z9/apps/$1/static/js/all.js
sudo ln -s /usr/local/lib/python3.4/dist-packages/suit/Suit.js /var/z9/apps/$1/static/js/suit.js

# restarting
sudo /etc/init.d/$1-app start
sudo /etc/init.d/nginx restart
sudo /etc/init.d/$1-app rebuild

echo "Done!"
