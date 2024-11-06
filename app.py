from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.get('/')
def index():
    makeRequest()
    return render_template('home_page.html')

def makeRequest():
    api_key = 'fafe5690'
    base_url = 'http://www.omdbapi.com/'
    title = "Inception"
    params = {
        'apikey': api_key,
        't': title
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        print(data)  # This will print the movie data
    else:
        print(f"Error: {response.status_code}")
