from ntpath import join
from flask import Flask, render_template, request, abort, send_from_directory, session, redirect, url_for
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import distinct, desc, create_engine, exc
import json
from sqlalchemy import func, insert, text
import time
from prometheus_client import Counter, generate_latest, REGISTRY



while 1:
    try:
        e = create_engine('postgresql+psycopg2://post_user:qwerty1234@postgres-db:5432/postgres').connect()
        e.execute(text('select 1'))
    except exc.OperationalError:
        print('Waiting for database...')
        time.sleep(1)
    else:
        break

print('Connected!')

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
app.register_blueprint(auth_bp)
init_login_manager(app)

from models import User, Role, Plan, Goals

http_requests_total = Counter('http_requests_total', 'Total number of HTTP requests')
function_calls_total = Counter('function_calls_total', 'Total number of function calls with labels', labelnames=['endpoint'])

def increment_function_calls(endpoint):
    function_calls_total.labels(endpoint=endpoint).inc()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count', methods=['GET', 'POST'])
def count():
    students = User.query.all()
    counted = {
        'Вечерняя':0,
        'Дневная':0,
        'Заочная':0
    }
    stud_forms = set()
    http_requests_total.inc()
    for i in students:
        counted[i.form] += 1
        stud_forms.add(i.form)
    if request.method == "GET":
        return render_template('count.html',stud_forms=stud_forms)
    elif request.method == "POST":
        return render_template('count.html',stud_forms=stud_forms,selected_name_list=request.form['stud_form_id'],counted=counted[request.form['stud_form_id']])
    
@app.route('/disciplines', methods=['GET', 'POST'])
def disciplines():
    discs = Plan.query.with_entities(Plan.disc_name).group_by(Plan.disc_name).all()
    if request.method == 'GET':
        return render_template('disc.html',discs=discs)
    if request.method == 'POST':
        check = False
        for i in Plan.query.with_entities(Plan.disc_name).group_by(Plan.disc_name).all():
            if request.form['disc_id'][2:-3] in i:
                check = True
                break
        if check:
            hours = Plan.query.with_entities(func.sum(Plan.amount)).where(Plan.disc_name == request.form['disc_id'][2:-3]).first()
            exams_flag = Plan.query.with_entities(Plan.exam).where(Plan.disc_name == request.form['disc_id'][2:-3]).where(Plan.exam == True).all()
            goals_flag = Plan.query.with_entities(Plan.exam).where(Plan.disc_name == request.form['disc_id'][2:-3]).where(Plan.exam == False).all()
            return render_template('disc.html', discs=discs, selected_name_list=request.form['disc_id'],hours=hours,exams=exams_flag,goals=goals_flag)
        else:
            return render_template('disc.html',discs=discs)

@app.route('/students', methods=['GET','POST'])
def students():
    increment_function_calls('students')
    students = User.query.order_by(User.last_name).all()
    if request.method == 'GET':
        return render_template('students.html',students=students)
    elif request.method == 'POST':
        form = request.form
        id = form.get('id')
        update = form.get('update')
        year = form.get('year')
        name = form.get('name')
        format = form.get('format')
        group = form.get('group')
        if len(name.split()) < 3:
            for i in range(3-len(name.split())):
                name += ' Nul'
        m_name,f_name,l_name = name.split()
        if update == '0':
            user = User.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.commit()
            result = User(login=f_name,password_hash=1,last_name=l_name,first_name=f_name,middle_name=m_name, form=format,date=year,group=group,role_id=2)
            db.session.add(result)
            db.session.commit()
        elif update == '1':
            result = User(login=f_name,password_hash=1,last_name=l_name,first_name=f_name,middle_name=m_name, form=format,date=year,group=group,role_id=2)
            db.session.add(result)
            db.session.commit()
        else:
            pass
    return redirect(url_for('students'))

@app.route('/discs', methods = ['GET', 'POST'])
def disc():
    discs = Plan.query.order_by(Plan.id)
    if request.method == 'GET':
        return render_template('discs.html', disciplines=discs)
    elif request.method == 'POST':
        form = request.form
        id = form.get('id')
        update = form.get('update')
        spec_name = form.get('spec_name')
        disc_name = form.get('disc_name')
        sem = form.get('sem')
        amount = form.get('amount')
        exam = bool(form.get('exam'))
        if update == '0':
            discipline = Plan.query.filter_by(id=id).first()
            db.session.delete(discipline)
            db.session.commit()
            result = Plan(spec_name=spec_name,disc_name=disc_name,sem=sem,amount=amount,exam=exam)
            db.session.add(result)
            db.session.commit()
        elif update == '1':
            result = Plan(spec_name=spec_name,disc_name=disc_name,sem=sem,amount=amount,exam=exam)
            db.session.add(result)
            db.session.commit()
        else:
            pass
    return redirect(url_for('disc'))

@app.route('/goals', methods = ['GET', 'POST'])
def goals():
    dbgoals = Goals.query.order_by(Goals.id)
    goal = []
    for dbgoal in dbgoals:
        student = User.query.filter_by(id = dbgoal.student).first()
        student_name = student.last_name + ' ' + student.first_name + ' ' + student.middle_name
        goal.append({
            'id': dbgoal.id,
            'sem': dbgoal.sem,
            'student': student_name,
            'disc_name': Plan.query.filter_by(id = dbgoal.disc_name).first().disc_name,
            'goal': dbgoal.goal
        })
    if request.method == 'GET':
        return render_template('goals.html', goals=goal)
    elif request.method == 'POST':
        form = request.form
        id = form.get('id')
        update = form.get('update')
        sem = form.get('sem')
        student = form.get('student')
        student_last_name, student_first_name, student_middle_name = student.split()
        disc_name = form.get('disc_name')
        discipline = Plan.query.filter_by(disc_name=disc_name).first()
        goal = form.get('goal')
        user = User.query.filter_by(last_name = student_last_name, first_name = student_first_name, middle_name = student_middle_name).first()
        if update == '1':
            print(user.id)
            print(discipline.id)
            result = Goals(sem=sem,student=user.id,disc_name=discipline.id,goal=goal)
            db.session.add(result)
            db.session.commit()
        elif update == '0':
            delete_goal = Goals.query.filter_by(id=id).first()
            db.session.delete(delete_goal)
            db.session.commit()
            result = Goals(sem=sem,student=user.id,disc_name=discipline.id,goal=goal)
            db.session.add(result)
            db.session.commit()
    return redirect(url_for('goals'))

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}
