### Deployment

1. Login to Your server by root user
`ssh root@your_server_ip`

2. once you loign add the user with your name

`adduser guru`

3. Now we have the User gave it sudo rights

`usermod -aG sudo guru`

4. Logout from root user and login by guru (created user)

5. Initialize & update Ubuntu packages

`sudo apt-get update`

`sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx`

6. Create the user and database in postgreSQL database as per the app requirement.

`sudo -u postgres psql`

here we add the database name to app 

`CREATE DATABASE app;`

`CREATE USER guru WITH PASSWORD 'guru_password';`

Now we gave access to the new creted user in Database

`ALTER ROLE myprojectuser SET client_encoding TO 'utf8';`

`ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';`

`ALTER ROLE myprojectuser SET timezone TO 'UTC';`

`GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;`

and quit the postgresql

`\q`

7. Now create a python virtual environament

`sudo -H pip3 install —-upgrade pip`

`sudo -H pip3 install virtualenv`

8. create app directory and start the virtualenv

`mkdir ~/application`

`cd ~/application`

`virtualenv application`

`source application/bin/activate`

9. install daphne and psycopg2-binary so python or our app can connect to postgreSQL and daphne

`pip install daphne psycopg2-binary`

10. clone your dango project

`
git clone "https://github.com/guru-sevak-singh/scan2food.git"
`

`cd scan2food`

`pip install -r requirement.txt`

`python manage.py makemigrations`

`python manage.py migrate`

11. Initialize youd django project and update the DATABASE in settings.py file

```
DATABASES = {
   'default': {
      'ENGINE': 'django.db.backends.postgresql_psycopg2',
      'NAME': 'app',
      'USER': 'guru',
      'PASSWORD': 'guru_password',
      'HOST': 'localhost',
      'PORT': '5432',
      }
}
```

12. Creating systemd Socket and Service Files for Daphne

daphne socket file
`sudo nano /etc/systemd/system/daphne.socket`

file content

```
[Unit]
Description=daphne socket

[Socket]
ListenStream=/run/daphne.sock

[Install]
WantedBy=sockets.target
```

daphne service file

`sudo nano /etc/systemd/system/daphne.service`

file content:

```
[Unit]
Description=daphne daemon
Requires=daphne.socket
After=network.target

[Service]
Type=simple
User=guru
WorkingDirectory=/home/guru/application/django_project_dir
ExecStart=/home/guru/application/scan2food/bin/daphne -b 0.0.0.0 -p 8000 source.asgi:application

[Install]
WantedBy=multi-user.target
```

13. start the daphne service and socket file

`sudo systemctl start daphne.socket`

`sudo systemctl enable daphne.socket`

14. check status of daphne

`sudo systemctl status daphne.socket`

15. check existence of daphne.sock file in `/run` directory

`file /run/daphne.sock`

16. check the daphne running

`sudo journalctl -u daphne.socket`

`sudo systemctl status daphne`

`sudo systemctl daemon-reload`

`sudo systemctl restart daphne`


17. Configure Nginx to Proxy Pass to Daphne

sudo nano /etc/nginx/sites-available/scan2food

18. file content:

```
upstream channels-backend {server localhost:8000;}

server {
listen 80;
server_name server_domain_or_IP;

location /static/ {
root /home/guru/application/scan2food;
}
location /media/ {
root //home/guru/application/scan2food;
}
location / {
proxy_pass http://channels-backend;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header Host $http_host;
proxy_redirect off;
}
}
```

19. copy and paste the file in site-available also

`sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled`

20. test your ngins

`sudo nginx -t`

21. restart the nginx

`sudo systemctl restart nginx`

22. allow the nginx through ufw (a kind of firewall)

`sudo ufw allow 'Nginx Full'`

