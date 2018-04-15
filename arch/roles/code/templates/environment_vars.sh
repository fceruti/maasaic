export DJANGO_ENV={{ env }}
export DJANGO_DEBUG={{ django_debug }}
export DJANGO_SECRET_KEY={{ django_secret_key }}
export DJANGO_DATABASE_URL=postgres://{{ django_db_user }}:{{ django_db_password }}@{{ django_db_host }}:5432/{{ django_db_name }}
export DEFAULT_SITE_DOMAIN=maasaic.com

export AWS_ACCESS_KEY_ID={{ aws_access_key_id }}
export AWS_SECRET_ACCESS_KEY={{ aws_secret_key }}
export AWS_STORAGE_BUCKET_NAME={{ s3_bucket_name }}
export AWS_LOCATION={{ s3_static_location }}
export STATIC_URL=https://{{ s3_bucket_name }}.s3.amazonaws.com/{{ s3_static_location }}/
