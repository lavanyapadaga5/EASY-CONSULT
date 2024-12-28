from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Used for session management

# Dummy data for demonstration
users = {"testuser": {"password": "testpass", "email": "test@example.com"}}
appointments = {"testuser": {}}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template('login.html', msg="")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in users:
            flash("Username already exists. Try another.")
        else:
            users[username] = {"password": password, "email": email}
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
    return render_template('register.html', msg="")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_appointments = appointments.get(username, {})
    return render_template('dashboard.html', username=username, appointments=user_appointments)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    if request.method == 'POST':
        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']

        if username not in appointments:
            appointments[username] = {}
        if doctor not in appointments[username]:
            appointments[username][doctor] = []

        appointments[username][doctor].append(f"{date} {time}")
        flash("Appointment scheduled successfully!")
        return redirect(url_for('dashboard'))

    doctors = ["Dr. Smith", "Dr. Patel", "Dr. Khan"]  # Example doctor list
    return render_template('schedule.html', doctors=doctors)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
