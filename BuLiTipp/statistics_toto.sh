#!/bin/bash
unentschieden='("0:0","1:1","2:2","3:3","4:4")'
#spielzeit='("1","2")'
spielzeit='("2")'
#spielzeit='("1")'
# 1=DFB, 2=Saison
users='("1","4","5","6","7","8","9","10","11","12")'

filename="BuLiTipp/database.db"

echo "copy punkterechner..."
cp BuLiTippApp/models/punkterechner_1_1_1.py BuLiTippApp/models/punkterechner.py
echo "refresh statistics..."
./refreshStatistics.py

echo
echo "=== beste Toto-Quoten (Hinrunde) ==="
echo $(sqlite3 $filename 'select punkte, count(*) as count from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' and p.punkte>=7 and t.nummer<18  group by punkte order by punkte desc;')
echo $(sqlite3 $filename 'select punkte, count(*) as count, u.username from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' and p.punkte>=7 and t.nummer<18  group by punkte, username order by punkte desc, count desc;')

echo
echo "=== beste Toto-Quoten ==="
echo $(sqlite3 $filename 'select punkte, count(*) as count from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' and p.punkte>=7  group by punkte order by punkte desc;')
echo $(sqlite3 $filename 'select punkte, count(*) as count, u.username from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' and p.punkte>=7  group by punkte, username order by punkte desc, count desc;')

echo
echo "=== schlechteste Toto-Quoten ==="
echo $(sqlite3 $filename 'select punkte, count(*) as count from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' and p.punkte<=3  group by punkte order by punkte desc;')
echo $(sqlite3 $filename 'select punkte, count(*) as count, u.username from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' and p.punkte<=3  group by punkte, username order by punkte desc, count desc;')

echo
echo "=== Toto-Quoten Uebersicht ==="
echo $(sqlite3 $filename 'select punkte, count(*) as count from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' group by punkte order by punkte desc;')
