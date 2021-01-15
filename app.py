import os
from os.path import isfile, join
from flask import Flask, render_template, url_for,  request, redirect, send_file, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'images/'
all_files = [f for f in os.listdir('images') if isfile(join('images', f))]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['POST', 'GET'])
def index():
    print(all_files)
    if request.method == 'POST':
        new_image = request.files['image']
        filename = secure_filename(new_image.filename)
        new_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('index.html')
    return render_template('index.html')


@app.route('/img')
def img():
    return send_file('images/{0}'.format(request.args.get('id')), mimetype='image/gif')


@app.route('/gallery')
def gallery():
    return render_template('gallery.html', images=all_files)


if __name__ == '__main__':
    app.run()
