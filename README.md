# maasaic.com

### Dev-ops

#### Configure server

```
ansible-playbook -i arch/inventories/prod/ -u ubuntu configure.yml

```

#### Static files

##### Compress static files
```
python manage.py compress --settings=maasaic.settings.compress
```

##### Upload to S3
```
python manage.py compress --settings=maasaic.settings.compress
```
