__author__ = "Niall Nolan"
__version__ = "1.0.0"

from flask import Flask, request, render_template
import requests


# Initialise our web app.
app = Flask(__name__)

# You can use a Python file to configure your apps' environment variables, such a debug mode on/off.
app.config.from_pyfile('config.py')


# A route is a place on our website. '/' is the main page. '/About' would be a sub-page.
@app.route('/')
# http://127.0.0.1:5000/
def homepage():
    # Display our homepage HTML file.
    return render_template('index.html')


@app.route('/', methods=['POST', 'GET'])
def api_call():
    errors = []
    if request.method == 'POST':
        # Retrieve user specified word from form in 'index.html' with name attribute 'user_word'.
        user_word = request.form['user_word']

        try:
            if user_word == '':
                errors.append(f'Please type a word, then click Search.')
                return render_template('index.html', errors=errors)

            # Query Google's dictionary API with the user's word.
            # Syntax of URL request to the API is, e.g. 'https://api.dictionaryapi.dev/api/v2/entries/en_US/hello'.
            response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en_GB/{user_word}')
            # Save the response as in json format.
            results = response.json()

            # API response is a list.
            # A list item contains a main dictionary with keys ['word'], ['phonetics'] and ['meanings'].
            # Words can have many meanings. The API returns one ['meaning'] key per list item.
            # Retrieve the number of meaning keys.
            no_of_meanings = len(results)

            # Retrieve the value for each dictionary key wanted and append to a new list.
            results_laid_out = []

            word = results[0].get('word')
            results_laid_out.append(word)

            phonetics_text = results[0].get('phonetics')[0].get('text')
            results_laid_out.append(phonetics_text)

            # However, inception-like, the API may return multiple definitions per meaning.
            # A word can have one meaning with three definitions or two meanings with two definitions respectively.
            # Each definition is within dictionary key ['definitions'] per meaning.
            # Get the definitions and the number of definitions.
            definitions = []
            n = 0
            while n < no_of_meanings:
                definitions += [item['meanings'] for item in results if (item['meanings'])][n]
                n += 1

            no_of_definitions = len(definitions)

            each_definition = []
            for item in definitions:
                each_definition.append(item['definitions'][0]['definition'])

            # Add the definitions to 'results_laid_out'.
            results_laid_out.append(each_definition)

            # Create dictionary of our results to be displayed easily in our homepage.
            results_dict = {
                'Word:': results_laid_out[0],
                'Phonetics text:': results_laid_out[1],
                'Definitions:': results_laid_out[2]
            }

            return render_template('index.html', errors=errors, results=results_dict.items())

        except KeyError:
            # Occurs when there are no API results for the user's word.
            errors.append(f'No results found for {user_word}. Please check spelling or try another word.')
            return render_template('index.html', errors=errors)


@app.errorhandler(404)
def page_not_found(e):
    # The '404' below return 404 response code to the debugger, so we see clearly user got 404.
    return '<h1>404</h1><p>The resource could not be found.</p>', 404


if __name__ == '__main__':
    # Run the app. It is hosted at http://127.0.0.1:5000/ (a.k.a http://localhost:5000/).
    app.run()

