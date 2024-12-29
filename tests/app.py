from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/change_color')
def change_color():
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return jsonify(color=color)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080)
