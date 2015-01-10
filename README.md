# The Anti-Social Network

Join at [https://anti-social.herokuapp.com](https://anti-social.herokuapp.com) !!!

### Are you tired of not having enough online followers in your social networks?

Can't you stand the fact that only the cool kids are popular and have all the "likes"? Nobody "stars" or "retweets" your stories? Do you wish you had more friends to love all your pointless posts?

###Your problems are over!

Get as many friends as you need to feel good about yourself again! Register Today!


### Posts are not limited to 140 characters and you can write in rich text!


### Screenshots:

![](http://i.imgur.com/aWITmEH.png)

![](http://i.imgur.com/fRnw4Ok.png)

![](http://i.imgur.com/N9e8kTB.png)

![](http://i.imgur.com/M9WeNOs.png)

![](http://i.imgur.com/GM6WNIK.png)

![](http://i.imgur.com/8ugLkBq.png)





## Instructions - Development

The Anti-Social Network was built on Flask&Python. The License is MIT, feel free to play:


#### Start your virtual environment.

#### Import the dependences:

```
(anti) $ pip install -r requirements/*
```

####Import environment variables for user authentications (this can also be added to your .bash):

```
(anti) $ export MAIL_USERNAME=<Gmail username>
(anti) $ export MAIL_PASSWORD=<Gmail password>
(anti) $ export ANTISOCIAL_ADMIN=<your-email-address>
(anti) $ export SECRET_KEY=<choose-a-secrecy>
```


#### Upgrade your DB:

```
$ python manage.py db migrate
$ python manage.py db upgrade
```

#### Run!

```
$ python manage.py runserver
```

#### You can also do:

```
$ python manage.py shell
$ python manage.py test
```




## Instructions - Production

If you want to use the machinery to deploy the app somewhere (MIT License).
[Instructions here](https://coderwall.com/p/pstm1w?i=2&p=1&q=author%3Abt3gl&t%5B%5D=bt3gl).


