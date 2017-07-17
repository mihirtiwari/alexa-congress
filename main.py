from flask import Flask
from flask_ask import Ask, question, statement, session
import requests, json, os
import logging

app = Flask(__name__)
ask = Ask(app, '/')

app.config['ASK_APPLICATION_ID'] = os.environ['APP_ID']
app.config['ASK_VERIFY_REQUESTS'] = True

MEMBERS_URL = "https://api.propublica.org/congress/v1/members/"
API_KEY = os.environ['API_KEY']
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
    'Washington DC': 'DC',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

@app.route('/')
def home():
    return 'Hello World!'

def get_senators(postal_code):
    url = MEMBERS_URL + "senate/" + postal_code + "/current.json"
    senators = {}
    req = requests.get(url, headers=HEADERS)

    if req.status_code is not 200:
        return []

    r = req.json()

    parties = {
        "D": "Democrat",
        "R": "Republican",
        "I": "Independent"
    }

    if len(r["results"]) == 0:
        return []

    for result in r["results"]:
        name = result["name"]
        party = parties[result["party"]]

        senators[name] = party

    return senators

def get_house_reps(postal_code, district):
    url = MEMBERS_URL + "house/" + postal_code + "/" + district + "/current.json"
    house = {}
    req = requests.get(url, headers=HEADERS)
    r = req.json()

    if r['status'] == 'ERROR':
        return ['none']

    if r['status'] != 'OK':
        return []

    parties = {
        "D": "Democrat",
        "R": "Republican",
        "I": "Independent"
    }

    for result in r["results"]:
        name = result["name"]
        party = parties[result["party"]]

        house[name] = party

    return house

def get_num_reps(postal_code):
    url = MEMBERS_URL + "house/" + postal_code + "/current.json"
    house = {}
    req = requests.get(url, headers=HEADERS)

    if req.status_code is not 200:
        return -1

    r = req.json()

    return len(r['results'])

@ask.launch
def start():
    q = "Hello, welcome to Congress Reps! For help, say \'Help\'. What would you like to know about our Congress?"
    return question(q)

@ask.intent('SenateStateIntent')
def senators_state(state):
    if state is None:
        return statement("Your request could not be processed.")
    found = False
    for s in us_state_abbrev.keys():
        if state.lower() == s.lower() or state.lower() == us_state_abbrev[s].lower():
            state = s
            found = True

    if found is False:
        return statement("Invalid state given.")

    senators = get_senators(us_state_abbrev[state])
    if len(senators) is 0:
        return statement("Your request could not be processed.")

    s = "Your senators are: "

    s += "Senator " + senators.keys()[0] + " (" + senators[senators.keys()[0]] + ") and "
    s += "Senator " + senators.keys()[1] + " (" + senators[senators.keys()[1]] + ")."

    card_statement = "The senators for " + state + " are: Senator "
    card_statement += senators.keys()[0] + " (" + senators[senators.keys()[0]] + ") and "
    card_statement += "Senator " + senators.keys()[1] + " (" + senators[senators.keys()[1]] + ")."

    return statement(s).simple_card(title="Congress Reps says...", content=card_statement)

@ask.intent('ChoiceSpokenIntent')
def choice_spoken(choice):
    if not session.attributes:
        return statement("Your request could not be processed.")
    if choice.find('senate') != -1 or choice.find('senator') != -1:
        session.attributes['senate_or_house'] = 'senate'
        q = 'What state would you like senators for?'
        return question(q)
    elif choice.find('rep') != -1 or choice.find('representative') != -1 or choice.find('house of representatives') != -1:
        session.attributes['senate_or_house'] = 'house'
        q = 'What state would you like representatives for?'
        return question(q)
    else:
        return statement('Your request could not be processed.')

@ask.intent('StateSpokenIntent')
def state_spoken(state):
    if not session.attributes:
        return statement("Your request could not be processed.")
    SENATE_OR_HOUSE = session.attributes['senate_or_house']
    if SENATE_OR_HOUSE == 'senate':
        return senators_state(state)
    elif SENATE_OR_HOUSE == 'house':
        session.attributes['state'] = state
        q = "What district would you like representatives for?"

        return question(q);
    else:
        return statement('Your request could not be processed.')

@ask.intent('HouseStateSeparateIntent')
def house_state_separate(state):
    if state is None:
        return statement("Your request could not be processed.")
    session.attributes['senate_or_house'] = 'house'
    found = False
    for s in us_state_abbrev.keys():
        if state.lower() == s.lower() or state.lower() == us_state_abbrev[s].lower():
            state = s
            found = True

    if found is False:
        return statement("Invalid state given.")

    return state_spoken(state)

@ask.intent('HouseStateDistrictSeparateIntent')
def house_state_district_separate(district):
    state = session.attributes['state']
    if state is None:
        return statement('Invalid request given.')

    return house_proper(state, district)

@ask.intent('HouseProperIntent')
def house_proper(state, district):
    if state is None:
        return statement("Your request could not be processed.")
    found = False
    for s in us_state_abbrev.keys():
        if state.lower() == s.lower() or state.lower() == us_state_abbrev[s].lower():
            state = s
            found = True

    if found is False:
        return statement("Invalid state given.")

    house = get_house_reps(us_state_abbrev[state], district)

    if len(house) is 0:
        return statement("Your request could not be processed.")

    if type(house) is list and house[0] == 'none':
        return statement('The district provided does not exist')

    h = "Your representative is " + house.keys()[0] + " (" + house[house.keys()[0]] + ")"

    card_statement = "The representative for " + state + " district " + str(district)
    card_statement += " is representative " + house.keys()[0] + " (" + house[house.keys()[0]] + ")"

    return statement(h).simple_card(title="Congress Reps says...", content=card_statement)

@ask.intent('NumberofRepsTotalIntent')
def num_reps():
    s = 'Currently there are 435 representatives in the House of Representatives.'
    return statement(s).simple_card(title="Congress Reps says...", content=s)

@ask.intent('NumberofRepsStateIntent')
def num_reps_state(state):
    found = False
    for s in us_state_abbrev.keys():
        if state.lower() == s.lower() or state.lower() == us_state_abbrev[s].lower():
            state = s
            found = True

    if found is False:
        return statement("Invalid state given.")

    num = get_num_reps(us_state_abbrev[state])

    if num == -1:
        return statement("Your request could not be processed.")

    s = 'There are ' + str(num) + ' representatives in the state of ' + state

    return statement(s).simple_card(title="Congress Reps says...", content=s)

@ask.intent('NumberofSenatorsIntent')
def num_senators():
    s = 'Currently there are 100 senators in the Senate'
    return statement(s).simple_card(title="Congress Reps says...", content=s)

@ask.intent('NumberofSenatorsStateIntent')
def num_senators_state(state):
    if state is None:
        return statement("Your request could not be processed.")
    found = False
    for s in us_state_abbrev.keys():
        if state.lower() == s.lower() or state.lower() == us_state_abbrev[s].lower():
            state = s
            found = True

    if found is False:
        return statement("Invalid state given.")

    s = 'There are 2 senators in the state of ' + state

    return statement(s).simple_card(title="Congress Reps says...", content=s)

@ask.intent('AMAZON.HelpIntent')
def help():
    s = 'Thanks for using Congress Reps! To know a state\'s senators, say \'Who are the senators'
    s += ' for...\' and then the state name. To know a state\'s representatives by district, say '
    s += '\'Who is the representative for...\' and then the state name and then \' ...for district...\' '
    s += 'and then the district number. To ask how many senators a state has, ask \'How many senators'
    s += ' for...\' and then the state\'s name. To ask how many representatives a state has, ask '
    s += '\'How many representatives for...\' and then the state\'s name.'

    return statement(s);

@ask.intent('AMAZON.StopIntent')
def canceled():
    s = "Goodbye."

    return statement(s)

@ask.session_ended
def session_ended():
    return "{}", 200

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
    app.config['ASK_APPLICATION_ID'] = os.environ['APP_ID']
    app.config['ASK_VERIFY_REQUESTS'] = True
