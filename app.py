from flask import Flask
import db

app = Flask(__name__)
db.init_app(app)


@app.route("/")
def hello_world():
    return "hello!"

@app.route("/seat/info")
def get_seat_info():
    obj = {
            "id": 1,
            "row": 2,
            "col": 3
        }
    return "JSON()"