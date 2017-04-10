from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField


class SummonerForm(Form):
    name = StringField("Name")
    region = SelectField('Region', choices = [('EUW','EUW'), ('NA', 'NA'), ('BR', 'BR'), ('EUNE', 'EUNE'),
                                              ('LAN', 'LAN'), ('LAS', 'LAS'), ('OCE', 'OCE'), ('RU', 'RU'),
                                              ('TR', 'TR'), ('JP', 'JP'), ('SEA', 'SEA'), ('KR', 'KR')])
    submit = SubmitField(label="Submit")
