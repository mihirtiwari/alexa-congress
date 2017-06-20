from flask import Flask

app = Flask(__name__)
ask = Ask(app, '/')

@app.route('/')
def home():
    return 'Hello World!'

def get_senators(state):
    # return array of senators' names

@ask.launch()
def start():
    q = "Hello, what would you like to know about?"
    return question(q)

@ask.intent('SenateNoStateIntent')
def senators_no_state():
    q = "What state would you like senators for?"
    return question(q)

@ask.intent('SenateStateIntent')
def senators_state():
    senators = get_senators()
    s = "Your senators are "
    for x in range(0, len(senators)):
         statement += senators[x] + ', ' if x == len(senators) - 1 else statement += 'and ' + senators[x] + '.';

    return statement(s)
    
# https://pythonprogramming.net/intro-alexa-skill-flask-ask-python-tutorial/
# https://github.com/johnwheeler/flask-ask
# https://www.youtube.com/watch?v=cXL8FDUag-s&list=PL6LVC9c1eflVHEbiNb0_dQF0LGLLrZtNL
# https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/Flask-Ask-A-New-Python-Framework-for-Rapid-Alexa-Skills-Kit-Development
# https://projects.propublica.org/api-docs/congress-api/endpoints/

if __name__ == '__main__':
    app.run(debug=True)
