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

# configure default mappers.py in default project database
cd ../databases/
mv default $1
cd $1/
sed -e "s/{default}/$1/g" default_mappers.py > mappers.py
rm -f default_mappers.py
cd ../../

# configure application.py and launcher
sed -e "s/{default}/$1/g" default_application.py > application.py
sed -e "s/{default}/$1/g" default_launcher.sh > launcher.sh
rm -f default_application.py
rm -f default_launcher.sh
chmod +x launcher.sh

# configure default bootstrap template
cd views/
sed -e "s/{default}/$1/g" default_bootstrap.html > bootstrap.html
cd ../

# setting up rights for the app directory
sudo chown www-data:www-data -R /var/z9/apps/$1

#TODO: solve problem with permission when this directory is mounted via sshfs - I can't get it work for now
sudo chmod 777 -R /var/z9/apps/$1


# make soft-links for uwsgi launcher and nginx-conf
sudo ln -s /var/z9/apps/$1/launcher.sh /etc/init.d/$1-app
sudo ln -s /var/z9/apps/$1/conf/$1.nginx.conf /etc/nginx/conf.d/$1.conf

# restarting
sudo /etc/init.d/$1-app start
sudo /etc/init.d/nginx restart
sudo /etc/init.d/$1-app rebuild

echo "Done!"
