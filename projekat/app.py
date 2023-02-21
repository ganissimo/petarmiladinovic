from flask import Flask, render_template, url_for, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
import mysql
import mysql.connector 
import mariadb
import ast


konekcija = mysql.connector.connect(
passwd="",   #ovde upisujemo lozinku
user="root",     #ovde ide ime
database="vlasnici", #ovde stavljamo ime base 
port=   3306 , #stavljamo portna kome radi mysql server 
auth_plugin='mysql_native_password') 

#pravimo kursor na kome cemo postavljati upite i za pokretanje povezivanja sa bazom
kursor=konekcija.cursor(dictionary=True)

#deklaracija aplikacije
app=Flask(__name__)
app.secret_key="tajni_kljuc_aplikacije"


def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False

def rola():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).pop("rola")


#logika aplikacije

@app.route('/vlasnici', methods=['GET'])   #za prikazivanje tabele (npr za admina)          vlasnici.html
def render_vlasnici():

    if ulogovan():
        upit ="select * from vlasnik"   #sintaksa iz mysql-a
        kursor.execute(upit)         #koristimo kursor za izvsravanje upita
        vlasnik = kursor.fetchall()
        if rola() == 'admin':
            rolaProvera = True
            print(rola())
        else:
            rolaProvera = False
            print(rola())    #ovde smesatmo podatke iza baze u promenjljivu vlasnik
        return render_template('admin.html', vlasnik = vlasnik, rolaProvera=rolaProvera) #prilikom rederovanja saljemo podatke u vlasnik promenjljivu
    else:
        return redirect(url_for("render_login"))

@app.route('/register',methods=['GET'])
def render_register():
    return render_template('register.html')

@app.route('/home',methods=['GET']) #ovde prikazujemo login na pocetku                          login.html
def render_home():
    if ulogovan():
        return render_template('index.html')
    else:
        return redirect(url_for("render_login"))

@app.route('/register',methods=["GET","POST"])   #dodajemo korisnika novog              dodajkorisnika.html
def korisnik_novi():
        if request.method=="GET":
            return render_template('register.html')

        if request.method=="POST":          #uzimamo podatke iz forme npr forma[ime]
            forma=request.form    
            #heshovana_lozinka= generate_password_hash(forma["pass"])
            vrednosti=(
            forma["ime"],
            forma["email"],
            forma["lozinka"],
            forma["rola"],
            forma["ime_psa"],
            )

            upit =  """ insert into
                        vlasnik(ime,email,lozinka,rola,ime_psa)
                        values(%s,%s,%s,%s,%s)
            """
            kursor.execute(upit, vrednosti)
            konekcija.commit()

            return redirect(url_for("render_vlasnici"))

@app.route('/',methods=['GET','POST'])
def render_login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        forma = request.form
        upit = "SELECT * FROM vlasnik WHERE email = %s"
        vrednost = (forma["email"],)
        kursor.execute(upit,vrednost)
        korisnik = kursor.fetchone()
        #return render_template('vlasnici.html')
        if korisnik != None:
            #if check_password_hash(korisnik["lozinka"],forma ["lozinka1"]):    #ne mogu oba ifa
            if korisnik["lozinka"] == forma["lozinka1"]:
                session["ulogovani_korisnik"] =str(korisnik)
                return redirect(url_for("render_home"))
            else:
                return render_template("login.html")
        else:
            return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("ulogovani_korisnik",None)
    return redirect(url_for("render_login"))

@app.route('/vlasnik_izmena/<id>',methods=['GET','POST'])
def vlasnik_izmena(id):
    if request.method == 'GET':
        upit = "SELECT * FROM vlasnik WHERE id=%s"
        vrednost = (id, )
        kursor.execute(upit, vrednost)
        vlasnik = kursor.fetchone()

        return render_template("izmena.html",vlasnik=vlasnik)

    if request.method == "POST":
        upit = """ update vlasnik set
                    ime = %s, email = %s, lozinka = %s, rola = %s, ime_psa = %s
                    where id = %s
        """
        forma = request.form
        vrednosti =(
            forma["ime"],
            forma["email"],
            forma["lozinka"],
            forma["rola"],
            forma["ime_psa"],
            id
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('render_vlasnici'))

@app.route('/brisanje<id>', methods=['GET','POST'])
def brisanje(id):
    upit = "DELETE FROM vlasnik WHERE id = %s"  #AND id_produkti = %s LIMIT 1"
    vrednost = (id, )
    kursor.execute(upit, vrednost)
    konekcija.commit()

    return redirect(url_for("render_vlasnici"))

#pokretanje aplikacije 
app.run(debug=True)