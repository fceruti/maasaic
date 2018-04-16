# maasaic.com

### Dev-ops

##### Configure server
```
ansible-playbook -i arch/inventories/prod/ -u ubuntu configure.yml

```

##### Deploy
```
ansible-playbook -i arch/inventories/prod/ -u ubuntu arch/deploy.yml
```


### Static files

##### Compress static files
```
python manage.py compress --force
```

##### Upload to S3
```
python manage.py collectstatic --settings=maasaic.settings.collect_static
```
