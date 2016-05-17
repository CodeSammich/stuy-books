from flask import Flask, render_template, url_for, session, request


app = Flask(__name__)

@app.route('/')
@app.route("/home/")
def home():
    return render_template("home.html")

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method == "GET":
        return render_template("login.html")
    else:
        uname = request.form['uname']
        pword = request.form['pword']

        if accounts.isValue(uname,pword):
            session['uname'] = uname
            return redirect(url_for("home"))
        return render_template("login.html")

@app.route("/signup")
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        uname = request.form['uname']
        pwrd = request.form['pword']
        if accounts.newUser(uname,pword):
            msg = "Account created"
            return render_template("signup.html", msg=msg)
        else:
            msg = "Failed to create account"
            return render_template("signup.html", msg=msg)

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0',port=8000)
