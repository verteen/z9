#!/bin/bash

if ! [ -n "$1" ]; then
	echo "Ошибка! Нет имени проекта"
	exit 1
fi

if [ $1 == "default" ]; then
	echo "Ошибка! test"
	exit 1
fi

if ! [ -d /var/z9/apps ]; then
	echo "Ошибка! Запустите setup_environment.sh перед созданием проекта."
	exit 1
fi

if ! [ -d /var/z9/virtualenv ]; then
	echo "Ошибка! Запустите setup_environment.sh перед созданием проекта."
	exit 1
fi

Z9_DIR="$( dirname `readlink -e "$0"` )/.."
APP_DIR=/var/z9/apps/$1

# make new copy of directories
mkdir $APP_DIR
cp -r $Z9_DIR/core/default_app/* $APP_DIR
cd $APP_DIR

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

# configure controllers directory
cd controllers/
sed -e "s/{default}/$1/g" default_controllers.py > common.py
rm -f default_controllers.py
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
sudo chown www-data:www-data -R $APP_DIR
sudo chmod 775 -R $APP_DIR

# make soft-links for uwsgi launcher and nginx-conf
sudo ln -sf $APP_DIR/launcher.sh /etc/init.d/$1-app
sudo ln -sf $APP_DIR/conf/$1.nginx.conf /etc/nginx/conf.d/$1.conf

sudo ln -s $APP_DIR/views/__css__/all.css $APP_DIR/static/css/all.css
sudo ln -sf $APP_DIR/views/__js__/all.js $APP_DIR/static/js/all.js
sudo ln -sf /var/z9/virtualenv/lib/python3.4/site-packages/suit/Suit.js /var/z9/apps/$1/static/js/suit.js

# restarting
sudo /etc/init.d/$1-app start
sudo /etc/init.d/nginx restart
sudo /etc/init.d/$1-app rebuild

echo "Done!"
