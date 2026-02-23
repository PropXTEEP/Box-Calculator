# Updated app.py with background image support

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Assume you have an index.html that includes background image support

if __name__ == '__main__':
    app.run(debug=True)