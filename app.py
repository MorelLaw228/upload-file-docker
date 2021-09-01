#!/usr/bin/python3

from flask import *
from werkzeug.utils import secure_filename
import os
import sys
from PIL import Image
import pytesseract
import cv2


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGHT'] = 10*1024*1024


@app.route('/about')
def about_page():
    return render_template("about_page.html")

@app.route('/uploader',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['files']

        # create secure filename
        filename = secure_filename(f.filename)

        # save file to uploads directory
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
        f.save(filepath)

        # load example of image to ocr and convert it to grayscale
        image = cv2.imread(filepath)

        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        # apply thresholding to preprocess the image
        gray = cv2.threshold(gray,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # apply median blurring to remove any blurring
        gray = cv2.medianBlur(gray,3)

        # save the preprocess image to UPLOAD_FOLDER
        output_image = os.path.join(app.config['UPLOAD_FOLDER'],"{}.png".format(os.getpid()))
        cv2.imwrite(output_image,gray)

        # perform OCR on the processed image
        text = pytesseract.image_to_string(Image.open(output_image))

        # remove processed image
        os.remove(output_image)


        return render_template("upload_page.html",displaytext = text,fname = filename)


if __name__ == '__main__':
    app.run(debug=True)