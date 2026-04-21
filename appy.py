from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'



db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# =========================
# MODELOS
# =========================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Deuda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    saldo = db.Column(db.Float)
    interes = db.Column(db.Float)
    fecha_pago = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =========================
# RUTAS
# =========================

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    deudas = Deuda.query.filter_by(user_id=current_user.id).all()
    total = sum(d.saldo for d in deudas)
    return render_template('dashboard.html', deudas=deudas, total=total)

@app.route('/nueva_deuda', methods=['GET','POST'])
@login_required
def nueva_deuda():
    if request.method == 'POST':
        deuda = Deuda(
            nombre=request.form['nombre'],
            saldo=float(request.form['saldo']),
            interes=float(request.form['interes']),
            fecha_pago=request.form['fecha_pago'],
            user_id=current_user.id
        )
        db.session.add(deuda)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('nueva_deuda.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# =========================
# MOTOR DE OPTIMIZACIÓN
# =========================

@app.route('/optimizacion')
@login_required
def optimizacion():
    deudas = Deuda.query.filter_by(user_id=current_user.id).all()
    ordenadas = sorted(deudas, key=lambda x: x.interes, reverse=True)
    return {"orden_pago": [d.nombre for d in ordenadas]}

# =========================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



    
