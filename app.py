from flask import Flask, render_template
from pages.distribution import distribution_blueprint
from pages.page2 import page2_blueprint 

app = Flask(__name__, static_folder='static', static_url_path='/static')

app.secret_key = 'mathtools'

app.register_blueprint(distribution_blueprint, url_prefix='/distribution')
app.register_blueprint(page2_blueprint, url_prefix='/page2')  

@app.route('/')
def index():
    return render_template('index.html')  

if __name__ == '__main__':
    app.run(debug=True)
