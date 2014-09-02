Z9 WEB-FRAMEWORK
================

includes envi, suit, mapex and some more...

---

###Requirements
* **nginx** installed and nginx.conf should include all *.conf files from conf.d directory


* **uwsgi** installed and configured with **python3** support. Also you should add a symlink for uwsgi binary in /usr/local/bin/. 

* **envi**, **suit**, **mapex** located in python3.X/dist-packages directory.

* **z9-framework** itself should be located in /var/z9/.

---

###Managing applications

In order to add new empty application, run:

> bin/add\_host.sh appname

This will create new "appname" directory in the "app" directory with proper structure and run the app, so it will be accessible as http://appname.local from localhost.
You might want to change your /etc/hosts accordingly.


To stop the application and remove its directories use:

> bin/rm\_host.sh appname


