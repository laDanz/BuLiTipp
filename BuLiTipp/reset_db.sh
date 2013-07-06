python manage.py dumpdata BuLiTippApp > temp_data.json
python manage.py reset BuLiTippApp
python manage.py loaddata temp_data.json
