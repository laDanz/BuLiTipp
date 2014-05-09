#!/bin/bash
unentschieden='("0:0","1:1","2:2","3:3","4:4")'
#spielzeit='("1","2")'
spielzeit='("2")'
#spielzeit='("1")'
# 1=DFB, 2=Saison
users='("1","4","5","6","7","8","9","10","11","12")'

filename="BuLiTipp/database.db"

echo "reset punkterechner..."
git checkout BuLiTippApp/models/punkterechner.py
echo "refresh statistics..."
./refreshStatistics.py


echo "=== Echte Ergebnissse ==="
echo "von " $(sqlite3 $filename 'select count(*) as count from bulitippapp_spiel s, bulitippapp_spieltag st where st.id=s.spieltag_id and ergebniss <> "DNF" and st.spielzeit_id in '$spielzeit';') "spielen, sind das die häufigsten ECHTEN Ergebnisse:"
echo $(sqlite3 $filename 'select ergebniss, count(s.id) as count from bulitippapp_spiel s, bulitippapp_spieltag st where s.spieltag_id=st.id and ergebniss <> "DNF" and st.spielzeit_id in'$spielzeit' group by ergebniss order by count desc;')
echo $(sqlite3 $filename 'select count(*) as count from bulitippapp_spiel s,bulitippapp_spieltag st where s.spieltag_id=st.id and ergebniss in '$unentschieden' and st.spielzeit_id in '$spielzeit';') " Unentschieden"

echo
echo "=== Getippte Ergebnisse ==="
echo "von " $(sqlite3 $filename 'select count(*) as count from bulitippapp_tipp t, bulitippapp_spiel s, bulitippapp_spieltag st, auth_user u where u.id in '$users' and u.id=t.user_id and t.spiel_id=s.id and s.spieltag_id=st.id and s.ergebniss <> "DNF" and st.spielzeit_id in '$spielzeit';') "spielen, sind das die häufigsten GETIPPTEN Ergebnisse:"
echo $(sqlite3 $filename 'select t.ergebniss, count(t.id) as count from bulitippapp_tipp t, bulitippapp_spiel s, bulitippapp_spieltag st, auth_user u where u.id in '$users' and u.id=t.user_id and t.spiel_id=s.id and s.spieltag_id=st.id and s.ergebniss <> "DNF" and st.spielzeit_id in '$spielzeit' group by t.ergebniss order by count desc;')
echo $(sqlite3 $filename 'select count(*) as count from bulitippapp_tipp t, bulitippapp_spiel s, bulitippapp_spieltag st, auth_user u where u.id in '$users' and u.id=t.user_id and t.spiel_id=s.id and s.spieltag_id=st.id and t.ergebniss in '$unentschieden' and st.spielzeit_id in '$spielzeit';') " Unentschieden"

echo
echo "=== So viele Spiele haben die User getippt ==="
echo $(sqlite3 $filename 'select u.username, count(t.id) as count from bulitippapp_tipp t left join bulitippapp_spiel s on t.spiel_id = s.id, auth_user u , bulitippapp_spieltag st where s.spieltag_id=st.id and u.id=t.user_id and st.spielzeit_id in '$spielzeit' and u.id in '$users' group by u.username order by count desc;')
echo "(Punkte pro Spieltag ausrechnen)"

echo
echo "=== Richtig Getippt ==="
echo "insegesamt wurde " $(sqlite3 $filename 'select count(t.id) as count from bulitippapp_tipp t left join bulitippapp_spiel s on t.spiel_id = s.id , bulitippapp_spieltag st, auth_user u where u.id in '$users' and t.user_id=u.id and s.spieltag_id=st.id and t.ergebniss=s.ergebniss and st.spielzeit_id in '$spielzeit';')  "mal richtig getippt. Die Verteilung:"
echo $(sqlite3 $filename 'select t.ergebniss, count(t.id) as count from bulitippapp_tipp t left join bulitippapp_spiel s on t.spiel_id = s.id , bulitippapp_spieltag st, auth_user u  where u.id in '$users' and u.id=t.user_id and s.spieltag_id=st.id and t.ergebniss=s.ergebniss and st.spielzeit_id in '$spielzeit' group by t.ergebniss order by count desc;')
echo "Diese User haben richtig getippt:"
echo $(sqlite3 $filename 'select u.username, count(t.id) as count from bulitippapp_tipp t left join bulitippapp_spiel s on t.spiel_id = s.id, auth_user u , bulitippapp_spieltag st where s.spieltag_id=st.id and u.id=t.user_id and u.id in '$users' and t.ergebniss=s.ergebniss and st.spielzeit_id in '$spielzeit' group by u.username order by count desc;')

echo
echo "=== Punkteverteilung ==="
echo $(sqlite3 $filename 'select punkte, count(*) as count from bulitippapp_punkte p, auth_user u, bulitippapp_spieltag t where t.id= p.spieltag_id and t.spielzeit_id in '$spielzeit' and u.id=p.user_id and u.id in '$users' group by punkte order by punkte desc;')


echo "import statistics" | ./manage.py shell #2> /dev/null
