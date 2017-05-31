python3 manage.py migrate
python3 manage.py createautoadmin
python3 manage.py loaddata fixtures/*.json
python3 manage.py collectstatic --noinput