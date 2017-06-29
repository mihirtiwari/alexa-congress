from flask import Flask
from flask_ask import Ask, question, statement
import requests, json

app = Flask(__name__)
ask = Ask(app, '/')

MEMBERS_URL = "https://api.propublica.org/congress/v1/members/"
API_KEY = ""
HEADERS = {"X-API-Key": API_KEY}

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'Washington, DC': 'DC',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

@app.route('/')
def home():
    return 'Hello World!'

def get_senators(postal_code):
    # return array of senators' names
    url = MEMBERS_URL + "senate/" + postal_code + "/current.json"
    senators = {}
    req = requests.get(url, headers=HEADERS)

    if req.status_code is not requests.code.ok:
        return []

    r = req.json()

    parties = {
        "D": "Democrat",
        "R": "Republican",
        "I": "Independent"
    }

    for result in r["results"]:
        name = result["name"]
        party = parties[result["party"]]

        senators[name] = party

    return senators

@ask.launch
def start():
    q = "Hello, what would you like to know about?"
    return question(q)

@ask.intent('SenateNoStateIntent')
def senators_no_state():
    q = "What state would you like senators for?"
    return question(q)

@ask.intent('SenateStateIntent')
def senators_state(state):
    if state not in us_state_abbrev.keys():
        return statement("Invalid state given.")

    senators = get_senators(us_state_abbrev[state])
    if len(senators) is 0:
        return statement("Your request could not be processed.")

    s = "Your senators are: \n"

    s += "Senator " + senators.keys()[0] + " (" + senators[senators.keys()[0]] + ") and "
    s += "Senator " + senators.keys()[1] + " (" + senators[senators.keys()[1]] + ")."

    return statement(s)

@ask.session_ended
def session_ended():
    return "{}", 200
# https://pythonprogramming.net/intro-alexa-skill-flask-ask-python-tutorial/
# https://github.com/johnwheeler/flask-ask
# https://www.youtube.com/watch?v=cXL8FDUag-s&list=PL6LVC9c1eflVHEbiNb0_dQF0LGLLrZtNL
# https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/Flask-Ask-A-New-Python-Framework-for-Rapid-Alexa-Skills-Kit-Development
# https://projects.propublica.org/api-docs/congress-api/endpoints/

if __name__ == '__main__':
    app.run(debug=True)
