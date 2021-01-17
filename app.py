import boto3
import pyrebase
from flask import Flask, render_template,  request, redirect
from botocore.client import Config
import secrets
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repo.db'
db.init_app(app)

firebase = pyrebase.initialize_app(secrets.PYREBASE_CONFIG)
auth = firebase.auth()

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


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        new_images = request.files.getlist('images[]')
        for image in new_images:
            acl_value = ''
            if request.form['public-private']:
                acl_value = 'public-read'
            s3.Bucket(secrets.BUCKET_NAME).put_object(Key=image.filename, Body=image, ACL=acl_value)
        return redirect('/public-gallery')
    return render_template('index.html')


@app.route('/delete-images', methods=['POST'])
def delete():
    images_to_delete = request.form.getlist('select-object')
    for image in images_to_delete:
        response = client.delete_object(
            Bucket=secrets.BUCKET_NAME,
            Key=image
        )
        print(response)

    return redirect('/public-gallery')


@app.route('/personal-gallery')
def img():
    return '/img'


@app.route('/public-gallery', methods=['GET'])
def gallery():
    photos = bucket.objects.all()
    return render_template('gallery.html', images=photos)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        unsuccessful = 'Please check your credentials'
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            print(user)
            return redirect('/')
        except:
            return render_template('login.html', us=unsuccessful)
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        unsuccessful = 'Please check your credentials'
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.create_user_with_email_and_password(email, password)
            print(user)
            return redirect('/')
        except:
            return render_template('signup.html', us=unsuccessful)
    return render_template('signup.html')


@app.route('/logout', methods=['POST'])
def logout():
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
