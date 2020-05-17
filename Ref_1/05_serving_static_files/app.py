from flask import Flask, render_template
app = Flask(__name__)
 
@app.route('/')
def index():
    name, nick, age, condition_1, condition_2 = "Kim", "Jerry", 28, False, False
    template_context = dict(name=name, nick=nick, age=age, 
                            condition_1=condition_1, condition_2=condition_2)
    return render_template('index.html', **template_context)

if __name__ == "__main__":
    app.run(debug=True)