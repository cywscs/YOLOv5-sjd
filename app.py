import os
import shutil
import json
from time import sleep

from flask import Flask, render_template, request, redirect, jsonify
import requests
import base64

from gevent import pywsgi

import config
import detect

app = Flask(__name__)
app.config.from_object(config)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], "sample.jpg"))
    res = {
        "data": {
            "url": "http://localhost:5000/static/upload/sample.jpg"
        },
        "meta": {
            "msg": "上传成功",
            "status": 200
        }
    }
    return res


@app.route('/detect', methods=['GET'])
def ocr():
    # 识别空手机袋
    shutil.rmtree('static/exp')
    detect.detect()
    # 裁剪出小图
    shutil.move('./static/exp/labels/sample.txt', './static/exp')
    shutil.rmtree("./static/output")
    os.mkdir("./static/output")
    os.system('python outputImage.py')
    # ocr识别数字
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Ofgbon2NA3qf2xeyp7dG4L52' \
           '&client_secret=gaF4Snap3iTFySdmufL7HjKFm8Ur5dge'
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
    response = requests.get(host)
    access_token = json.loads(response.content.decode('utf-8')).get("access_token")
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    num = []

    for i in os.listdir("static/output"):
        imgdir = os.path.join('static/output/', i)
        f = open(imgdir, 'rb')
        img = base64.b64encode(f.read())
        params = {"image": img}
        response = requests.post(request_url, data=params, headers=headers)
        print(json.loads(response.content.decode('utf-8')))
        # 识别失败情况
        if json.loads(response.content.decode('utf-8')).get("words_result") == []:
            num = ["null"]
            return json.dumps(num)
        else:
            num.append(json.loads(response.content.decode('utf-8')).get("words_result")[0].get("words"))
        sleep(0.5)

    # 调整识别错误的结果
    for i in range(len(num)):
        if int(num[i]) > 60:
            num[i] = str(int(num[i]) - 60)

    return json.dumps(num)  # 返回结果


if __name__ == '__main__':
    # windows
    server = pywsgi.WSGIServer(('localhost', 5000), app)
    # linux
    # server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
