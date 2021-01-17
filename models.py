from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    private_images = db.relationship('PrivateImage', backref='user')
    public_images = db.relationship('PublicImage', backref='user')

    def __repr__(self):
        return '<User %r>' % self.id


class PrivateImage(db.Model):
    key = db.Column(db.String(200), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<PrivateImage %r>' % self.key


class PublicImage(db.Model):
    key = db.Column(db.String(200), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<PublicImage %r>' % self.key
