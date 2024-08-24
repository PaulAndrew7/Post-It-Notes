from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime as dt
import sqlite3


app = Flask(__name__)

@app.route('/')
def loginPage():
    return render_template('login.html')
# ... (previous code)

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        connection = sqlite3.connect('loginData.db', check_same_thread=False)
        cursor = connection.cursor()

        # Check if the email is already registered
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # User with the same email already exists
            return render_template('login.html', error='Email already registered.')

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, password))

        connection.commit()
        connection.close()

        # Redirect to the home page after successful registration
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Extract email and password from the form
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        connection = sqlite3.connect('loginData.db')
        cursor = connection.cursor()

        # Check if the user exists and the password is correct
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        connection.close()

        if user:
            # User exists, redirect to the home page after successful login
            print("Login Success")
            return redirect(url_for('index'))
        else:
            # User not found or incorrect password, show an error
            print("Login error")
            return render_template('login.html', error='Invalid email or password.')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/create', methods=['POST'])
def submit():
    connect = sqlite3.connect('data.db', check_same_thread=False)
    cursor = connect.cursor()

    title = request.form['title']
    desc = request.form['desc']

    dateCreated = dt.today().date()
    hourCreated = '0'+str(dt.now().hour) if dt.now().hour<10 else str(dt.now().hour)
    minCreated = '0'+str(dt.now().minute) if dt.now().minute < 10 else str(dt.now().minute)
   

    
    record = [(title, desc, str(dateCreated), str(hourCreated) + ':' + str(minCreated))]
    # Inside the /create route
    try:
        cursor.executemany("INSERT INTO notes VALUES (?, ?, ?, ?)", record)
        connect.commit()
        return render_template('success.html')
    except sqlite3.IntegrityError:
        connect.rollback()  # Rollback the transaction
        error_message = 'Note with the same title already exists.'
        return render_template('create.html', error=error_message)
    finally:
        connect.close()
        

@app.route('/display')
def displayNotes():
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    cursor.execute("SELECT noteTitle, noteDesc, date, time FROM notes")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('display.html', rows=rows)


@app.route('/note/<int:note_id>')
def display_note(note_id):
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notes WHERE rowid = ?", (note_id,))
    note = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('note.html', note=note, note_id=note_id)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()

    if request.method == 'POST':
        # Handle the note update here
        title = request.form['title']
        desc = request.form['desc']

        cursor.execute("UPDATE notes SET noteTitle = ?, noteDesc = ? WHERE rowid = ?", (title, desc, note_id))

        connection.commit()

        cursor.execute("SELECT * FROM notes WHERE rowid = ?", (note_id,))
        note = cursor.fetchone()

        return render_template('note.html', note=note, note_id=note_id)
    else:
        cursor.execute("SELECT * FROM notes WHERE rowid = ?", (note_id,))
        note = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return render_template('edit.html', note=note, note_id=note_id)

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()

    # Delete the note with the given note_id
    cursor.execute("DELETE FROM notes WHERE rowid = ?", (note_id,))

    # Retrieve the remaining notes
    cursor.execute("SELECT rowid, * FROM notes")
    remaining_notes = cursor.fetchall()

    # Reassign primary key values for continuity
    for index, note in enumerate(remaining_notes, start=1):
        cursor.execute("UPDATE notes SET rowid = ? WHERE rowid = ?", (index, note[0]))

    connection.commit()
    connection.close()

    return redirect(url_for('displayNotes'))

if __name__ == '__main__':
    app.run(debug=True)
