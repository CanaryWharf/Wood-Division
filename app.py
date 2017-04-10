from flask import Flask, render_template, request, url_for
from forms import SummonerForm
import backend
import os
import simplejson as json
app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
def index():
    form = SummonerForm()
    return render_template('index.html',
                           title = "Tester page",
                           form = form)

def fucked(reason):
    return render_template('notfound.html',
                           reason=reason)

@app.route('/viewgame', methods=['POST'])
def viewgame():
    name = request.form['name']
    region = request.form['region']
    key = os.environ.get('rito_api_key')
    config = backend.getConfig(name, region, key)
    if not config:
        fucked("Couldn't find Summoner: %s in %s" % (name, region))

    match = backend.get_match(config)
    if not match:
        return fucked("%s is not in a game" % (name))

    santised_data = backend.load_match()

    return render_template('results.html',
                           title='Name Page',
                           name = name)


if __name__=="__main__":
    app.run()
