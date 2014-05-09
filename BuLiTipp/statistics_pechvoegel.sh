#!/bin/bash
unentschieden='("0:0","1:1","2:2","3:3","4:4")'
#spielzeit='("1","2")'
spielzeit='("2")'
#spielzeit='("1")'
# 1=DFB, 2=Saison
users='("1","4","5","6","7","8","9","10","11","12")'

filename="BuLiTipp/database.db"

echo "copy punkterechner..."
cp BuLiTippApp/models/punkterechner_pechvoegel.py BuLiTippApp/models/punkterechner.py
echo "refresh statistics..."
./refreshStatistics.py

echo
echo "=== Pechvoegel (wegen einem Tor daneben 0 Punkte) ==="
echo $(sqlite3 $filename 'select sum(punkte) as summe, u.username from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' group by u.username order by summe desc;')

