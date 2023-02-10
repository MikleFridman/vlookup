from flask_login import UserMixin, current_user
# from flask_security import RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    no_active = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))
    name = db.Column(db.String(32))
    type_id = db.Column(db.Integer, db.ForeignKey('game_type.id'))
    table_id = db.Column(db.String(32))
    rollout_date = db.Column(db.Date)
    features = db.Column(db.String(128))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    def __repr__(self):
        return self.name


class GameType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    games = db.relationship('Game', backref='type')

    def __repr__(self):
        return self.name


class RTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    min = db.Column(db.Float)
    max = db.Column(db.Float)
    game = db.relationship('Game', backref='rtp')


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(128))
    games = db.relationship('Game', backref='status')

    def __repr__(self):
        return self.name


class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(128))
    games = db.relationship('Game', backref='provider')

    def __repr__(self):
        return self.name
