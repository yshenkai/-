
import flask
import json
app=flask.Flask(__name__)
@app.route("/classification",methods=["POST"])
def getArticleCf():
    result = {"success": False}
    if flask.request.method == "POST":
        if flask.request.get_data():
            a = json.loads(flask.request.json)["a"]
            result["a"]=a
            result["success"]=True
    return flask.jsonify(result)
if __name__=="__main__":
    print(("* Loading Keras model and Flask staring server...."
           "please wait until server has fully started"))
    app.run(host='0.0.0.0')
