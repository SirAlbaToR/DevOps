from ntpath import join
from flask import Flask, render_template, request, abort, send_from_directory, session
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import distinct, desc
import json
from sqlalchemy import func



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
    for i in students:
        counted[i.form] += 1
        stud_forms.add(i.form)
    if request.method == "GET":
        return render_template('count.html',stud_forms=stud_forms)
    elif request.method == "POST":
        return render_template('count.html',stud_forms=stud_forms,selected_name_list=request.form['stud_form_id'],counted=counted[request.form['stud_form_id']])
    
@app.route('/disciplines', methods=['GET', 'POST'])
def disciplines():
    print(Plan.query.with_entities(Plan.disc_name).group_by(Plan.disc_name).all())
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