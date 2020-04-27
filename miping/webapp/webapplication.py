from flask import Flask


app = Flask(__name__)

"""TODO"""


@app.route("/api/get")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


if __name__ == "__main__":
    app.run(host='127.0.0.1')
