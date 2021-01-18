# Shopify Developer Challenge


For this challenge, I've built an image repository where users can create an account, add public and private images, and delete their own images.

### Built with:
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Amazon S3](https://aws.amazon.com/s3/)
- [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [Firebase Authentication](https://firebase.google.com/docs/auth)

### Installation
1. Clone the repo<br />
```
git clone https://github.com/orizabal/ShopifyDeveloperChallenge2021.git
```
2. Install packages<br />
```
pip install -r requirements.txt
```
3. Run app.py<br />
```
python3 app.py
```

### Usage
**Go to /signup** to create an account. After you create an account, you will be redirected to the **/login** page.

After you login, select the image(s) (.jpg, .png) that you wish to upload. Select the Public? checkbox if you want the image(s) to be public.

You will then be redirected to **/public-gallery** where you can see all public images from yourself and other users. You will be able to delete images that you have uploaded.

You can also go to **/personal-gallery** to see only images that you have uploaded (public and private). You may delete any image in your personal gallery.

Click the Logout button to log out.
