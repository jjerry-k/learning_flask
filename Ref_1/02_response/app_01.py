from flask import Flask, request, g, abort
 
app = Flask(__name__)
 
@app.before_first_request
def before_first_request():
    print("before_first_request() called")
 
@app.before_request
def before_request():
    print("before_request() called")
 
@app.after_request
def after_request(response):
    print("after_request() called")
    return response
 
@app.errorhandler(404)
def http_404_handler(error):
    return "<p>HTTP 404 Error Encountered</p>", 404
 
@app.errorhandler(500)
def http_500_handler(error):
    return "<p>HTTP 500 Error Encountered</p>", 500

@app.route("/")
def index():
    return "Hello World"

@app.route("/info")
def info():
    abort(404)
 
@app.route("/about")
def about():
    abort(500)

if __name__ == "__main__":
    app.run(debug=True)