from flask import Flask, render_template,request,redirect,url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os 
from twilio.rest import Client
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///randevu.db'
db = SQLAlchemy(app)
app.secret_key = 'gizli123'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
hours = ["8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00"]
Services=["Haircut","Manicure","Pedicure","Facial","Massage"]
today=datetime.today().date()

load_dotenv()
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
def sms_gonder(telefon, mesaj):
    client = Client(TWILIO_SID,TWILIO_TOKEN)
    client.messages.create(
        body=mesaj,
        from_=TWILIO_NUMBER,
        to=telefon
    )
class Randevu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(50), nullable=False)
    surname= db.Column(db.String(50), nullable=False)
    meet= db.Column(db.Date, nullable=False)
    service= db.Column(db.String(50), nullable=False)
    hours=db.Column(db.String(10), nullable=False)
    phone=db.Column(db.String(10), nullable=False)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route("/")
def index():
    # Geçmiş tarihleri engellemek için bugünün tarihini HTML'e metin olarak gönderiyoruz
    today_str = datetime.today().strftime('%Y-%m-%d')
    return render_template('index.html', services=Services, hours=hours, today=today_str)

@app.route('/randevu', methods=['POST'])
def randevu():
    today=datetime.today().date()
    name=request.form.get('name',"")
    surname=request.form.get("surname","")
    service=request.form.get("service","")
    meet=request.form.get("meet","")
    meet = datetime.strptime(meet, '%Y-%m-%d').date()
    hours=request.form.get("hours","")
    phone=request.form.get("phone","")
    phone = "+90" + phone.lstrip("0")
    if today>meet:
        flash("please enter a valid date! ","danger")
        return redirect(url_for("index"))
    else:

        yeni=Randevu(name=name, surname=surname, meet=meet, service=service,hours=hours,phone=phone )
        db.session.add(yeni)
        db.session.commit()
        sms_gonder(phone,f"randevunuz oluşturuldu:{meet} saat {hours} - {service} ")
    return render_template('randevu.html', name=name, surname=surname, meet=meet, service=service, hours=hours, phone=phone)

@app.route('/randevular')
@login_required
def randevular():
    randevular = Randevu.query.all()
    
    # --- DASHBOARD İSTATİSTİKLERİ ---
    today_date = datetime.today().date()
    bugunku_randevular = sum(1 for r in randevular if r.meet == today_date)
    
    hizmet_sayilari = {}
    for r in randevular:
        hizmet_sayilari[r.service] = hizmet_sayilari.get(r.service, 0) + 1
        
    en_populer = max(hizmet_sayilari, key=hizmet_sayilari.get) if hizmet_sayilari else "-"
    toplam = len(randevular)
    
    return render_template('randevular.html', randevular=randevular, bugunku=bugunku_randevular, populer=en_populer, toplam=toplam)
@app.route("/randevusil", methods=['POST'])
def randevusil():
    id = request.form.get("id")
    randevu = Randevu.query.get(id)
    if randevu:
        db.session.delete(randevu)
        db.session.commit()
        flash("Silindi!","success")
    else:
        pass
    return redirect(url_for("randevular"))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                flash("login successful!","success")
                return  redirect(url_for('randevular'))
            else:
                flash("password incorrect","danger")
        else:
            flash("username or password is incorrect","danger")
    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("you have been logout","success")
    return redirect(url_for("index"))
@app.route("/dolu_saatler")
def dolu_saatler():
    dolu_saatler=[]
    date=request.args.get("meet")
    randevular=Randevu.query.filter_by(meet=date)
    for randevu in randevular:
        dolu_saatler.append(randevu.hours)
    return jsonify(dolu_saatler)




    
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
