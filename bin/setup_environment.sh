#!/bin/bash

### Apps directory
if ! [ -d /var/z9/apps ]; then
    sudo mkdir -p /var/z9/apps
    sudo chown www-data:www-data -R /var/z9
    sudo chmod 775 -R /var/z9
fi

### Python virtualenv
if ! [ -d /var/z9/virtualenv ]; then
    virtualenv --python=python3 /var/z9/virtualenv
fi

source /var/z9/virtualenv/bin/activate

### Python packages
pip install --allow-all-external --allow-unverified pyodbc -qr $( dirname `readlink -e "$0"` )/../core/default_app/requirements.txt

PACKAGES="/var/z9/virtualenv/lib/python3.4/site-packages"
cd $PACKAGES

if ! [ -d $PACKAGES/envi ]; then
    git clone https://github.com/ayurjev/envi.git
else
    (echo "Envi" && cd $PACKAGES/envi && git pull)
fi

if ! [ -d $PACKAGES/mapex ]; then
    git clone https://github.com/ayurjev/mapex.git
else
    (echo "Mapex" && cd $PACKAGES/mapex && git pull)
fi

if ! [ -d $PACKAGES/suit ]; then
    git clone https://github.com/ayurjev/suit.git
else
    (echo "Suit" && cd $PACKAGES/suit && git pull)
fi

if ! [ -d $PACKAGES/z9 ]; then
    git clone https://github.com/ayurjev/z9.git
else
    (echo "Z9" && cd $PACKAGES/z9 && git pull)
fi


### suitup
ln -sf /var/z9/virtualenv/lib/python3.4/site-packages/suit/suitup.py /var/z9/virtualenv/bin/suitup
chmod +x /var/z9/virtualenv/bin/suitup


echo "Done!"
