from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify, send_from_directory, abort
from models import Uzytkownik, Requests, Kierunki, Grupy, Requests_Kierunki, Przedmioty, Zajecia, Oceny, Egzaminy, Konto_Bankowe, Payment, Email, Egzaminy_Wyniki
import json
import os
import calendar
import bcrypt
from datetime import datetime, timedelta


DATA_FOLDER = 'data'
KIERUNKI_FILE = 'data/kierunki.json'
GRUPY_FILE = 'data/grupy.json'
OCENY_FILE = 'data/oceny.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


geekoczelnia_bp = Blueprint('geekoczelnia', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------------------------------------- GŁOWNA STRONA ----------------------------------------------------------

@geekoczelnia_bp.route('/', methods=['GET', 'POST'])
def hello():
    selected_view = "login"

    if request.method == "POST":
                selected_view = request.form.get("view", "login")

    return render_template('hello.html', selected_view=selected_view)


# ---------------------------------------------------------- KONTAKT ----------------------------------------------------------

@geekoczelnia_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')



# ---------------------------------------------------------- LOGOWANIE ----------------------------------------------------------

@geekoczelnia_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        haslo = request.form['haslo']

        haslo_hash = bcrypt.hashpw(haslo.encode('utf-8'), bcrypt.gensalt())
        user = next((user for user in Uzytkownik.get_all_users() if user.email == email), None)
        
        if user: 
            stored_hash = user.haslo.encode('utf-8')
            if bcrypt.checkpw(haslo.encode('utf-8'), stored_hash):
                session['user_id'] = user.id
                session['email'] = user.email
                session['rola'] = user.rola
                session['imie'] = user.imie
                session['nazwisko'] = user.nazwisko
                session['haslo'] = user.haslo
                session['grupa'] = user.grupa
                if user.rola == "Administrator":
                    return redirect(url_for('geekoczelnia.admin'))
                elif user.rola == "Student":
                    return redirect(url_for('geekoczelnia.dashboard_student')) 
                elif user.rola == "Wykładowca":
                    return redirect(url_for('geekoczelnia.dashboard_wykladowca'))
            else:
                flash("Niepoprawne hasło", "error")
                return render_template('hello.html', selected_view='login')
        else:
            flash("Niepoprawny email", "error")
            return render_template('hello.html', selected_view='login')

    return render_template('hello.html',selected_view='login')


# ---------------------------------------------------------- WYLOGOWANIE ----------------------------------------------------------

@geekoczelnia_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()  
    return redirect(url_for('geekoczelnia.hello'))  


# ---------------------------------------------------------- REJESTRACJA STUDENTA ----------------------------------------------------------

@geekoczelnia_bp.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        email = request.form['email']
        haslo = request.form['haslo']

        haslo_hash = bcrypt.hashpw(haslo.encode('utf-8'), bcrypt.gensalt())
        haslo_hash_utf8 = haslo_hash.decode('utf-8', 'ignore')

        if Uzytkownik.email_exists(email):
            flash("Email jest już zajęty, wybierz inny.", "error")
            return render_template('hello.html', selected_view = "rejestracja_student")

        new_user = Uzytkownik(
            id=Uzytkownik.get_all_users()[-1].id + 1 if Uzytkownik.get_all_users() else 1,
            imie=imie,
            nazwisko=nazwisko,
            email=email,
            rola="Student",
            haslo=haslo_hash_utf8,
            kierunek="",
            grupa="",
            semestr=""
        )

        test_user = Uzytkownik(
            id=Uzytkownik.get_all_users()[-1].id + 1 if Uzytkownik.get_all_users() else 1,
            imie=imie,
            nazwisko=nazwisko,
            email=email,
            rola="Student",
            haslo=haslo,
            kierunek="",
            grupa="",
            semestr=""
        )
        new_bank_account = Konto_Bankowe(
            id = Konto_Bankowe.get_all_bank_accounts()[-1].id + 1 if Konto_Bankowe.get_all_bank_accounts() else 1,
            student_id=Uzytkownik.get_all_users()[-1].id + 1 if Uzytkownik.get_all_users() else 1,
            saldo=0
        )

        with open("data/test.json", "a") as file:
            json.dump(haslo,file,indent=4)




        Uzytkownik.save_user(new_user)
        Konto_Bankowe.save_bank_account(new_bank_account)


        recipient_email = email
        sender = "Geekoczelnia@online"
        title = "Rejestracja na GEEKoczelni"
        message = f"""
        Witaj {imie} {nazwisko},

        Dziękujemy za zarejestrowanie się na naszą uczelnie!
        Zaloguj się na swoje konto żeby zarejestrować się na wybrany przez siebie kierunek.
        
        Pozdrawiamy,
        Zespół GEEKoczelni
        """
        Email.send_email(recipient_email, title, message, sender)




        flash("Zarejestrowałeś się jako student", "success")
        return redirect(url_for('geekoczelnia.hello'))

    return render_template('register_student.html')

# ---------------------------------------------------------- REJESTRACJA WYKŁADOWCY ----------------------------------------------------------


@geekoczelnia_bp.route('/register_wykladowca', methods=['GET', 'POST'])
def register_wykladowca():
    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        email = request.form['email']
        haslo = request.form['haslo']

        haslo_hash = bcrypt.hashpw(haslo.encode('utf-8'), bcrypt.gensalt())
        haslo_hash_utf8 = haslo_hash.decode('utf-8', 'ignore')

        if Uzytkownik.email_exists(email):
            flash("Email jest już zajęty, wybierz inny.", "warning")
            return render_template('hello.html', selected_view = 'rejestracja_wykladowca')
        new_request = Requests(
            id=Requests.get_all_requests()[-1].id + 1 if Requests.get_all_requests() else 1,
            imie=imie,
            nazwisko=nazwisko,
            email=email,
            rola="Wykładowca",
            haslo=haslo_hash_utf8
        )
        Requests.save_request(new_request)


        recipient_email = email
        sender = "Geekoczelnia@online"
        title = "Rejestracja na GEEKoczelni"
        message = f"""
        Witaj {imie} {nazwisko},

        Dziękujemy za zarejestrowanie się na naszą uczelnie jako wykładowca!
        Prosimy o cierpliwość — Twoje zgłoszenie zostanie rozpatrzone przez administrację, a po jego zatwierdzeniu zostaniesz poinformowany drogą mailową.
        
        Pozdrawiamy,
        Zespół GEEKoczelni
        """
        Email.send_email(recipient_email, title, message, sender)



        
        flash("Zarejestrowałeś się jako wykładowca, poczekaj na akceptacje administratora", "info")
        return redirect(url_for('geekoczelnia.hello'))

    return render_template('hello.html')



# ---------------------------------------------------------- DASHBOARD STUDENTA ----------------------------------------------------------
@geekoczelnia_bp.route('/dashboard_student', methods=["GET", "POST"])
def dashboard_student():
    uzytkownicy_data = Uzytkownik.get_all_users()
    kierunki_data = Kierunki.get_all_kierunki()
    grupy_data = Grupy.get_all_grupy()
    przedmioty_data = Przedmioty.get_all_przedmioty()
    zajecia_data = Zajecia.get_all_zajecia()
    oceny_data = Oceny.get_all_oceny()
    egzaminy_data = Egzaminy.get_all_egzaminy()
    egzaminy_wyniki_data = Egzaminy_Wyniki.get_all_egzaminy_wyniki()

    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login')) 
    
    if session['rola'] == "Student":
        

        user_id = session['user_id']
        session_user = next((u for u in Uzytkownik.get_all_users() if u.id == user_id), None)
        wykladowcy = Uzytkownik.get_wykladowcy()
        oceny_student = Oceny.get_oceny_student(user_id)
        selected_view = request.args.get('view', 'home')
        wiadomosci = request.form.get("wiadomosci", "odebrane")
        wiadomosci_id_odebranej = ""
        wiadomosci_id_wyslanej = ""
        kierunki_data = Kierunki.get_all_kierunki()




        messages = []
        with open("data/maile.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
            messages = [msg for msg in all_messages if msg['recipient'] == session_user.email]

        sent_messages = []
        with open("data/maile.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
            sent_messages = [msg for msg in all_messages if msg['sender'] == session_user.email]  



        oceny_przedmioty = Oceny.get_oceny_przedmioty(oceny_student)

        kierunek = next((req for req in kierunki_data if req.id == session_user.kierunek), None)

        grupa = next((req for req in grupy_data if req.id == session_user.grupa), None)


        saldo = Konto_Bankowe.get_student_balance(user_id)
        konto_bankowe_id = Konto_Bankowe.get_student_bank_account_id(user_id)
        transakcje = Payment.get_payments_history(konto_bankowe_id)


        target_file = f'/uploads/{user_id}.jpg' if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{user_id}.jpg')) else '/uploads/default.jpg'



        
        year = int(request.form.get('year', datetime.now().year))
        month = int(request.form.get('month', datetime.now().month))

        month_translation = {
                        "January": "Styczeń",
                        "February": "Luty",
                        "March": "Marzec",
                        "April": "Kwiecień",
                        "May": "Maj",
                        "June": "Czerwiec",
                        "July": "Lipiec",
                        "August": "Sierpień",
                        "September": "Wrzesień",
                        "October": "Październik",
                        "November": "Listopad",
                        "December": "Grudzień"
                    }

        if request.method == "POST":
                selected_view = request.form.get("view")
                action = request.form.get('action')
                form_id = request.form.get('form_id')
                if action == 'next':
                    selected_view = "calendar"
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
                elif action == 'prev':
                    selected_view = "calendar"
                    if month == 1:
                        month = 12
                        year -= 1
                    else:
                        selected_view = "calendar"
                        month -= 1
                elif form_id == "wiadomosci":
                    wiadomosci = request.form.get("wiadomosci")
                    selected_view = "wiadomosci"
                elif form_id == "odebrane":
                    wiadomosci = "odebrane"
                    wiadomosci_id_odebranej = request.form.get("wiadomosci_id_odebranej")
                    selected_view = "wiadomosci"
                elif form_id == "wyslane":
                    wiadomosci = "wyslane"
                    wiadomosci_id_wyslanej = request.form.get("wiadomosci_id_wyslanej")
                    selected_view = "wiadomosci"
                

        
        zajecia_sorted = Zajecia.sorted_zajecia()
        egzaminy_sorted = Egzaminy.sorted_egzaminy()

        month_calendar = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        month_name_pl = month_translation.get(month_name, month_name)


        return render_template('dashboard_student.html',
                                user=session_user,
                                kierunek=kierunek,
                                grupa=grupa,
                                zajecia = zajecia_data,
                                selected_view=selected_view,
                                users = uzytkownicy_data, 
                                oceny = oceny_data,
                                egzaminy=egzaminy_data,
                                saldo = saldo,
                                grupy=grupy_data,
                                konto_bankowe_id = Konto_Bankowe.get_student_bank_account_id(user_id),
                                payments = transakcje,
                                zdjecie = target_file,
                                year=year,
                                month=month,
                                month_name=month_name_pl,
                                month_calendar=month_calendar,
                                zajecia_sorted=zajecia_sorted,
                                oceny1 = oceny_student,
                                przedmioty_oceny = oceny_przedmioty,
                                przedmioty = przedmioty_data,
                                wykladowcy = wykladowcy,
                                messages=messages,
                                kierunki=kierunki_data,
                                egzaminy_wyniki = egzaminy_wyniki_data,
                                egzaminy_sorted=egzaminy_sorted,
                                wiadomosci=wiadomosci,
                                sent_messages=sent_messages,
                                wiadomosci_id_odebranej=wiadomosci_id_odebranej,
                                wiadomosci_id_wyslanej=wiadomosci_id_wyslanej
                                )
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))
    

# ---------------------------------------------------------- REJESTRACJA NA KIERUNEK  ----------------------------------------------------------

@geekoczelnia_bp.route('/rejestracja_na_kierunek', methods=['GET', 'POST'])
def register_for_kierunek():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Student":
        kierunki_data = Kierunki.get_all_kierunki()
        if request.method == 'POST':
            id = session['user_id']
            imie = session['imie']
            nazwisko = session['nazwisko']
            email = session['email']
            haslo = session['haslo']
            kierunek = request.form['kierunek']
            view = request.form.get('view', 'home')

            new_request = Requests_Kierunki(
                id=Requests_Kierunki.get_all_requests_kierunki()[-1].id + 1 if Requests_Kierunki.get_all_requests_kierunki() else 1,
                imie=imie,
                nazwisko=nazwisko,
                email=email,
                rola="Student",
                haslo=haslo,
                kierunek=kierunek,
                grupa="",
                semestr=""
            )
            Requests_Kierunki.save_request_kierunki(new_request)
            flash(f"Wysłałeś prośbę o rejestrację na kierunek", "success")
            return redirect(url_for('geekoczelnia.dashboard_student'))


        return render_template('rejestracja_na_kierunek.html',
                               kierunki = kierunki_data,
                               view=view,
                               )
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))


# ---------------------------------------------------------- PŁATNOŚĆ  ----------------------------------------------------------

@geekoczelnia_bp.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Student":
        payments_data = Payment.get_all_payments()
        if request.method == 'POST':
            id = Payment.get_all_payments()[-1].id + 1 if Payment.get_all_payments() else 1
            konto_id = Konto_Bankowe.get_student_bank_account_id(session['user_id'])
            title = request.form['title']
            ammount = request.form['ammount']
            view = request.form.get('view', 'payment')

            date = datetime.now()
            date = date.strftime("%d/%m/%Y %H:%M:%S")

            new_payment = Payment(
                id = id,
                date = date,
                konto_id=konto_id,
                title=title,
                ammount=ammount
            )
            Payment.save_payment(new_payment)
            Konto_Bankowe.add_balance(konto_id, ammount)

            flash(f"Pomyślnie zasilono konto na {new_payment.ammount}zł.", "success")
            return redirect(url_for('geekoczelnia.dashboard_student', view=view))

        return render_template('dashboard_student.html', payments=payments_data)
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))



# ---------------------------------------------------------- DASHBOARD WYKŁADOWCA ----------------------------------------------------------

@geekoczelnia_bp.route('/dashboard_wykladowca', methods=["GET", "POST"])
def dashboard_wykladowca():
    uzytkownicy_data = Uzytkownik.get_all_users()
    kierunki_data = Kierunki.get_all_kierunki()
    grupy_data = Grupy.get_all_grupy()
    przedmioty_data = Przedmioty.get_all_przedmioty()
    zajecia_data = Zajecia.get_all_zajecia()
    oceny_data = Oceny.get_all_oceny()
    egzaminy_data = Egzaminy.get_all_egzaminy()
    egzaminy_wyniki_data = Egzaminy_Wyniki.get_all_egzaminy_wyniki()
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))  
    
    if session['rola'] == "Wykładowca":
        
        user_id = session['user_id']
        session_user = next((u for u in Uzytkownik.get_all_users() if u.id == user_id), None)

        przedmioty = Przedmioty.get_przedmioty_wykladowca(user_id)
        grupa_id = request.args.get('grupa_id')
        groups = request.form.get("groups", None)
        selected_view = request.args.get('view', 'home') 
        target_file = f'/uploads/{user_id}.jpg' if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{user_id}.jpg')) else '/uploads/default.jpg'
        wiadomosci = request.form.get("wiadomosci", "odebrane")
        year = int(request.form.get('year', datetime.now().year))
        month = int(request.form.get('month', datetime.now().month))
        wiadomosci_id_odebranej = ""
        wiadomosci_id_wyslanej = ""


        messages = []
        with open("data/maile.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
            messages = [msg for msg in all_messages if msg['recipient'] == session_user.email]

        sent_messages = []
        with open("data/maile.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
            sent_messages = [msg for msg in all_messages if msg['sender'] == session_user.email]  

        month_translation = {
                        "January": "Styczeń",
                        "February": "Luty",
                        "March": "Marzec",
                        "April": "Kwiecień",
                        "May": "Maj",
                        "June": "Czerwiec",
                        "July": "Lipiec",
                        "August": "Sierpień",
                        "September": "Wrzesień",
                        "October": "Październik",
                        "November": "Listopad",
                        "December": "Grudzień"
                    }
        if request.method == "POST":
                selected_view = request.form.get("view", selected_view)
                action = request.form.get('action')
                form_id = request.form.get('form_id')
                if action == 'next':
                    selected_view = "calendar"
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
                elif action == 'prev':
                    selected_view = "calendar"
                    if month == 1:
                        month = 12
                        year -= 1
                    else:
                        selected_view = "calendar"
                        month -= 1
                elif form_id == "grupy":
                    groups = request.form.get("groups")
                    selected_view = "grupy"
                    grupa_id = request.form.get("grupa_id")
                elif form_id == "wiadomosci":
                    wiadomosci = request.form.get("wiadomosci")
                    selected_view = "wiadomosci"
                elif form_id == "odebrane":
                    wiadomosci = "odebrane"
                    wiadomosci_id_odebranej = request.form.get("wiadomosci_id_odebranej")
                    wiadomosci_id_wyslanej = ""
                    selected_view = "wiadomosci"
                elif form_id == "wyslane":
                    wiadomosci = "wyslane"
                    wiadomosci_id_wyslanej = request.form.get("wiadomosci_id_wyslanej")
                    wiadomosci_id_odebranej = ""
                    selected_view = "wiadomosci"





        zajecia_sorted = Zajecia.sorted_zajecia()
        egzaminy_sorted = Egzaminy.sorted_egzaminy()

        month_calendar = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        month_name_pl = month_translation.get(month_name, month_name)

        return render_template('dashboard_wykladowca.html',
                            user=session_user,
                            zajecia = zajecia_data,
                            przedmioty = przedmioty_data,
                            users = uzytkownicy_data,
                            grupy = grupy_data,
                            kierunki = kierunki_data,
                            oceny = oceny_data,
                            egzaminy = egzaminy_data,
                            zdjecie = target_file,
                            przedmioty1 = przedmioty,
                            year=year,
                            month=month,
                            month_name=month_name_pl,
                            month_calendar=month_calendar,
                            selected_view=selected_view,
                            zajecia_sorted=zajecia_sorted,
                            egzaminy_wyniki=egzaminy_wyniki_data,
                            egzaminy_sorted=egzaminy_sorted,
                            groups=groups,
                            grupa_id=grupa_id,
                            wiadomosci=wiadomosci,
                            messages=messages,
                            wiadomosci_id_odebranej=wiadomosci_id_odebranej,
                            wiadomosci_id_wyslanej=wiadomosci_id_wyslanej,
                            sent_messages=sent_messages
                            )
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))



# ---------------------------------------------------------- DODAWANIE NOWEJ OCENY  ----------------------------------------------------------


@geekoczelnia_bp.route('/add_ocena', methods=['POST'])
def add_ocena():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Wykładowca":
        oceny_data = Oceny.get_all_oceny()
        
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            przedmiot_id = request.form.get('przedmiot_id')
            wykladowca_id = request.form.get('wykladowca_id')
            ocena = request.form.get('ocena')
            view = request.form.get('view', 'grupy')
            grupa_id = request.form.get('grupa_id')

            existing_ocena = next(
                (o for o in oceny_data if o.student_id == student_id and o.przedmiot_id == przedmiot_id),
                None
            )

            if existing_ocena   :
                existing_ocena.ocena = ocena
                Oceny.update_ocena(existing_ocena)
                flash(f"Pomyślnie zaktualizowano ocenę.", "success")
                
            else:
                new_ocena = Oceny(
                    id=oceny_data[-1].id + 1 if oceny_data else 1,
                    student_id=student_id,
                    przedmiot_id=przedmiot_id,
                    wykladowca_id=wykladowca_id,
                    ocena=ocena
                )
                Oceny.save_ocena(new_ocena)
                flash(f"Pomyślnie dodano ocene.", "success")
            

            return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view, grupa_id=grupa_id ))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))
    

# ---------------------------------------------------------- DODAWANIE NOWEGO EGZAMINU  ----------------------------------------------------------
    
@geekoczelnia_bp.route('/add_egzamin', methods=['POST'])
def add_egzamin():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Wykładowca":
        egzaminy_data = Egzaminy.get_all_egzaminy()
        if request.method == 'POST':
            data_egzaminu = request.form.get('data_egzaminu')
            przedmiot_id = request.form.get('przedmiot_id')
            wykladowca_id = request.form.get('wykladowca_id')
            grupa_id = request.form.get('grupa_id')

            view = request.form.get('view', 'grupy')
            existing_egzamin = next(
                (e for e in egzaminy_data if e.przedmiot_id == przedmiot_id and e.grupa_id == grupa_id),
                None
            )

            if existing_egzamin:
                existing_egzamin.data = data_egzaminu
                Egzaminy.update_egzamin(existing_egzamin)
                flash(f"Pomyślnie zaktualizowano date egzaminu.", "success")
            else:
                new_egzamin = Egzaminy(
                    id=egzaminy_data[-1].id + 1 if egzaminy_data else 1,
                    data=data_egzaminu,
                    przedmiot_id=przedmiot_id,
                    wykladowca_id=wykladowca_id,
                    grupa_id=grupa_id
                )
                Egzaminy.save_egzamin(new_egzamin)
                flash(f"Pomyślnie dodano nowy termin egzaminu", "success")


            return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view, grupa_id=grupa_id))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))
    


# ----------------------------------------------------------DASHBOARD ADMIN ----------------------------------------------------------

@geekoczelnia_bp.route('/admin', methods=["GET", "POST"])
def admin():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))  
    if session['rola'] == "Administrator":
        
        users = Uzytkownik.get_all_users()

        selected_view = request.args.get('view', 'home') 

        user_id = session['user_id']
        session_user = next((u for u in Uzytkownik.get_all_users() if u.id == user_id), None)

        target_file = f'/uploads/{user_id}.jpg' if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{user_id}.jpg')) else '/uploads/default.jpg'

        requests_data = Requests.get_all_requests()

        requests_kiernki_data = Requests_Kierunki.get_all_requests_kierunki()

        kierunki_data = Kierunki.get_all_kierunki()

        grupy = Grupy.get_all_grupy()

        przedmioty_data = Przedmioty.get_all_przedmioty()

        zajecia_data = Zajecia.get_all_zajecia()

        egzaminy_data = Egzaminy.get_all_egzaminy()

        konta_bankowe = Konto_Bankowe.get_all_bank_accounts()

        wszyscy_uzytkownicy = Uzytkownik.count_students()

        uzytkownicy_na_kierunku = Uzytkownik.count_students_by_kierunki()

        avg_ocena = Oceny.get_srednia_ocen()

        avg_ocena_kierunek = Oceny.get_srednia_dla_kierunku()

        avg_egzamin = Egzaminy.get_sredni_wynik()

        avg_egzamin_kierunek = Egzaminy.get_srednia_wynikow_dla_kierunku()

        wiadomosci = request.form.get("wiadomosci", "odebrane")
        wiadomosci_id_odebranej = ""
        wiadomosci_id_wyslanej = ""

        messages = []
        with open("data/maile.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
            messages = [msg for msg in all_messages if msg['recipient'] == session_user.email]

        sent_messages = []
        with open("data/maile.json", "r", encoding="utf-8") as file:
            all_messages = json.load(file)
            sent_messages = [msg for msg in all_messages if msg['sender'] == session_user.email] 


        month_translation = {
                        "January": "Styczeń",
                        "February": "Luty",
                        "March": "Marzec",
                        "April": "Kwiecień",
                        "May": "Maj",
                        "June": "Czerwiec",
                        "July": "Lipiec",
                        "August": "Sierpień",
                        "September": "Wrzesień",
                        "October": "Październik",
                        "November": "Listopad",
                        "December": "Grudzień"
                    }

        year = int(request.form.get('year', datetime.now().year))
        month = int(request.form.get('month', datetime.now().month))
        if request.method == "POST":
                form_id = request.form.get('form_id')
                selected_view = request.form.get("view")
                action = request.form.get('action')
                if action == 'next':
                    selected_view = "calendar"
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
                elif action == 'prev':
                    selected_view = "calendar"
                    if month == 1:
                        month = 12
                        year -= 1
                    else:
                        selected_view = "calendar"
                        month -= 1
                elif form_id == "wiadomosci":
                    wiadomosci = request.form.get("wiadomosci")
                    selected_view = "wiadomosci"
                elif form_id == "odebrane":
                    wiadomosci = "odebrane"
                    wiadomosci_id_odebranej = request.form.get("wiadomosci_id_odebranej")
                    selected_view = "wiadomosci"
                elif form_id == "wyslane":
                    wiadomosci = "wyslane"
                    wiadomosci_id_wyslanej = request.form.get("wiadomosci_id_wyslanej")
                    selected_view = "wiadomosci"
        
        zajecia_sorted = Zajecia.sorted_zajecia()
        egzaminy_sorted = Egzaminy.sorted_egzaminy()

        month_calendar = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        month_name_pl = month_translation.get(month_name, month_name)


        return render_template(
            'admin.html',
            email=session['email'],
            rola=session['rola'],
            imie=session['imie'],
            nazwisko=session['nazwisko'],
            users=users,
            requests=requests_data,
            kierunki=kierunki_data,
            grupy=grupy,
            user=session_user,
            zdjecie = target_file,
            selected_view = selected_view,
            requests_kierunki=requests_kiernki_data,
            przedmioty=przedmioty_data,
            zajecia = zajecia_data,
            konta_bankowe = konta_bankowe,
            year=year,
            month=month,
            month_name=month_name_pl,
            month_calendar=month_calendar,
            zajecia_sorted=zajecia_sorted,
            egzaminy_sorted=egzaminy_sorted,
            egzaminy_data=egzaminy_data,
            wszyscy_uzytkownicy=wszyscy_uzytkownicy,
            uzytkownicy_na_kierunku=uzytkownicy_na_kierunku,
            avg_ocena=avg_ocena,
            avg_ocena_kierunek=avg_ocena_kierunek,
            avg_egzamin=avg_egzamin,
            avg_egzamin_kierunek=avg_egzamin_kierunek,
            messages=messages,
            wiadomosci=wiadomosci,
            wiadomosci_id_odebranej=wiadomosci_id_odebranej,
            wiadomosci_id_wyslanej=wiadomosci_id_wyslanej,
            sent_messages=sent_messages

            
        )
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))
    
# ---------------------------------------------------------- USUWANIE UŻYTKOWNIKA ----------------------------------------------------------


@geekoczelnia_bp.route('/uzytkownicy/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    flash(f"Pomyślnie usunięto użytkownika wraz z jego danymi.", "success")
    user = next((u for u in Uzytkownik.get_all_users() if u.id == user_id), None)
    if user.rola == "Student":
        Payment.delete_payments(user_id)
        Konto_Bankowe.delete_account(user_id)
        Oceny.delete_oceny(user_id)
        Egzaminy_Wyniki.delete_egzaminy(user_id)
        Uzytkownik.delete_user(user_id)

        filename = f"{user_id}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            os.remove(filepath)
        except:
            return redirect(url_for('geekoczelnia.admin'))
        
    else:
        
        Uzytkownik.delete_user(user_id)
        filename = f"{user_id}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            os.remove(filepath)
        except:
            return redirect(url_for('geekoczelnia.admin'))
        
        return redirect(url_for('geekoczelnia.admin'))



# ---------------------------------------------------------- ZAAKCEPTOWANIE NOWEGO WYKŁADOWCY ----------------------------------------------------------

@geekoczelnia_bp.route('/requests/accept/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    flash(f"Pomyślnie zaakceptowano nowego wykładowcę.", "success")
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        requests_data = Requests.get_all_requests()
        request_to_accept = next((req for req in requests_data if req.id == request_id), None)
        if not request_to_accept:
            return "Nie znaleziono żądania rejestracji", 404

        request_dict = request_to_accept.to_dict()
        new_id = Uzytkownik.get_all_users()[-1].id + 1 if Uzytkownik.get_all_users() else 1
        new_user_data = {**request_dict, "id": int(new_id)}
        new_user = Uzytkownik.from_json(new_user_data)

        Uzytkownik.save_user(new_user)
        Requests.delete_request(request_id)

        recipient_email = new_user.email
        sender = "Geekoczelnia@online"
        title = "Twoje konto zostało zaakceptowane"
        message = f"""
        Witaj {new_user.imie} {new_user.nazwisko},

        Twoje konto na platformie zostało zaakceptowane. Możesz się teraz zalogować.
        
        Pozdrawiamy,
        Zespół Geekoczelni
        """
        Email.send_email(recipient_email, title, message, sender)

        return redirect(url_for('geekoczelnia.admin'))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))

# ---------------------------------------------------------- ODRZUCENIE NOWEGO WYKŁADOCWY ----------------------------------------------------------

@geekoczelnia_bp.route('/requests/reject/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    view = "requests_wykladowcy"
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        if not request_id:
            return "Błąd: Brak parametru request_id", 400

        try:
            request_id = int(request_id)
        except ValueError:
            return "Błąd: Nieprawidłowe ID", 400

        requests_data = Requests.get_all_requests()

        request_to_reject = next((req for req in requests_data if req.id == request_id), None)
        if not request_to_reject:
            return "Nie znaleziono żądania rejestracji", 404

        Requests.delete_request(request_id)
        flash(f"Odrzucono rejestrację wykładowcy.", "success")
        return redirect(url_for('geekoczelnia.admin', view=view))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))

# ---------------------------------------------------------- NOWY KIERUNEK ----------------------------------------------------------


@geekoczelnia_bp.route('/add_kierunek', methods=['GET', 'POST'])
def add_kierunek():
    
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        if request.method == 'POST':
            nazwa = request.form.get('nazwa').title()
            typ = request.form.get('typ')
            opis = request.form.get('opis')
            view = request.form.get('view', 'kierunki')

            new_course = Kierunki(
                id=Kierunki.get_all_kierunki()[-1].id + 1 if Kierunki.get_all_kierunki() else 1,
                nazwa = nazwa,
                typ = typ,
                opis=opis
            )
            Kierunki.save_kierunek(new_course)


        flash(f"Kierunek '{nazwa}' został pomyślnie zarejestrowany!", "success")
        return redirect(url_for('geekoczelnia.admin', view=view))
    
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))

# ---------------------------------------------------------- NOWA GRUPA ----------------------------------------------------------


@geekoczelnia_bp.route('/add_grupa', methods=['GET', 'POST'])
def add_grup():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        if request.method == 'POST':
            nazwa = request.form['nazwa']
            semestr = request.form['semestr']
            kierunek = request.form['kierunek']
            view = request.form.get('view', 'grupy')
            przedmioty = request.form.getlist('przedmioty') 



            grupy = Grupy.get_all_grupy()

            new_grupa = Grupy(
                id=grupy[-1].id + 1 if grupy else 1,
                nazwa = nazwa,
                semestr = semestr,
                kierunek=kierunek,
                przedmioty=przedmioty
            )

            Grupy.save_grupa(new_grupa)


        flash(f"Grupa '{new_grupa.nazwa}' została pomyślnie zarejestrowana!", "success")
        return redirect(url_for('geekoczelnia.admin', view=view))

    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))


# ---------------------------------------------------------- ODRZUCENIE REJESTRACJI NA KIERUNEK  ----------------------------------------------------------

@geekoczelnia_bp.route('/admin/reject_request_kierunek/', methods=['POST'])
def reject_request_kierunek():
    view = "requests_kierunki"
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        request_id = request.form.get('request_id')

        if not request_id:
            return "Błąd: Brak parametru request_id", 400

        try:
            request_id = int(request_id)
        except ValueError:
            return "Błąd: Nieprawidłowe ID", 400

        requests_kiernki_data = Requests_Kierunki.get_all_requests_kierunki()

        request_to_reject = next((req for req in requests_kiernki_data if req.id == request_id), None)
        if not request_to_reject:
            return "Nie znaleziono żądania rejestracji", 404

        Requests_Kierunki.reject_request(request_id)
        flash(f"Odrzucono rejestrację na kierunek.", "success")
        return redirect(url_for('geekoczelnia.admin', view=view))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))


# ---------------------------------------------------------- PRZYJECIE REJESTRACJI NA KIERUNEK ----------------------------------------------------------

@geekoczelnia_bp.route('/admin/accept_request_kierunek/', methods=['POST'])
def accept_request_kierunek_wybrany():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        user_email = request.form.get('user_email')
        request_kierunek = request.form.get('kierunek')
        request_kierunek_id = request.form.get('request_id')
        grupa = request.form.get('grupa')

        kierunki_data = Kierunki.get_all_kierunki()
        grupy = Grupy.get_all_grupy()
        users = Uzytkownik.get_all_users()
        requests_data = Requests_Kierunki.get_all_requests_kierunki()

        try:
            request_kierunek = int(request_kierunek)
            grupa = int(grupa)
            request_kierunek_id = int(request_kierunek_id)
        except ValueError:
            return "Błąd: Nieprawidłowe ID", 400

        kierunek_updated = next((req for req in kierunki_data if req.id == request_kierunek), None)
        grupa_updated = next((req for req in grupy if req.id == grupa), None)

        user = next((req for req in users if req.email == user_email), None)

        if not user or not kierunek_updated or not grupa_updated:
            return "Błąd: Brak użytkownika, kierunku lub grupy", 400

        user.kierunek = kierunek_updated.id
        user.grupa = grupa_updated.id
        user.semestr = "1"

        Uzytkownik.add_to_group(user.id, user.kierunek, user.grupa, user.semestr)

        Requests_Kierunki.delete_request(request_kierunek_id)
        sender = "Geekoczelnia@online"
        title = "Zostałeś zaakceptowany na kierunek studiów"
        message = f"""
        Witaj {user.imie} {user.nazwisko},

        Zostałeś przyjęty na kierunek {kierunek_updated.nazwa}.
        Twoja grupa: {grupa_updated.nazwa}
        Semestr: {user.semestr}.
            
        Życzymy powodzenia w nauce!

        Pozdrawiamy,
        Zespół Geekoczelni
        """
        Email.send_email(user.email, title, message, sender)

        flash(f"Użytkownik '{user.imie} {user.nazwisko}' o ID {user.id} został zaakceptowany do grupy {grupa_updated.nazwa} i powiadomiony e-mailem!", "success")
        return redirect(url_for('geekoczelnia.admin'))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))
    


# ---------------------------------------------------------- REJESTRACJA NOWEGO PRZEDMIOTU  ----------------------------------------------------------

@geekoczelnia_bp.route('/add_przedmiot', methods=['GET', 'POST'])
def add_przedmiot():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":

        if request.method == 'POST':
            nazwa = request.form['nazwa']
            wykladowca_id = request.form['wykladowca']
            ects = request.form['ects']
            opis = request.form['opis']
            egzamin = request.form['egzamin']
            view = request.form.get('view', 'przedmioty')

            przedmioty = Przedmioty.get_all_przedmioty()

            new_przedmiot = Przedmioty(
                id=przedmioty[-1].id + 1 if przedmioty else 1,
                nazwa=nazwa,
                wykladowca_id=wykladowca_id,
                ects=int(ects),
                opis=opis,
                egzamin=egzamin
            )

            Przedmioty.save_przedmiot(new_przedmiot)

        flash(f"Przedmiot '{new_przedmiot.nazwa}' został pomyślnie dodany!", "success")
        return redirect(url_for('geekoczelnia.admin', view=view))

    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))


# ---------------------------------------------------------- DODANIE NOWYCH ZAJĘĆ  ----------------------------------------------------------


@geekoczelnia_bp.route('/add_zajecie', methods=['GET', 'POST'])
def add_zajecie():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        zajecia_data = Zajecia.get_all_zajecia()

        if request.method == 'POST':
            przedmiot_id = request.form['przedmiot_id']
            grupa_id = request.form['grupa_id']
            sala = request.form['sala']
            rodzaj = request.form['rodzaj']
            rozpoczecie = request.form['rozpoczecie']
            czestotliwosc = request.form["czestotliwosc"]
            ilosc = int(request.form["ilosc"])
            rozpoczecie_data = datetime.fromisoformat(rozpoczecie)
            zakonczenie_data = rozpoczecie_data + timedelta(hours=1, minutes=30)
            zakonczenie = zakonczenie_data.isoformat()
            view = request.form.get('view', 'zajecia')


            rozpoczecie_dt = datetime.fromisoformat(rozpoczecie)
            zakonczenie_dt = datetime.fromisoformat(zakonczenie)


            grupa = Grupy.get_grupa_by_id(grupa_id)
            if grupa:
                grupa_nazwa = grupa.nazwa  # Nazwa grupy
            else:
                grupa_nazwa = "Nieznana grupa"  # Jeśli grupa nie została znaleziona


        if ilosc > 0:
            for i in range(ilosc):
                delta = timedelta(weeks=i) if czestotliwosc == 'tydzien' else timedelta(weeks=2*i)



                nowe_rozpoczecie = rozpoczecie_dt + delta
                nowe_zakonczenie = zakonczenie_dt + delta

                
                new_zajecie = Zajecia(
                    id=zajecia_data[-1].id + 1 + i if zajecia_data else 1 + i,
                    przedmiot_id=przedmiot_id,
                    grupa_id=grupa_id,
                    sala=sala,
                    rodzaj=rodzaj,
                    rozpoczecie=nowe_rozpoczecie.isoformat(),
                    zakonczenie=nowe_zakonczenie.isoformat()
                )

                Zajecia.save_zajecie(new_zajecie)

            flash(f"Zajęcia dla grupy '{grupa_nazwa}' o ID {new_zajecie.grupa_id} został pomyślnie zarejestrowany!", "success")
            return redirect(url_for('geekoczelnia.admin', view=view))

    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))




# ---------------------------------------------------------- USUWANIE ZAJEC ----------------------------------------------------------
@geekoczelnia_bp.route('/zajecia/delete/<int:zajecie_id>', methods=['POST'])
def delete_zajecie(zajecie_id):
    flash(f"Usunięto zajęcie.", "success")
    view = request.form.get('view', None)
    Zajecia.delete_zajecie(zajecie_id)
    if session['rola'] == "Administrator":
        return redirect(url_for('geekoczelnia.admin', view=view))
    else:
        return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
    
# ---------------------------------------------------------- USUWANIE EGZAMINU ----------------------------------------------------------


@geekoczelnia_bp.route('/egzaminy/delete/<int:egzamin_id>', methods=['POST'])
def delete_egzamin(egzamin_id):
    flash(f"Usunięto egzamin.", "success")
    view = request.form.get('view', None)
    month = request.form.get('month', None)
    Egzaminy.delete_egzamin(egzamin_id)
    if session['rola'] == "Administrator":
        return redirect(url_for('geekoczelnia.admin', view=view, month=month))
    else:
        return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view, month=month))
    

# ---------------------------------------------------------- DODAWANIE WYNIKU EGZAMINU  ----------------------------------------------------------

@geekoczelnia_bp.route('/add_egzamin_wynik', methods=['POST'])
def add_egzamin_wynik():
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Wykładowca":
        egzaminy_wyniki_data = Egzaminy_Wyniki.get_all_egzaminy_wyniki()
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            egzamin_id = request.form.get('egzamin_id')
            wynik = request.form.get('wynik')

            # Odczytanie 'view' i 'groups' z formularza POST
            view = request.form.get('view', 'grupy')  # 'view' domyślnie 'grupy'
            grupa_id = request.form.get('grupa_id')

            existing_egzamin = next(
                (e for e in egzaminy_wyniki_data if e.student_id == student_id and e.egzamin_id == egzamin_id),
                None
            )

            if existing_egzamin:
                existing_egzamin.wynik = wynik
                Egzaminy_Wyniki.update_egzamin_wynik(existing_egzamin)
            else:
                new_egzamin = Egzaminy_Wyniki(
                    id=egzaminy_wyniki_data[-1].id + 1 if egzaminy_wyniki_data else 1,
                    student_id=student_id,
                    egzamin_id=egzamin_id,
                    wynik=wynik
                )
                Egzaminy_Wyniki.save_egzamin_wynik(new_egzamin)
            flash(f"Pomyślnie dodano wynik z egzaminu.", "success")
            return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view, grupa_id=grupa_id))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))
    
# ---------------------------------------------------------- POBIERANIE PŁATNOŚĆI  ----------------------------------------------------------

@geekoczelnia_bp.route('/uzytkownicy/get_payment/<int:user_id>', methods=['POST'])
def get_payment(user_id):
    view="students"
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        if request.method == 'POST':
            id = Payment.get_all_payments()[-1].id + 1 if Payment.get_all_payments() else 1
            konto_id = Konto_Bankowe.get_student_bank_account_id(user_id)
            title = request.form['title']
            ammount = int(request.form['ammount'])
            
            date = datetime.now()
            date = date.strftime("%d/%m/%Y %H:%M:%S")



            new_payment = Payment(
                id=id,
                date=date,
                konto_id=konto_id,
                title=title,
                ammount=-ammount
            )
            Payment.save_payment(new_payment)
            Konto_Bankowe.take_balance(konto_id, ammount)

            saldo_po_transakcji = Konto_Bankowe.get_student_balance(user_id)
            student_email = Konto_Bankowe.get_student_email(user_id)

            sender = "admin@geekoczelnia.online"
            title = "Pobranie środków z konta"
            message = f"""
            Z Twojego konta została pobrana kwota: {ammount}.

            Tytuł transakcji: {title}.
            Twoje aktualne saldo wynosi: {saldo_po_transakcji}.

            Pozdrawiamy,
            Zespół Geekoczelni
            """
            Email.send_email(student_email, title, message, sender)

            flash(f"Pomyślnie pobrano z konta użytkownika kwotę {ammount}zł.", "success")
            return redirect(url_for('geekoczelnia.admin', view=view))

        return redirect(url_for('geekoczelnia.admin'))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))

# ---------------------------------------------------------- BULK PAYMENT ----------------------------------------------------------

@geekoczelnia_bp.route('/uzytkownicy/bulk_payment', methods=['POST'])
def bulk_payment():
    view="students"
    if 'user_id' not in session:
        return redirect(url_for('geekoczelnia.login'))
    if session['rola'] == "Administrator":
        konta_bankowe = Konto_Bankowe.get_all_bank_accounts()
        title = request.form['title']
        ammount = request.form['ammount']
        date = datetime.now()
        date = date.strftime("%d/%m/%Y %H:%M:%S")
        for konto in konta_bankowe:
            id = Payment.get_all_payments()[-1].id + 1 if Payment.get_all_payments() else 1

            
            ammount = int(ammount)

            new_payment = Payment(
                id = id,
                date=date, 
                konto_id=konto.id,
                title=title,
                ammount= ammount * -1
            )
            Payment.save_payment(new_payment)
            Konto_Bankowe.take_balance(konto.id, ammount)
            saldo_po_transakcji = Konto_Bankowe.get_student_balance(konto.id)
            sender = "Geekoczelnia@online"
            student_email = Konto_Bankowe.get_student_email(konto.student_id)
            title = "Pobranie środków z konta"
            message = f"""
            Z Twojego konta została pobrana kwota: {ammount}.

            Tytuł transakcji: {title}.
            Twoje aktualne saldo wynosi: {saldo_po_transakcji}.

            Pozdrawiamy,
            Zespół Geekoczelni
            """
            Email.send_email(student_email, title, message, sender)
        flash(f"Pomyślnie pobrano czesne o wartości {new_payment.ammount}zł.", "success")
        return redirect(url_for('geekoczelnia.admin', view=view))
    else:
        flash("Nie masz dostępu do tego miejsca", "error")
        return redirect(url_for('geekoczelnia.login'))


    
# ---------------------------------------------------------- ZMIANA HASŁA ----------------------------------------------------------

@geekoczelnia_bp.route('/change_password', methods=['POST'])
def change_password():
        user_id = session['user_id']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        user = next((user for user in Uzytkownik.get_all_users() if user.id == user_id), None)
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        view = request.form.get('view', 'dane')
        stored_hash = user.haslo.encode('utf-8')
        if bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
            haslo_hash_utf8 = new_password_hash.decode('utf-8', 'ignore')

            Uzytkownik.change_password(user_id, haslo_hash_utf8)

            

            if session['rola'] == "Student":
                flash('Zmieniono hasło', "success")
                return redirect(url_for('geekoczelnia.dashboard_student', view=view))
            elif session['rola'] == "Wykładowca":
                flash(f'Zmieniono hasło', "success")
                return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
            else:
                flash(f'Zmieniono hasło', "success")
                return redirect(url_for('geekoczelnia.admin', view=view))
        else: 
            if session['rola'] == "Student":
                flash('Podaj poprawne hasło', "warning")
                return redirect(url_for('geekoczelnia.dashboard_student', view=view))
            elif session['rola'] == "Wykładowca":
                flash(f'Podaj poprawne hasło', "warning")
                return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
            else:
                flash(f'Podaj poprawne hasło', "warning")
                return redirect(url_for('geekoczelnia.admin', view=view))
        
    

# ---------------------------------------------------------- UPLOAD PLIKU  ----------------------------------------------------------
@geekoczelnia_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------------------------------------------------- UPLOAD PICTURE ----------------------------------------------------------

@geekoczelnia_bp.route('/upload_picture', methods=['POST'])
def upload_picture():
    user_id = session['user_id']
    view = request.form.get('view', 'dane')

    if 'file' not in request.files:
        flash('Nie wybrano pliku')
        return redirect(url_for('geekoczelnia.dashboard_student', view=view))

    file = request.files['file']

    if file.filename == '':
        if session['rola'] == "Student":
            flash('Brak wybranego pliku', "error")
            return redirect(url_for('geekoczelnia.dashboard_student', view=view))
        elif session['rola'] == "Wykładowca": 
            flash('Brak wybranego pliku', "error")
            return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
        else:
            flash('Brak wybranego pliku', "error")
            return redirect(url_for('geekoczelnia.admin', view=view))


    if file and allowed_file(file.filename):
        try:
            extension = file.filename.rsplit('.', 1)[1].lower()
            new_filename = f"{user_id}.{extension}"
            filepath = os.path.join(UPLOAD_FOLDER, new_filename)
            file.save(filepath)
            
            if session['rola'] == "Student":
                flash(f'Zapisano zdjęcie!', "success")
                return redirect(url_for('geekoczelnia.dashboard_student', view=view))
            elif session['rola'] == "Wykładowca":
                flash(f'Zapisano zdjęcie!', "success")
                return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
            else:
                flash(f'Zapisano zdjęcie!', "success")
                return redirect(url_for('geekoczelnia.admin', view=view))
        except Exception as e:
            if session['rola'] == "Student":
                flash(f'Niepoprawny format, proszę o przesłanie pliku jpg', "warning")
                return redirect(url_for('geekoczelnia.dashboard_student', view=view))
            elif session['rola'] == "Student":
                flash(f'Niepoprawny format, proszę o przesłanie pliku jpg', "warning")
                return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
            else:
                flash(f'Niepoprawny format, proszę o przesłanie pliku jpg', "warning")
                return redirect(url_for('geekoczelnia.admin', view=view))
                

  

    if session['rola'] == "Student":
        flash('Niepoprawny format, proszę o przesłanie pliku jpg', "warning")
        return redirect(url_for('geekoczelnia.dashboard_student', view=view))
    elif session['rola'] == "Wykładowca":
        flash(f'Niepoprawny format, proszę o przesłanie pliku jpg', "warning")
        return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
    else:
        flash(f'Niepoprawny format, proszę o przesłanie pliku jpg', "warning")
        return redirect(url_for('geekoczelnia.admin', view=view))


# ---------------------------------------------------------- WIADOMOŚCI WEWNĘTRZNE----------------------------------------------------------
@geekoczelnia_bp.route('/send_message', methods=['POST'])
def send_message():
    recipent = request.form['recipent']
    sender = request.form['sender']
    title = request.form['title']
    message = request.form['message']
    view = 'wiadomosci'
    user = next((user for user in Uzytkownik.get_all_users() if user.email == sender), None)
    Email.save_email_to_file(recipent, title, message, sender)
    if user.rola == "Student":
        return redirect(url_for('geekoczelnia.dashboard_student', view=view))
    elif user.rola == "Wykładowca":
        return redirect(url_for('geekoczelnia.dashboard_wykladowca', view=view))
    else:
        return redirect(url_for('geekoczelnia.admin', view=view))

@geekoczelnia_bp.route('/send_bulk_message', methods=['POST'])
def send_bulk_message():
    recipents = request.form['recipents']
    sender = request.form['sender']
    title = request.form['title']
    message = request.form['message']
    view = 'wiadomosci'
    user = next((user for user in Uzytkownik.get_all_users() if user.email == sender), None)
    if recipents == "Student":
        users = Uzytkownik.get_students()
        for user in users:
            Email.save_email_to_file(user['email'], title, message, sender)
    elif recipents == "Wykładowca":
        users = Uzytkownik.get_wykladowcy()
        for user in users:
            Email.save_email_to_file(user['email'], title, message, sender)
        

    
    return redirect(url_for('geekoczelnia.admin', view=view))





# ---------------------------------------------------------- ZAJECIA JAVA SCRIPT ----------------------------------------------------------

@geekoczelnia_bp.route('/data/<filename>')
def get_data(filename):
    rola = session.get('rola', None)
    if rola == "Administrator":
        return send_from_directory(DATA_FOLDER, filename)
    else:
        abort(403)


