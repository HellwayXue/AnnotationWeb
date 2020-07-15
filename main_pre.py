from flask import Flask
from pathlib import Path
import pickle
import sys
import requests
from flask import request, render_template, redirect, url_for, session, flash
app = Flask(__name__)
import os
if not os.path.exists("static/"):
    os.makedirs("static/")

videos = pickle.load(open("videos_name.pkl", "rb"))
examples = pickle.load(open("examples_name.pkl", "rb"))
minelabels = pickle.load(open("result_dict_containsmine.pkl", "rb"))
video_per_person=100
global_dict = {}
result_dict = {}
error_list = []
SHARED = 4
link = "https://loopingvideos.blob.core.windows.net/videos/flickr_dataset_resize/"
link = "https://loopingvideo.oss-cn-beijing.aliyuncs.com/flickr_dataset_resize/"


def getHttpStatusCode(url):
    try:
        request = requests.get(url)
        httpStatusCode = request.status_code
        return httpStatusCode
    except requests.exceptions.HTTPError as e:
        return e

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        id = int(request.form['id'])
        return redirect(url_for('hello_world', id=id))
    return render_template('index.html')

@app.route('/index3', methods=['POST', 'GET'] )
def hello_world():
    if request.method == 'POST':
        origin_id = int(request.form['origin_id'])
        if 'score' in request.form and 'scene' in request.form:
            index = global_dict[origin_id]
            if "12" in request.form.getlist("scene"):
                if request.form["text"] == "":
                    flash("请填写文本框")
                    index = global_dict[origin_id]
                else:
                    text = request.form["text"].lower()
                    if origin_id in result_dict:
                        result_dict[origin_id].append([videos[index], request.form["score"], request.form.getlist("scene"), text])
                    else:
                        result_dict[origin_id]= [[videos[index], request.form["score"], request.form.getlist("scene"), text]]
                    with open("static/result.txt", "a") as f:
                        f.write('id: {}, video: {}, label:{}, scene:{}, other:{}'.format(origin_id, videos[index], request.form["score"], request.form.getlist("scene"), text) + '\n')
                    index = global_dict[origin_id]+1
                    global_dict[origin_id] = index
            else:
                if origin_id in result_dict:
                    result_dict[origin_id].append([videos[index], request.form["score"], request.form.getlist("scene"), "None"])
                else:
                    result_dict[origin_id]= [[videos[index], request.form["score"], request.form.getlist("scene"), "None"]]
                with open("static/result.txt", "a") as f:
                    f.write('id: {}, video: {}, label:{}, scene:{}, other:{}'.format(origin_id, videos[index], request.form["score"], request.form.getlist("scene"), "None") + '\n')
                index = global_dict[origin_id]+1
                global_dict[origin_id] = index
        elif 'score' in request.form and request.form["score"] == "3":
            index = global_dict[origin_id]
            if origin_id in result_dict:
                result_dict[origin_id].append([videos[index], request.form["score"], "None", "None"])
            else:
                result_dict[origin_id]= [[videos[index], request.form["score"], "None", "None"]]
            with open("static/result.txt", "a") as f:
                f.write('id: {}, video: {}, label:{}, scene:{}, other:{}'.format(origin_id, videos[index], request.form["score"], "None", "None") + '\n')
            index = global_dict[origin_id]+1
            global_dict[origin_id] = index
        else:
            if 'score' not in request.form:
                flash("请选择视频类别")
            elif 'scene' not in request.form:
                flash("请选择运动类型")
            index = global_dict[origin_id]
    else:
        origin_id = int(request.args['id'])
        if origin_id in global_dict:
            index = global_dict[origin_id]
        else:
            index = SHARED//3 * video_per_person
            global_dict[origin_id] = index
    if index >= SHARED//3*video_per_person + video_per_person or index==len(videos):
        return '<h1> 标注结束，感谢你的参与！</h1>'
    video = videos[index]
    
    # status = getHttpStatusCode(link + video)
    # while status != 200:
    #     error_list.append(video)
    #     pickle.dump(error_list, open("error_videos.pkl", "wb"))
    #     index = global_dict[origin_id]+1
    #     global_dict[origin_id] = index
    #     if index >= SHARED//3*video_per_person + video_per_person or index==len(videos):
    #         return '<h1> 标注结束，感谢你的参与！</h1>'
    #     video = videos[index]
    #     status = getHttpStatusCode(link + video)
    return render_template('index3.html', video=link+video, origin_id=origin_id)

@app.route('/request')
def my_request():
    pickle.dump(result_dict, open("static/result_dict.pkl", "wb"))
    return str(result_dict)

@app.route('/result')
def result_count():
    score_dict={"1":"正样本", "2":"不确定", "3":"负样本"}
    print_str = ''
    my_label = minelabels[5]
    my_dict = {}
    for i in my_label:
        my_dict[i[0]] = int(i[1])
    for key in result_dict:
        print_str += " 第%s个标注员: <br>"%str(key)
        result = result_dict[key]
        for r in result:
            if r[0] in my_dict:
                if int(r[1]) != my_dict[r[0]]:
                    print_str += " 视频链接： %s"%link + r[0]\
                                + " 标注员的标注： " + score_dict[str(r[1])] + " 正确的标注： " + score_dict[str(my_dict[r[0]])] + "<br>"
    return print_str


@app.route('/examples')
def example():
    web = "https://loopingvideos.blob.core.windows.net/videos/example/"
    translate_dict = {'negative1.mp4':"负样本1", 'negative2.mp4':"负样本2", 'negative3.mp4':"负样本3", 'rotting.mp4':"腐烂", 
                        'smoke.mp4':"烟", 'star.mp4':"星空", 'traffic.mp4':"车流", 'waterfall_stream.mp4':"瀑布溪流", 'water_sea.mp4':"水（海洋湖面）", 
                        'blossom.mp4':"花开", 'cloud.mp4':"云", 'cloudandhayfield.mp4':"云和田野草堆", 'crowd.mp4':"人群", 'melting.mp4':"融化"}
    example_videos = [web + v for v in examples]
    video_names = [translate_dict[v] for v in examples]

    return render_template('index2.html', video=example_videos, video_name=video_names)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    # app.run(threaded=True)
    app.run(host="0.0.0.0", threaded=True)