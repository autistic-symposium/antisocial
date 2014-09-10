__author__="Marina Wahl"

"""
    In the MVC paradigm, models are the database interface
"""


from datetime import datetime
import hashlib

# Werkzeug's security module implements secure password hashing
# through these two functions
from werkzeug.security import generate_password_hash, check_password_hash

# for hashing
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request

# for rich text
from markdown import markdown
import bleach

from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager



"""
    PERMISSIONS Class:
    Users are assigned a discrete role, but the roles are defined in terms of
    permissions.
    The default field is true for only one role.
    The permission fields is an integer used as bit flags, each task will have
    a bit position, and for each role, the tasks that are allowed for that role
    have their bits set to 1.
"""

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80



"""
    FOLLOW Class
"""

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



"""
    ROLE Class
"""

class Role(db.Model):
    __tablename__ = 'roles'
    # SLQAlchemy requires all modesl to define a primary key
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # lazy='dynamic' to request that the query is not automatically
    # executed, so filters can be addes
    users = db.relationship('User', backref='role', lazy='dynamic')

    # create roles in the database
    # To apply roles to the database:
    # $ Role.insert_roles()
    # $ Role.query.all()
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    # readable string representation
    def __repr__(self):
        return 'Role %r' % self.name



"""
    USER Class
"""


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # A many-to-many relationship implemented as two one to-many relationship
    # Follow instances, where each one has the follower and followed back reference
    # properties set to the respective users. The lazy='joined' mode enables this all
    # to happen from a single database query. If lazy is set to the default value of
    # select , then the follower and followed users are loaded lazily when they are
    # first accessed and each attribute will require an individual query, which means
    # that obtaining the complete list of followed users would require 100 additional
    # database queries.
    # The cascade argument configures how actions performed on a parent object propagate
    # to related objects. An example of a cascade option is the rule that says that when an
    # object is added to the database session, any objects associated with it through
    # relationships should automatically be added to the session as well. The default
    # cascade options are appropriate for most situations, but there is one case in which
    # the default cascade options do not work well for this many-to-many relationship.
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # Comments in posts
    comments = db.relationship('Comment', backref='author', lazy='dynamic')


    # show own posts together with follower points
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()



    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # define a default role for users
        if self.role is None:
            if self.email == current_app.config['ANTISOCIAL_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        # to get the gravatar address
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))



    # password hashing and unhashing
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        #print(type(password))
        #print(type(self.password_hash))
        #print(type(self.password_hash.encode('utf-8')))
        return check_password_hash(self.password_hash.encode('utf-8'), password.encode('utf-8'))



    # for email authentication and token generations
    def generate_confirmation_token(self, expiration=3000):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    def generate_reset_token(self, expiration=3000):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})



    # reseting user password
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True



    # to change email
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True



    # permissions verification for a user
    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)



    # to set date/time in signup and posts (refresh last visit)
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    # readable str rep
    def __repr__(self):
        return 'User %r' % self.username


    # create fake data
    # User.generate_fake()
    @staticmethod
    def generate_fake(count=10):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
            username=forgery_py.internet.user_name(True),
            password=forgery_py.lorem_ipsum.word(),
            confirmed=True,
            name=forgery_py.name.full_name(),
            location=forgery_py.address.city(),
            about_me=forgery_py.lorem_ipsum.sentence(),
            member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()



    # the following/follower propriety
    # this method inserts a Follow instance in the association table
    # that links a follower with a followed user
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(followed=user)
            self.followed.append(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            self.followed.remove(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    # Join union database to only show the relevant posts
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)




"""
    POST Class:
    A blog post is represented by a body, a timestamp, and a one-to-may
    relationship from the User model.
"""

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    # db .Text gives no limitation on the length
    body = db.Column(db.Text)
    # rich text
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')


    # create fake posts
    @staticmethod
    def generate_fake(count=10):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
            timestamp=forgery_py.date.date(True),
            author=u)
            db.session.add(p)
            db.session.commit()


    # rich text
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


# rich text event listener: it will automatically be invoked whenever
# the body field on any instance of the class is set to a new value
# The conversion is done in three steps: first the markdown() function does
# an initial conversion to HTML. The result is passed to clean(), along with
# a list of approved HTML tags (removes any tag that are not in the whitelist).
# The final conversion is done with linkify(), that converts any URL written
# in plain text into a proper <a>
db.event.listen(Post.body, 'set', Post.on_changed_body)








"""
    ANONYMONUS Class
"""

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser


# User loader callback function, that loads a
# user, given the identifier (as a unicode string)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""
    COMMENTS class
"""

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)
