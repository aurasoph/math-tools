from flask import Flask, render_template
from flask_cors import CORS
from pages.distribution import distribution_blueprint
from pages.page2 import page2_blueprint 

app = Flask(
    __name__, 
    static_folder='../frontend/static',  
    static_url_path='/static', 
    template_folder='../frontend'  
)

CORS(app, resources={r"/*": {"origins": ["https://www.luntontius.site", "http://localhost:3000"]}})

app.secret_key = 'mathtools'

app.register_blueprint(distribution_blueprint, url_prefix='/distribution')
app.register_blueprint(page2_blueprint, url_prefix='/page2')  

@app.route('/')
def index():
    return render_template('index.html') 

if __name__ == '__main__':
    app.run(debug=True)
