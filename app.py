from flask import Flask, render_template, request, redirect, session
from database import get_connection

app = Flask(__name__)
app.secret_key = 'secretkey'


# INICIO 

@app.route('/')
def index():

    if 'user_id' in session:
        return redirect('/dashboard')

    return redirect('/login')


# REGISTRO 

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


# LOGIN 

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
            session['role'] = user['role']

            return redirect('/dashboard')

        else:
            return "Correo o contraseña incorrectos"

    return render_template('login.html')


# DASHBOARD 

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('dashboard.html')

# CREAR ENCUESTA 

@app.route('/create_survey', methods=['GET', 'POST'])
def create_survey():

    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return "Acceso denegado"

    if request.method == 'POST':

        conn = get_connection()
        cursor = conn.cursor()

        title = request.form['title']

        # guardar encuesta
        query = "INSERT INTO surveys (title) VALUES (%s)"
        cursor.execute(query, (title,))

        conn.commit()

        survey_id = cursor.lastrowid

        #pregunta 1

        q1 = request.form['q1']

        query = "INSERT INTO questions (survey_id, question_text) VALUES (%s, %s)"
        cursor.execute(query, (survey_id, q1))

        conn.commit()

        q1_id = cursor.lastrowid

        op1_q1 = request.form['op1_q1']
        op2_q1 = request.form['op2_q1']

        query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
        cursor.execute(query, (q1_id, op1_q1))

        query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
        cursor.execute(query, (q1_id, op2_q1))

        conn.commit()

        #pregunta 2

        q2 = request.form['q2']

        query = "INSERT INTO questions (survey_id, question_text) VALUES (%s, %s)"
        cursor.execute(query, (survey_id, q2))

        conn.commit()

        q2_id = cursor.lastrowid

        op1_q2 = request.form['op1_q2']
        op2_q2 = request.form['op2_q2']

        query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
        cursor.execute(query, (q2_id, op1_q2))

        query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
        cursor.execute(query, (q2_id, op2_q2))

        conn.commit()

        #pregunta 3

        q3 = request.form['q3']

        query = "INSERT INTO questions (survey_id, question_text) VALUES (%s, %s)"
        cursor.execute(query, (survey_id, q3))

        conn.commit()

        q3_id = cursor.lastrowid

        op1_q3 = request.form['op1_q3']
        op2_q3 = request.form['op2_q3']

        query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
        cursor.execute(query, (q3_id, op1_q3))

        query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s)"
        cursor.execute(query, (q3_id, op2_q3))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/dashboard?message=created')

    return render_template('create_survey.html')


#  VER ENCUESTAS 

@app.route('/surveys')
def surveys():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM surveys"
    cursor.execute(query)

    surveys = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('surveys.html', surveys=surveys)





#RESPONDER ENCUESTA 

@app.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
def survey(survey_id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # verificar si ya respondió
    query = "SELECT * FROM answers WHERE user_id = %s AND survey_id = %s"

    values = (session['user_id'], survey_id)

    cursor.execute(query, values)

    existing_answer = cursor.fetchone()

    if existing_answer:
        return "Ya respondiste esta encuesta"

    # obtener preguntas
    query = "SELECT * FROM questions WHERE survey_id = %s"

    cursor.execute(query, (survey_id,))

    questions = cursor.fetchall()

    # obtener opciones
    for question in questions:

        query = "SELECT * FROM options WHERE question_id = %s"

        cursor.execute(query, (question['id'],))

        options = cursor.fetchall()

        question['options'] = options

    if request.method == 'POST':

        for question in questions:

            option_id = request.form.get(f"question_{question['id']}")

            query = """
            INSERT INTO answers
            (user_id, survey_id, question_id, option_id)
            VALUES (%s, %s, %s, %s)
            """

            values = (
                session['user_id'],
                survey_id,
                question['id'],
                option_id
            )

            cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/surveys?message=answered')
        

    return render_template(
        'survey.html',
        questions=questions
    )

# RESULTS

@app.route('/results/<int:survey_id>')
def results(survey_id):

    if 'user_id' not in session:
        return redirect('/login')
    if session['role'] != 'admin':
        return "Acceso denegado"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # obtener preguntas
    query = "SELECT * FROM questions WHERE survey_id = %s"

    cursor.execute(query, (survey_id,))

    questions = cursor.fetchall()

    # obtener opciones y conteo
    for question in questions:

        query = """
        SELECT options.id,
               options.option_text,
               COUNT(answers.option_id) as total_votes
        FROM options
        LEFT JOIN answers
        ON options.id = answers.option_id
        WHERE options.question_id = %s
        GROUP BY options.id
        """

        cursor.execute(query, (question['id'],))

        options = cursor.fetchall()

        question['options'] = options

    cursor.close()
    conn.close()

    return render_template(
        'results.html',
        questions=questions
    )

# LOGOUT 

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)