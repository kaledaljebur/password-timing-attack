from flask import Flask, request, render_template_string, redirect, url_for
from time import sleep

app = Flask(__name__)

USERNAME = "admin"
PASSWORD = "p4ss"

LOGIN_FORM = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login</h2>
    <form method="POST" action="/login">
        <label>Username: <input type="text" name="username"></label><br><br>
        <label>Password: <input type="password" name="password"></label><br><br>
        <button type="submit">Login</button>
    </form>
    {% if error %}
    <p style="color:red;">{{ error }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        print(f"[DEBUG] Received: {username}:{password}")
        if username == USERNAME:
            correct = True
            for i in range(len(PASSWORD)):
                if i >= len(password) or password[i] != PASSWORD[i]:
                    correct = False
                    break
                sleep(0.05)  
            print(f"[DEBUG] correct={correct} | full_match={password == PASSWORD}")
            if correct and password == PASSWORD:
                return "<h3>Welcome, you are logged in!</h3>", 200
        error = "Invalid username or password"
        return render_template_string(LOGIN_FORM, error=error), 401
    return render_template_string(LOGIN_FORM, error=error), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
