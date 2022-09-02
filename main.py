from sqlite3 import Cursor
from flask import Flask,render_template, request, session, redirect, url_for, flash
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import mysql.connector
from sqlalchemy import BigInteger

#My DB connection
local_server = True
app = Flask(__name__)
app.secret_key="yash1th"

#This is for unique user access
login_manager=LoginManager(app)
login_manager.login_view="login"

@login_manager.user_loader    
def load_student(student_sid):
    return Student.query.get(int(student_sid))

#DB connection
#app.config["SQLALCHEMY_DATABASE_URI"]="mysql://username:password@localhost/database_table_name" (no pwd for our server)
app.config["SQLALCHEMY_DATABASE_URI"]="mysql://root:@localhost/e-learning ms"
db=SQLAlchemy(app)

connection = mysql.connector.connect(host='localhost',
                                         database='e-learning ms',
                                         user='root',
                                         password='')




#creating DB models
class Student(UserMixin,db.Model):
    def get_id(self):
           return (self.sid)
    sid=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    dob=db.Column(db.DateTime)
    city=db.Column(db.String(20))
    phone=db.Column(db.BigInteger)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Tutor(UserMixin,db.Model):
    def get_id(self):
           return (self.tid)
    tid=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    phone=db.Column(db.BigInteger)
    email=db.Column(db.String(50),unique=True)
    cid=db.Column(db.String(20))

class Enrollment(UserMixin,db.Model):
    def get_id(self):
           return (self.eid)
    eid=db.Column(db.Integer,primary_key=True)
    enrollmentdate=db.Column(db.Date)
    sid=db.Column(db.Integer)
    cid=db.Column(db.String(20))

class Course(UserMixin,db.Model):
    def get_id(self):
           return (str(self.cid))
    cid=db.Column(db.String(20),primary_key=True)
    name=db.Column(db.String(20))
    duration=db.Column(db.String(20))
    description=db.Column(db.String(1000))

class Assessment(UserMixin,db.Model):
    def get_id(self):
           return (self.sid)
    sid=db.Column(db.Integer,primary_key=True)
    cid=db.Column(db.String(20),primary_key=True)
    asgmt1=db.Column(db.Integer)
    asgmt2=db.Column(db.Integer)
    asgmt2=db.Column(db.Integer)

class Trig(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sid=db.Column(db.Integer)
    cid=db.Column(db.String(20))
    action=db.Column(db.String(20))
    date=db.Column(db.Date)

@app.route('/index')
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/student",methods=["POST","GET"])
@login_required
def student():
    coursedata=[]
    sid=int(current_user.sid)
    
    #stored procedure
    connection = mysql.connector.connect(host='localhost',
                                         database='e-learning ms',
                                         user='root',
                                         password='')
    cursor = connection.cursor()
    results=cursor.callproc('Remarks', [sid, ])
    print (results)
    print("Printing assessment details")
    for result in cursor.stored_results():
        res=(result.fetchall())
    print(res)

    enrollmentdata=Enrollment.query.filter_by(sid=sid).all()
    for enrollment in enrollmentdata:
        course=Course.query.filter_by(cid=enrollment.cid).first()
        coursedata.append(course)
    print(coursedata)
    if request.method=="POST":
        cid=request.form.get("cid")
        sid=int(current_user.sid)
        db.engine.execute(f"DELETE FROM `enrollment` WHERE `enrollment`.`sid`={sid} AND `enrollment`.`cid`='{cid}'")
        connection = mysql.connector.connect(host='localhost',
                                         database='e-learning ms',
                                         user='root',
                                         password='')
        cursor = connection.cursor()
        results=cursor.callproc('Remarks', [sid, ])
        print (results)
        print("Printing assessment details")
        for result in cursor.stored_results():
            res=(result.fetchall())
        print(res)
        flash("Unenrolled Successfully","success")
        return redirect(url_for("student",res=res))
    return render_template("student.html",name=current_user.name,coursedata=coursedata,res=res)

@app.route("/studentsignup",methods=["POST","GET"])
def studentsignup():
    if request.method=="POST":
        name=request.form.get("name")
        dob=request.form.get("dob")
        city=request.form.get("city")
        phone=request.form.get("phone")
        email=request.form.get("email")
        password=request.form.get("password")
        encpswd=generate_password_hash(password)
        student=Student.query.filter_by(email=email).first()
        if student:
            flash("Email already exists","warning")
            return render_template("/studentsignup.html")
        
        new_student=db.engine.execute(f" INSERT INTO `student` (`name`,`dob`,`city`,`phone`, `email`, `password`) VALUES ('{name}','{dob}','{city}','{phone}','{email}','{encpswd}');" )
        flash("SignUp Successful", "success")
        return render_template("studentlogin.html")
        

    return render_template("studentsignup.html")

@app.route("/studentlogin",methods=["POST","GET"])
def studentlogin():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        student=Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password,password):
            login_user(student)
            flash("Login Successful", "success")
            return redirect(url_for("student"))
        else:
            flash("Invalid credentials","danger")
            return render_template("studentlogin.html")
        
    return render_template("studentlogin.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("Logout Successful","warning")
    return redirect(url_for("home"))
    
@app.route("/tutor",methods=["POST","GET"])
def tutor():
    trigdata=db.engine.execute(f"SELECT * FROM `trig`")
    studentdata=[]
    if request.method=="POST":
        cid=request.form.get("cid")
        enrollmentdata=Enrollment.query.filter_by(cid=cid)
        for enrollment in enrollmentdata:
            student=Student.query.filter_by(sid=enrollment.sid).first()
            studentdata.append(student)
        print(studentdata)
        return render_template("tutor.html",enrollmentdata=enrollmentdata,studentdata=studentdata,trigdata=trigdata)
    return render_template("tutor.html",trigdata=trigdata)

@app.route("/tutorlogin",methods=["POST","GET"])
def tutorlogin():
    if request.method=="POST":
        email=request.form.get("email")
        phone=request.form.get("phone")
        tutor=Tutor.query.filter_by(email=email).first()
        #print(tutor.email)
        print(tutor)
        if tutor and int(tutor.phone)==int(phone):
            print("Successful")
            login_user(tutor)
            print("Login Successful", "success")
            flash("Login Successful", "success")
            return redirect(url_for("tutor"))
        else:
            print("Unsuccessful")
            flash("Invalid credentials","danger")
            return render_template("tutorlogin.html")

    return render_template("tutorlogin.html")

@app.route("/marksupdate",methods=["POST","GET"])
def marksupdate():
    if request.method=="POST":
        sid=request.form.get("sid")
        cid=request.form.get("cid")
        asgmt1=request.form.get("asgmt1")
        asgmt2=request.form.get("asgmt2")
        asgmt3=request.form.get("asgmt3")
        student=Student.query.filter_by(sid=sid).first()
        enrollment=Enrollment.query.filter_by(sid=sid)
        if student:
            for stud in enrollment:
                if cid==stud.cid:
                    db.engine.execute(f"INSERT INTO `assessment` (`sid`,`cid`,`asgmt1`,`asgmt2`,`asgmt3`) VALUES ('{sid}','{cid}','{asgmt1}','{asgmt2}','{asgmt3}') ON DUPLICATE KEY UPDATE `asgmt1`='{asgmt1}',`asgmt2`='{asgmt2}',`asgmt3`='{asgmt3}';")
                    flash("Marks Updated Successfully","success")
                    break
            else:
                    flash("Student hasn't enrolled into the selected course","warning")
        else:
            flash("Wrong Student ID","danger")
    return render_template("marksupdate.html")

@app.route("/courses",methods=["POST","GET"])
def courses():
    return render_template("courses.html")

@app.route("/enrollment",methods=["POST","GET"])
def enrollment():
    if request.method=="POST":
        sid=int(current_user.sid)
        cid=request.form.get("cid")
        enrollmentdate=request.form.get("enrollmentdate")
        enrollment=Enrollment.query.filter_by(sid=sid)
        #course=Course.query.filter_by(cid=cid).first()
        status=True
        for stud in enrollment:
            if cid==stud.cid:
                status=False
                flash('Already enrolled to this course',"warning")
                break
        if status:
            db.engine.execute(f"INSERT INTO `enrollment` (`enrollmentdate`,`sid`,`cid`) VALUES ('{enrollmentdate}','{sid}','{cid}');")
            flash("Enrolled Successfully","success")

    return render_template("enrollment.html")

@app.route("/profileupdate",methods=["POST","GET"])
@login_required
def profileupdate():
    if request.method=="POST":
        sid=int(current_user.sid)
        name=request.form.get("name")
        phone=request.form.get("phone")
        email=request.form.get("email")
        password=request.form.get("password")
        student=Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password,password):
            db.engine.execute(f"UPDATE `student` SET `name`='{name}',`phone`='{phone}',`email`='{email}' WHERE `sid`={sid};")
            flash("Profile Updated Successfully","success")
            return redirect(url_for("student"))
    return render_template("profileupdate.html")

@app.route("/assessmentmarks")
@login_required
def assessmentmarks():
     return render_template("assessmentmarks.html")

app.run(debug=True)