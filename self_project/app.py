from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    # return home.html
    return render_template('home.html') 

@app.route('/about')
def about():
    #return info.html
    context = dict(name='Jerry', age=28, gender="Male")
    return render_template('about.html', **context)

@app.route('/lwd')
def lwd():
    return render_template('lwd.html')

if __name__ == '__main__':
    app.run(debug=True)