
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import flask
import io
from model import get_model
from Total_1 import generator_image
# from model1 import get_model
import os
app=flask.Flask(__name__)
model=None
def load_model():
    global model
    model=get_model()
    model.summary()


def prepare_image(image,target):
    if image.mode!="RGB":
        image=image.convert("RGB")
    image=image.resize(target)
    image=img_to_array(image)/255.
    image=np.expand_dims(image,axis=0)
    #image=imagenet_utils.preprocess_input(image)
    return image

# @app.route("/predict",methods=["POST"])
def predict(image_path):
    data={"success":False}
    # if flask.request.method=="POST":
    #     if flask.request.files.get("image"):
    #image=flask.request.files["image"].read()
    image=Image.open(image_path)
    image=prepare_image(image,target=(256,256))

    preds=model.predict(image)
    print("=========>",preds)
    data["predictions"]=str(np.argmax(preds))
    data['prob']=str(preds[0][0])
    # r={"label":preds}
    #
    #
    # data["predictions"]=[]
    # data["predictions"].append(r)
    # for (imagenetID,label,prob) in result[0]:
    #     r={"label":label,"probability":float(prob)}
    #     data["predictions"].append(r)

    data["success"]=True
    return data


@app.route("/process",methods=["POST"])
def process():
    data={"success":False}
    if flask.request.method=="POST":
        if flask.request.files.get("wavfile"):
            wavfile=flask.request.files["wavfile"].read()
            pathlist=generator_image(wavfile,"data/picture/")
            numimage=len(pathlist)
            label=0
            score=0.0
            for i in pathlist:
                path=os.path.join("data/picture/",i)
                data_image=predict(path)
                label+=int(data_image["predictions"])
                score+=float(data_image["prob"])
            label =1 if label==numimage else 0
            score/=numimage
            data["label"]=label
            data["score"]=score
            print("label=",label)
            print("score=",score)
            # preds=model.predict(image)
            # print("=========>",preds)
            # data["predictions"]=str(np.argmax(preds))
            # data['prob']=str(preds[0][0])
            # r={"label":preds}
            #
            #
            # data["predictions"]=[]
            # data["predictions"].append(r)
            # for (imagenetID,label,prob) in result[0]:
            #     r={"label":label,"probability":float(prob)}
            #     data["predictions"].append(r)

            data["success"]=True
    return flask.jsonify(data)

if __name__=="__main__":
    print(("* Loading Keras model and Flask staring server...."
           "please wait until server has fully started"))
    load_model()
    app.run(host='0.0.0.0')

