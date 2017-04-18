from flask import Flask, render_template, request
from forms import SummonerForm
import backend
import simplejson as json
import os
app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
def index():
    form = SummonerForm()
    return render_template('index.html',
                           title = "Tester page",
                           form = form)

@app.errorhandler(404)
def fucked(reason="Can't find what you're looking for"):
    return render_template('notfound.html',
                           reason=reason)

@app.route('/viewgame', methods=['POST'])
def viewgame():
    test = True
    name = request.form['name']
    region = request.form['region']
    key = os.environ.get('rito_api_key')
    if not test:
        config = backend.get_config(name, region, key)
        if not config:
            return fucked("Couldn't find Summoner: %s in %s" % (name, region))

        match = backend.get_match(config, test=True)
        if not match:
            return fucked("%s is not in a game" % (name))

        friend, bully = backend.load_match(match[0], match[1], config)
    else:
        filename = open('refined_testdata.json')
        x = json.load(filename)
        filename.close()
        friend, bully = x['Friends'], x['Bullies']

    return render_template('results.html',
                           title='Results',
                           name = name,
                           friend = friend,
                           bully = bully)


if __name__=="__main__":
    app.run()
