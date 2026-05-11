from flask import Flask, render_template, request, redirect, session
from database import get_connection

app = Flask(__name__)
app.secret_key = 'secretkey'


# ---------------- INICIO ----------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------- REGISTRO ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()

        # verificar si correo existe
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user:
            return "El correo ya existe"

        # insertar usuario
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        values = (name, email, password)

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s AND password = %s"

        values = (email, password)

        cursor.execute(query, values)

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            session['user_id'] = user['id']
            session['user_name'] = user['name']

            return redirect('/dashboard')

        else:
            return "Correo o contraseña incorrectos"

    return render_template('login.html')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('dashboard.html')

# ---------------- CREAR ENCUESTA ----------------

@app.route('/create_survey', methods=['GET', 'POST'])
def create_survey():

    if request.method == 'POST':

        title = request.form['title']

        conn = get_connection()
        cursor = conn.cursor()

        # guardar encuesta
        query = "INSERT INTO surveys (title) VALUES (%s)"
        cursor.execute(query, (title,))

        conn.commit()

        # obtener id encuesta
        survey_id = cursor.lastrowid

        # preguntas
        question1 = request.form['question1']
        question2 = request.form['question2']
        question3 = request.form['question3']

        questions = [question1, question2, question3]

        for question in questions:

            query = "INSERT INTO questions (survey_id, question_text) VALUES (%s, %s)"

            values = (survey_id, question)

            cursor.execute(query, values)

            conn.commit()

            # obtener id pregunta
            question_id = cursor.lastrowid

            # opciones
            option1 = request.form[f'option1_{question}']
            option2 = request.form[f'option2_{question}']

            query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
            cursor.execute(query, (question_id, option1))

            query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
            cursor.execute(query, (question_id, option2))

            conn.commit()

        cursor.close()
        conn.close()

        return "Encuesta creada"

    return render_template('create_survey.html')


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)