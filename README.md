## the anti-social network 

<br>

<p align="center">
<img height="200" src="http://i.imgur.com/aWITmEH.png">
<img height="200" src="http://i.imgur.com/fRnw4Ok.png">
<img height="200" src="http://i.imgur.com/N9e8kTB.png">
<img height="200" src="http://i.imgur.com/M9WeNOs.png">
<img height="200" src="http://i.imgur.com/GM6WNIK.png">
<img height="200" src="http://i.imgur.com/8ugLkBq.png">
</p>

<br>

---

### running

<br>

* install the dependencies in a venv:

```
pip install -r requirements/*
```

* import environment variables for user authentications (this can also be added to your `.bash`):

```
export MAIL_USERNAME=<Gmail username>
export MAIL_PASSWORD=<Gmail password>
export ANTISOCIAL_ADMIN=<your-email-address>
export SECRET_KEY=<choose-a-secrecy>
```

* upgrade your DB:

```
python manage.py db migrate
python manage.py db upgrade
```

* run:

```
python manage.py runserver
```

