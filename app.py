import boto3
import firebase_admin
import pyrebase
import datetime
from flask import Flask, render_template,  request, redirect, make_response
from firebase_admin import credentials, auth
from botocore.client import Config
import secrets
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repo.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    token = db.Column(db.String(5000))
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


cred = credentials.Certificate('fbAdminConfig.json')
firebaseadmin = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(secrets.PYREBASE_CONFIG)


s3 = boto3.resource(
    's3',
    aws_access_key_id=secrets.ACCESS_KEY_ID,
    aws_secret_access_key=secrets.ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
bucket = s3.Bucket(secrets.BUCKET_NAME)
client = boto3.client(
    's3',
    aws_access_key_id=secrets.ACCESS_KEY_ID,
    aws_secret_access_key=secrets.ACCESS_SECRET_KEY,
)


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.cookies.get('token'):
            return {'message': 'No token provided'}, 400
        try:
            user = auth.verify_id_token(request.cookies.get('token'))
            request.user = user
        except:
            return {'message': 'Invalid token provided'}, 400
        return f(*args, **kwargs)

    return wrap


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        unsuccessful = 'Please check your credentials'
        email = request.form['email']
        password = request.form['password']

        try:
            login_user = pb.auth().sign_in_with_email_and_password(email, password)

            user = User.query.filter_by(email=email).first()
            user.token = login_user['idToken']
            db.session.commit()

            resp = make_response(redirect('/'))
            resp.set_cookie('token', login_user['idToken'],
                            expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=3600))
            resp.set_cookie('email', email,
                            expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=3600))

            return resp
        except:
            return render_template('login.html', us=unsuccessful)
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        unsuccessful = 'Please check your credentials'
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user:
            return redirect('/login')

        try:
            auth.create_user(email=email, password=password)
            new_user = User(email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        except:
            return render_template('signup.html', us=unsuccessful)
    return render_template('signup.html')


@app.route('/logout', methods=['POST'])
def logout():
    pb.auth().current_user = None
    resp = make_response(redirect('/signup'))
    resp.set_cookie('token', '', expires=0)
    resp.set_cookie('email', '', expires=0)

    return resp


@app.route('/', methods=['POST', 'GET'])
@check_token
def index():
    if request.method == 'POST':
        new_images = request.files.getlist('images[]')
        cur_user = User.query.filter_by(email=request.cookies.get('email')).first()
        for image in new_images:
            added_image = s3.Bucket(secrets.BUCKET_NAME).put_object(Key=image.filename, Body=image, ACL='public-read')
            public = True if request.form.get('public-private') else False

            if public:
                public_img = PublicImage(key=added_image.key, user=cur_user)
                db.session.add(public_img)
                db.session.commit()
            elif not public:
                private_img = PrivateImage(key=added_image.key, user=cur_user)
                db.session.add(private_img)
                db.session.commit()

        return redirect('/public-gallery')
    return render_template('index.html')


@app.route('/delete-images', methods=['POST'])
@check_token
def delete():
    images_to_delete = request.form.getlist('select-object')
    cur_user = User.query.filter_by(email=request.cookies.get('email')).first().id
    for image in images_to_delete:
        public_delete = PublicImage.query.filter_by(user_id=cur_user, key=image).delete()
        private_delete = PrivateImage.query.filter_by(user_id=cur_user, key=image).delete()
        db.session.commit()

        if public_delete or private_delete:
            client.delete_object(
                Bucket=secrets.BUCKET_NAME,
                Key=image
            )

    return redirect('/public-gallery')


@app.route('/personal-gallery')
@check_token
def img():
    cur_user = User.query.filter_by(email=request.cookies.get('email')).first()
    photo_list = []
    private_photos = PrivateImage.query.filter_by(user=cur_user).all()
    public_photos = PublicImage.query.filter_by(user=cur_user).all()
    for photo in public_photos:
        photo_list.extend([photo.key])
    for photo in private_photos:
        photo_list.extend([photo.key])
    return render_template('gallery.html', images=photo_list)


@app.route('/public-gallery', methods=['GET'])
@check_token
def gallery():
    photo_list = []
    public_photos = PublicImage.query.all()
    for photo in public_photos:
        photo_list.extend([photo.key])
    return render_template('gallery.html', images=photo_list)


if __name__ == '__main__':
    app.run(debug=True)
