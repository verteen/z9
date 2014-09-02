#! /bin/bash
if ! [ -n "$1" ]; then
	echo "Ошибка! Нет имени проекта"
	exit 1
fi

# stopping uwsgi
sudo /etc/init.d/$1-app stop

# removing files
sudo rm -rf /var/z9/apps/$1
sudo rm -f /etc/init.d/$1-app
sudo rm -f /etc/nginx/conf.d/$1.conf

# restarting nginx
sudo /etc/init.d/nginx restart

echo "Done!"