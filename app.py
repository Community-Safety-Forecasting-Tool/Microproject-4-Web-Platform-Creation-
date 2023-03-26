from flask import Flask
from backend import DataModel
app = Flask(__name__, static_url_path='/static')


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/refresh')
def refresh():
    Model = DataModel()
    Model.gen_csv()
    return 'Done!'


if __name__ == '__main__':
    app.run()
