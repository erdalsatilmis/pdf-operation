from flask import Flask, request, Response
from flask_cors import CORS
import numpy as np
import cv2 as cv
import jsonpickle
from pdfToImage import pdfConvert
from readPage import getData
import base64
application = Flask(__name__)
CORS(application)


@application.route("/")
def index():
    return "<h1>Hello! v1</h1>"

@application.route('/api/pdf/imageRead', methods=['POST', 'OPTIONS'])
def readPage():
    pngUrl = request.form.get('pngUrl')
    imgdata = base64.b64decode(pngUrl)
    file_bytes = np.asarray(bytearray(imgdata), dtype=np.uint8)
    img = cv.imdecode(file_bytes, 1)
    pageCoordinates = getData(img)
    response = {
        "data": pageCoordinates
    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@application.route('/api/pdf/convertImage', methods=['POST', 'OPTIONS'])
def convertPDF():
    pdfByte = request.files['pdf'].read()
    imageFormat = request.form.get("format")
    pagesBase64 = pdfConvert(pdfByte,imageFormat)
    response = {
        "data": pagesBase64
    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# start flask app
if __name__ == "__main__":
 application.run()
#if __name__ == "__main__":
#    app.run(ssl_context='adhoc')

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)
