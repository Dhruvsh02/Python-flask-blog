from flask import Flask , render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
    name = "Dhruv Sharma"
    return render_template("about.html" , name2=name)

@app.route("/bootstrap")
def bootstrap():
    return render_template("bootstrap.html")

if __name__ == "__main__":
    app.run(debug=True) 
    