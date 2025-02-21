from flask import Flask, render_template
from pages.distribution import distribution_blueprint
from pages.simulation import simulation_blueprint 

app = Flask(
    __name__, 
    static_folder='../frontend/static',  
    static_url_path='/static', 
    template_folder='../frontend'  
)

app.secret_key = 'mathtools'

app.register_blueprint(distribution_blueprint, url_prefix='/distribution')
app.register_blueprint(simulation_blueprint, url_prefix='/simulation')  

@app.route('/')
def index():
    return render_template('index.html') 

if __name__ == '__main__':
    app.run(debug=True)
