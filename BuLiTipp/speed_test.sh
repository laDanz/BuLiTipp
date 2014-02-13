#!/bin/bash

echo "News, reference:"
time cat misc/webtest/webtest_news.py | ./manage.py shell 2> /dev/null
echo "Spieltag, full details:"
time cat misc/webtest/webtest.py | ./manage.py shell 2> /dev/null
echo "Spieltag(DFB), full details:"
time cat misc/webtest/webtest_dfb.py | ./manage.py shell 2> /dev/null
echo "Home, medium details"
time cat misc/webtest/webtest_home.py | ./manage.py shell 2> /dev/null
echo "Home(DFB), medium details"
time cat misc/webtest/webtest_home_dfb.py | ./manage.py shell 2> /dev/null
