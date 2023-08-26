from flask import Flask, render_template, request
from markupsafe import escape

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users/<username>')
def profile(username):
    return render_template('profile.html', username=escape(username))


if __name__ == '__main__':
    app.run()
