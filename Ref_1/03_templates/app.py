from flask import Flask, request, render_template
app = Flask(__name__)
 
@app.route('/')
def index():
    name, age = "Jerry", 28
    template_context = dict(name=name, age=age)
    return render_template('index.html', **template_context)

if __name__ == "__main__":
    app.run(debug=True)