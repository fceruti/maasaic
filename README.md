# Maasaic

Maasaic is a sofware to create and host your own websites using a mosaic like structure. The main idea is to create non-standard good looking websites very easily. You can try it out at maasaic.com

### Dev and testing

To start developing or trying out this project on your local computer follow this

```
git clone https://github.com/fceruti/maasaic.git
cd maasaic
mkvirtualenv --python=python3 maasaic
pip install -r requirements/dev.txt
```

You'll also need to set some environment variables, for which I create `.env` file and load it like this:

```
export DJANGO_SECRET_KEY=???
export DJANGO_ENV=dev
export DJANGO_DEBUG=True
export DJANGO_DATABASE_URL=postgres://localhost:5432/???
export DEFAULT_SITE_DOMAIN=http://maasaic-local.com:8000/
export STATIC_URL=/static/
export MEDIA_URL=http://maasaic-local.com:8000/media/
export MEDIA_ROOT=???
export STATIC_ROOT=???

export AWS_ACCESS_KEY_ID=???
export AWS_SECRET_ACCESS_KEY=???
export AWS_STORAGE_BUCKET_NAME=???
export AWS_LOCATION=???

export GIPHY_KEY=???

workon maasaic
```

Also, so that you can try out diffent sites, you have to add some entries in `/etc/hosts`

```
127.0.0.1 maasaic-local.com
127.0.0.1 fceruti.maasaic-local.com
...
```

To run the tests
```
py.test
```

To run a local dev server
```
python manage.py runserver
```

To check lint
```
flake8
```

### Dev-ops

##### Configure server
```
ansible-playbook -i arch/inventories/prod/ -u ubuntu configure.yml

```

##### Deploy
```
ansible-playbook -i arch/inventories/prod/ -u ubuntu arch/deploy.yml
```

##### Managing static files

###### Compress static files
```
python manage.py compress --force
```

###### Upload to S3
```
python manage.py collectstatic --settings=maasaic.settings.collect_static
```
