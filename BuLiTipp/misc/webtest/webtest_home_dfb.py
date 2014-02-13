from django.test import Client
c = Client()
response = c.post('/BuLiTipp/login', {'username': 'webtest', 'password': 'webtest'})
response = c.get('/BuLiTipp/home/1/37/')

if response.status_code == "302":
	raise("not registered user!")

f=open("response_home.html","w")
f.write(response.content)
f.close()
