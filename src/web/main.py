from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    @app.route('/')
    def main_page():
        return render_template('index.html', name="Mirhan", array=[{"name":"Matilda"}, {"name": "Selim"}])
    return app