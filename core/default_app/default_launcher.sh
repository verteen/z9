#!/bin/sh
### BEGIN INIT INFO
# Provides:             uwsgi_{default}
# Required-Start:       $remote_fs $syslog
# Required-Stop:        $remote_fs $syslog
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    uwsgi_{default}
### END INIT INFO
case $1 in
start)
        echo "Запуск uwsgi приложения {default}..."
        /usr/local/bin/uwsgi /var/z9/apps/{default}/conf/{default}.uwsgi.ini 2> /dev/null > /dev/null &
        ;;
stop)
        echo "Завершение работы uwsgi приложения {default}..."
        kill -9 `cat /var/z9/apps/{default}/{default}.uwsgi.pid` > /dev/null
        ;;
rebuild)
        echo "Перекомпиляция шаблонов"
        /usr/local/bin/suitup /var/z9/apps/{default}/views/
        echo "Пeрезапуск uwsgi приложения {default}..."
        kill `cat /var/z9/apps/{default}/{default}.uwsgi.pid` > /dev/null
        ;;
restart)
        echo "Пeрезапуск uwsgi приложения {default}..."
        kill `cat /var/z9/apps/{default}/{default}.uwsgi.pid` > /dev/null
        ;;
debug)
        echo "Запуск uwsgi приложения appserv в debug режиме..."
        /usr/local/bin/uwsgi /var/z9/apps/{default}/conf/{default}.uwsgi.ini
        ;;
help)
        echo "Используйте (start|stop|restart|help)."
        ;;
*) echo "Используйте (start|stop|restart|help)"
esac
exit 0
