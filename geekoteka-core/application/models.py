import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

MAILS_FILE = 'data/maile.json'
os.makedirs('data', exist_ok=True)


# ---------------------------------------------------------- UZYTKOWNIK ----------------------------------------------------------

class Uzytkownik:
    def __init__(self, id, imie, nazwisko, email, rola, haslo, kierunek, grupa, semestr):
        self.id = id
        self.imie = imie.capitalize()
        self.nazwisko = nazwisko.capitalize()
        self.email = email
        self.rola = rola
        self.haslo = haslo
        self.kierunek = kierunek
        self.grupa = grupa
        self.semestr = semestr

    def to_dict(self):
        return {
            "id": self.id,
            "imie": self.imie,
            "nazwisko": self.nazwisko,
            "email": self.email,
            "rola": self.rola,
            "haslo": self.haslo,
            "kierunek": self.kierunek,
            "grupa": self.grupa,
            "semestr": self.semestr,
        }

    @staticmethod
    def from_json(data):
        return Uzytkownik(
            id=data["id"],
            imie=data["imie"],
            nazwisko=data["nazwisko"],
            email=data["email"],
            rola=data["rola"],
            haslo=data["haslo"],
            kierunek=data.get("kierunek", ""),
            grupa=data.get("grupa", ""),
            semestr=data.get("semestr", ""),
        )

    @staticmethod
    def get_all_users():
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
            return [Uzytkownik.from_json(user) for user in users_data]
        
    def get_wykladowcy():
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
        
        wykladowcy = [w for w in users_data if w.get("rola") == "Wykładowca"]

        return wykladowcy
    @staticmethod
    def get_students():
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
        
        students = [w for w in users_data if w.get("rola") == "Student"]

        return students
    

    @staticmethod
    def save_user(new_user):
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)

        users_data.append(new_user.to_dict())

        with open("data/uzytkownicy.json", "w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def delete_user(user_id):
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
        updated_users = [user for user in users_data if user['id'] != user_id]
        with open("data/uzytkownicy.json", "w", encoding="utf-8") as file:
            json.dump(updated_users, file, ensure_ascii=False, indent=4)

    @staticmethod
    def email_exists(email):
        users = Uzytkownik.get_all_users()
        return any(user.email == email for user in users)
    

    @staticmethod
    def add_to_group(edited_user, kierunek, grupa, semestr):
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
        user = next((item for item in users_data if item["id"] == edited_user), None)

        user["kierunek"] = kierunek
        user["grupa"] = grupa
        user["semestr"] = semestr
        with open("data/uzytkownicy.json", "w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=4)
        
    @staticmethod
    def change_password(user_id, new_password):
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)

        user = next((item for item in users_data if item["id"] == user_id), None)

        user["haslo"] = new_password

        with open("data/uzytkownicy.json", "w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def count_students():
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)

        students = [user for user in users_data if user.get("rola") == "Student"]
        return len(students)


    @staticmethod
    def count_students_by_kierunki():
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)

        kierunki = set(user.get("kierunek") for user in users_data if user.get("kierunek"))

        kierunek_counts = {
            kierunek: len([user for user in users_data if user.get("kierunek") == kierunek])
            for kierunek in kierunki
        }

        return kierunek_counts

# ---------------------------------------------------------- EMAILE ----------------------------------------------------------

class Email:
    @staticmethod
    def send_email(recipient, title, message, sender):
        from config import EMAIL_ADDRESS, EMAIL_PASSWORD

        try:
            msg = MIMEMultipart()
            msg['From'] = f"Geekoczelnia <{EMAIL_ADDRESS}>"
            msg['To'] = recipient
            msg['Subject'] = title
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)

            Email.save_email_to_file(recipient, title, message, sender)

            print(f"E-mail wysłany do {recipient}")
            return True
        except Exception as e:
            print(f"Błąd wysyłania e-maila: {e}")
            return False

    @staticmethod
    def save_email_to_file(recipient, title, message, sender):
        if os.path.exists(MAILS_FILE):
            with open(MAILS_FILE, 'r', encoding="utf-8") as file:
                emails = json.load(file)
        else:
            emails = []

        date = datetime.now()
        date = date.strftime("%d/%m/%Y %H:%M:%S")

        new_email = {
            "id": len(emails) + 1,
            "date": date,
            "sender": sender,
            "recipient": recipient,
            "title": title,
            "message": message,
        }
        emails.append(new_email)

        with open(MAILS_FILE, 'w', encoding="utf-8") as file:
            json.dump(emails, file, ensure_ascii=False, indent=4)

    

# ---------------------------------------------------------- REQUESTY UZYTKOWNICY ----------------------------------------------------------

class Requests():
    def __init__(self, id, imie, nazwisko, email, rola, haslo):
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.email = email
        self.rola = rola
        self.haslo = haslo

    def to_dict(self):
        return {
            "id": self.id,
            "imie": self.imie,
            "nazwisko": self.nazwisko,
            "email": self.email,
            "rola": self.rola,
            "haslo": self.haslo
        }

    @staticmethod
    def from_json(data):
        return Requests(
            id=data["id"],
            imie=data["imie"],
            nazwisko=data["nazwisko"],
            email=data["email"],
            rola=data["rola"],
            haslo=data["haslo"]
        )
    @staticmethod
    def get_all_requests():
        with open("data/requests.json", "r", encoding="utf-8") as file:
            requests_data = json.load(file)
            return [Requests.from_json(user) for user in requests_data]

    @staticmethod
    def save_request(new_request):
        with open("data/requests.json", "r", encoding="utf-8") as file:
            requests_data = json.load(file)

        requests_data.append(new_request.to_dict())

        with open("data/requests.json", "w", encoding="utf-8") as file:
            json.dump(requests_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def delete_request(request_id):
        try:
            with open("data/requests.json", "r", encoding="utf-8") as file:
                requests_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            requests_data = []

        requests_data = [
            request for request in requests_data if request.get("id") != request_id
        ]

        with open("data/requests.json", "w", encoding="utf-8") as file:
            json.dump(requests_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_all_requests():
        with open("data/requests.json", "r", encoding="utf-8") as file:
            requests_data = json.load(file)
            return [Requests.from_json(user) for user in requests_data]

# ---------------------------------------------------------- KONTO BANKOWE ----------------------------------------------------------
    
class Konto_Bankowe():
    def __init__(self, id, student_id, saldo):
        self.id = id
        self.student_id = student_id
        self.saldo = saldo

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "saldo": self.saldo
        }

    @staticmethod
    def from_json(data):
        return Konto_Bankowe(
            id=data["id"],
            student_id=data["student_id"],
            saldo=data["saldo"]
        )
    
    @staticmethod
    def get_all_bank_accounts():
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            konta_bankowe_data = json.load(file)
            return [Konto_Bankowe.from_json(konto_bankowe) for konto_bankowe in konta_bankowe_data]

    @staticmethod
    def save_bank_account(new_bank_account):
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            konta_bankowe_data = json.load(file)

        konta_bankowe_data.append(new_bank_account.to_dict())

        with open("data/konta_bankowe.json", "w", encoding="utf-8") as file:
            json.dump(konta_bankowe_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_student_email(student_id):
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as file:
            uzytkownicy_data = json.load(file)
            user = next((item for item in uzytkownicy_data if item["id"] == student_id), None)
            return user["email"] if user else None

    @staticmethod
    def get_student_balance(student_id):
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            student = next((item for item in data if item["student_id"] == student_id), None)
            return student["saldo"] if student else None
        
    @staticmethod
    def get_student_bank_account_id(student_id):
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            student = next((item for item in data if item["student_id"] == student_id), None)
            return student["id"] if student else None
        
    @staticmethod
    def add_balance(account_id, ammount):
        account_id = int(account_id)
        
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        
        account = next((item for item in data if item["id"] == account_id), None)

        if account:
            if "saldo" in account:
                account["saldo"] += int(ammount)
            else:
                raise KeyError(f"Student {account_id} nie zawiera pola saldo.")
        else:
            raise ValueError(f"Student {account_id} nie istnieje.")

        with open("data/konta_bankowe.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod 
    def take_balance(account_id, ammount):
        account_id = int(account_id)
        
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        
        account = next((item for item in data if item["id"] == account_id), None)

        if account:
            if "saldo" in account:
                account["saldo"] -= int(ammount)
            else:
                raise KeyError(f"Student {account_id} nie zawiera pola saldo.")
        else:
            raise ValueError(f"Student {account_id} nie istnieje.")

        with open("data/konta_bankowe.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def delete_account(user_id):
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        updated_accounts = [konto for konto in data if konto['student_id'] != user_id]
        with open("data/konta_bankowe.json", "w", encoding="utf-8") as file:
            json.dump(updated_accounts, file, ensure_ascii=False, indent=4)
        
# ---------------------------------------------------------- PŁATNOŚCI ----------------------------------------------------------

class Payment():
    def __init__(self, id, konto_id, title, ammount, date):
        self.id = id
        self.konto_id = konto_id
        self.title = title
        self.ammount = ammount
        self.date = date

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "id_konta": self.konto_id,
            "tytuł": self.title,
            "kwota": self.ammount
        }
    
    @staticmethod
    def from_json(data):
        return Payment(
            id=data["id"],
            date=data["date"],
            konto_id=data["id_konta"],
            title=data["tytuł"],
            ammount=data["kwota"]
        )
    
    @staticmethod
    def get_all_payments():
        with open("data/payments.json", "r", encoding="utf-8") as file:
            payments_data = json.load(file)
            return [Payment.from_json(payment) for payment in payments_data]
        
    @staticmethod
    def save_payment(new_payment):
        with open("data/payments.json", "r", encoding="utf-8") as file:
            payments_data = json.load(file)

        payments_data.append(new_payment.to_dict())

        with open("data/payments.json", "w", encoding="utf-8") as file:
            json.dump(payments_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_payments_history(account_id):
        account_id = int(account_id)

        with open('data/payments.json', 'r', encoding='utf-8') as file:
            payments = json.load(file)
            
        payments_history = [p for p in payments if p.get("id_konta") == account_id]
            
        return payments_history
    
    def delete_payments(user_id):
        with open("data/konta_bankowe.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        konto = next((item for item in data if item["student_id"] == user_id), None)
        
        with open("data/payments.json", "r", encoding="utf-8") as file:
            payments_data = json.load(file)
        updated_payments = [payment for payment in payments_data if payment['id_konta'] != int(konto["id"])]
        with open("data/payments.json", "w", encoding="utf-8") as file:
            json.dump(updated_payments, file, ensure_ascii=False, indent=4)

# ---------------------------------------------------------- KIERUNKI ----------------------------------------------------------

class Kierunki:
    def __init__(self, id, nazwa, typ, opis):
        self.id = id
        self.nazwa = nazwa
        self.typ = typ
        self.opis = opis


    def to_dict(self):
        return {
            "id": self.id,
            "nazwa": self.nazwa,
            "typ": self.typ,
            "opis": self.opis
        }

    @staticmethod
    def from_json(data):
        return Kierunki(
            id=data["id"],
            nazwa=data["nazwa"],
            typ=data["typ"],
            opis=data["opis"]
        )
    @staticmethod
    def get_all_kierunki():
        with open("data/kierunki.json", "r", encoding="utf-8") as file:
            kierunki_data = json.load(file)
            return [Kierunki.from_json(kierunek) for kierunek in kierunki_data]

    @staticmethod
    def save_kierunek(new_kierunek):
        with open("data/kierunki.json", "r", encoding="utf-8") as file:
            kierunki_data = json.load(file)

        kierunki_data.append(new_kierunek.to_dict())

        with open("data/kierunki.json", "w", encoding="utf-8") as file:
            json.dump(kierunki_data, file, ensure_ascii=False, indent=4)

# ---------------------------------------------------------- REQUESTY KIERUNEK ----------------------------------------------------------        

class Requests_Kierunki:
    def __init__(self, id, imie, nazwisko, email, rola, haslo, kierunek, grupa, semestr):
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.email = email
        self.rola = rola
        self.haslo = haslo
        self.kierunek = kierunek
        self.grupa = grupa
        self.semestr = semestr

    def to_dict(self):
        return {
            "id": self.id,
            "imie": self.imie,
            "nazwisko": self.nazwisko,
            "email": self.email,
            "rola": self.rola,
            "haslo": self.haslo,
            "kierunek": self.kierunek,
            "grupa": self.grupa,
            "semestr": self.semestr
        }

    @staticmethod
    def from_json(data):
        return Requests_Kierunki(
            id=data["id"],
            imie=data["imie"],
            nazwisko=data["nazwisko"],
            email=data["email"],
            rola=data["rola"],
            haslo=data["haslo"],
            kierunek=data["kierunek"],
            grupa=data["grupa"],
            semestr=data["semestr"]
        )

    @staticmethod
    def get_all_requests_kierunki():
            with open("data/requests_kierunki.json", "r", encoding="utf-8") as file:
                requests_kierunki_data = json.load(file)
                return [Requests_Kierunki.from_json(user) for user in requests_kierunki_data]

    @staticmethod
    def save_request_kierunki(new_request_kierunek):
        try:
            with open("data/requests_kierunki.json", "r", encoding="utf-8") as file:
                requests_kierunki_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            requests_kierunki_data = []

        requests_kierunki_data.append(new_request_kierunek.to_dict())

        with open("data/requests_kierunki.json", "w", encoding="utf-8") as file:
            json.dump(requests_kierunki_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def reject_request(request_id):
        try:
            with open("data/requests_kierunki.json", "r", encoding="utf-8") as file:
                requests_kierunki_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            requests_kierunki_data = []

        requests_kierunki_data = [
            request for request in requests_kierunki_data if request.get("id") != request_id
        ]

        with open("data/requests_kierunki.json", "w", encoding="utf-8") as file:
            json.dump(requests_kierunki_data, file, ensure_ascii=False, indent=4)

    def delete_request(request_id):
        with open("data/requests_kierunki.json", "r", encoding="utf-8") as file:
            requests_kierunki_data = json.load(file)
        updated_requests = [req for req in requests_kierunki_data if req['id'] != request_id]
        with open("data/requests_kierunki.json", "w", encoding="utf-8") as file:
            json.dump(updated_requests, file, ensure_ascii=False, indent=4)

# ---------------------------------------------------------- GRUPY ----------------------------------------------------------            

class Grupy:
    def __init__(self, id, nazwa, semestr, kierunek, przedmioty=None):
        self.id = id
        self.nazwa = nazwa
        self.semestr = semestr
        self.kierunek = kierunek
        self.przedmioty = przedmioty if przedmioty is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "nazwa": self.nazwa,
            "semestr": self.semestr,
            "kierunek": self.kierunek,
            "przedmioty": self.przedmioty,
        }

    @staticmethod
    def from_json(data):
        return Grupy(
            id=data["id"],
            nazwa=data["nazwa"],
            semestr=data["semestr"],
            kierunek=data["kierunek"],
            przedmioty=data.get("przedmioty", []),
        )


    @staticmethod
    def save_grupa(new_grupa):
        with open("data/grupy.json", "r", encoding="utf-8") as file:
            Grupy_data = json.load(file)

        Grupy_data.append(new_grupa.to_dict())

        with open("data/grupy.json", "w", encoding="utf-8") as file:
            json.dump(Grupy_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_all_grupy():
        with open("data/grupy.json", "r", encoding="utf-8") as file:
            Grupy_data = json.load(file)
            return [Grupy.from_json(user) for user in Grupy_data]


    @staticmethod
    def get_grupa_by_id(grupa_id):
        with open("data/grupy.json", "r", encoding="utf-8") as file:
            Grupy_data = json.load(file)
            for grupa in Grupy_data:
                if grupa["id"] == grupa_id:
                    return Grupy.from_json(grupa)
        return None  # Zwróć None, jeśli grupa nie została znaleziona
# ---------------------------------------------------------- PRZEDMIOTY ----------------------------------------------------------

class Przedmioty:
    def __init__(self, id, nazwa, wykladowca_id, ects, opis, egzamin):
        self.id = id
        self.nazwa = nazwa
        self.wykladowca_id = wykladowca_id
        self.ects = ects
        self.opis = opis
        self.egzamin = egzamin

    def to_dict(self):
        return {
            "id": self.id,
            "nazwa": self.nazwa,
            "wykladowca_id": self.wykladowca_id,
            "ects": self.ects,
            "opis": self.opis,
            "egzamin": self.egzamin
        }

    @staticmethod
    def from_json(data):
        return Przedmioty(
            id=data["id"],
            nazwa=data["nazwa"],
            wykladowca_id=data["wykladowca_id"],
            ects=data["ects"],
            opis=data["opis"],
            egzamin=data["egzamin"]
        )

    @staticmethod
    def get_all_przedmioty():
        with open("data/przedmioty.json", "r", encoding="utf-8") as file:
            przedmioty_data = json.load(file)
            return [Przedmioty.from_json(przedmiot) for przedmiot in przedmioty_data]
        
    def get_przedmioty_wykladowca(user_id):
        user_id = str(user_id)
        with open("data/przedmioty.json", "r", encoding="utf-8") as file:
            przedmioty_data = json.load(file)

        przedmioty = [p for p in przedmioty_data if p.get("wykladowca_id") == user_id]

        return przedmioty

    @staticmethod
    def save_przedmiot(new_przedmiot):
        with open("data/przedmioty.json", "r", encoding="utf-8") as file:
            przedmioty_data = json.load(file)

        przedmioty_data.append(new_przedmiot.to_dict())

        with open("data/przedmioty.json", "w", encoding="utf-8") as file:
            json.dump(przedmioty_data, file, ensure_ascii=False, indent=4)

# ---------------------------------------------------------- ZAJECIA ----------------------------------------------------------

class Zajecia:
    def __init__(self, id, przedmiot_id, grupa_id, sala, rodzaj, rozpoczecie, zakonczenie):
        self.id = id
        self.przedmiot_id = przedmiot_id
        self.grupa_id = grupa_id
        self.sala = sala
        self.rodzaj = rodzaj
        self.rozpoczecie = rozpoczecie
        self.zakonczenie = zakonczenie

    def to_dict(self):
        return {
            "id": self.id,
            "przedmiot_id": self.przedmiot_id,
            "grupa_id": self.grupa_id,
            "sala": self.sala,
            "rodzaj": self.rodzaj,
            "rozpoczecie": self.rozpoczecie,
            "zakonczenie": self.zakonczenie
        }

    @staticmethod
    def from_json(data):
        return Zajecia(
            id=data["id"],
            przedmiot_id=data["przedmiot_id"],
            grupa_id=data["grupa_id"],
            sala=data["sala"],
            rodzaj=data["rodzaj"],
            rozpoczecie=data["rozpoczecie"],
            zakonczenie=data["zakonczenie"]
            )

    @staticmethod
    def get_all_zajecia():
        with open("data/zajecia.json", "r", encoding="utf-8") as file:
            zajecia_data = json.load(file)
            return [Zajecia.from_json(zajecie) for zajecie in zajecia_data]

    @staticmethod
    def save_zajecie(new_zajecie):
        with open("data/zajecia.json", "r", encoding="utf-8") as file:
            zajecia_data = json.load(file)

        zajecia_data.append(new_zajecie.to_dict())

        with open("data/zajecia.json", "w", encoding="utf-8") as file:
            json.dump(zajecia_data, file, ensure_ascii=False, indent=4)


    def delete_zajecie(zajecie_id):
        with open("data/zajecia.json", "r", encoding="utf-8") as file:
            zajecia_data = json.load(file)

        updated_zajecia = [zajecia for zajecia in zajecia_data if zajecia['id'] != zajecie_id]
        
        with open("data/zajecia.json", "w", encoding="utf-8") as file:
            json.dump(updated_zajecia, file, ensure_ascii=False, indent=4)
    @staticmethod
    def sorted_zajecia():
        with open("data/zajecia.json", "r", encoding="utf-8") as file:
            zajecia = json.load(file)
            zajecia_po_dacie = {}
        for zajecie in zajecia:
            zajecie_data = zajecie["rozpoczecie"][:10]
            if zajecie_data not in zajecia_po_dacie:
                zajecia_po_dacie[zajecie_data] = []
            zajecia_po_dacie[zajecie_data].append(zajecie)
        return zajecia_po_dacie
    
# ---------------------------------------------------------- OCENY ----------------------------------------------------------

class Oceny:
    def __init__(self, id, student_id, wykladowca_id, przedmiot_id, ocena):
        self.id = id
        self.student_id = student_id
        self.wykladowca_id = wykladowca_id
        self.przedmiot_id = przedmiot_id
        self.ocena = ocena

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "wykladowca_id": self.wykladowca_id,
            "przedmiot_id": self.przedmiot_id,
            "ocena": self.ocena
        }

    @staticmethod
    def from_json(data):
        return Oceny(
            id=data["id"],
            student_id=data["student_id"],
            wykladowca_id=data["wykladowca_id"],
            przedmiot_id=data["przedmiot_id"],
            ocena=data["ocena"]
        )

    @staticmethod
    def get_all_oceny():
        with open("data/oceny.json", "r", encoding="utf-8") as file:
            oceny_data = json.load(file)
            return [Oceny.from_json(ocena) for ocena in oceny_data]
        
    def get_oceny_student(user_id):
        user_id = str(user_id)
        with open("data/oceny.json", "r", encoding="utf-8") as file:
            oceny_data = json.load(file)

        oceny = [o for o in oceny_data if o.get("student_id") == user_id]
            
        return oceny
    
    def get_oceny_przedmioty(oceny_student):
        przedmioty_data = Przedmioty.get_all_przedmioty()
        
        przedmioty = []
        for ocena in oceny_student:
            for przedmiot in przedmioty_data:
                if int(ocena['przedmiot_id']) == przedmiot.id:
                    przedmioty.append(przedmiot)
        return przedmioty

    @staticmethod
    def save_ocena(new_ocena):
        with open("data/oceny.json", "r", encoding="utf-8") as file:
            oceny_data = json.load(file)

        oceny_data.append(new_ocena.to_dict())

        with open("data/oceny.json", "w", encoding="utf-8") as file:
            json.dump(oceny_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def update_ocena(updated_ocena):
        with open("data/oceny.json", "r", encoding="utf-8") as file:
            oceny_data = json.load(file)

        for ocena in oceny_data:
            if ocena["student_id"] == updated_ocena.student_id and ocena["przedmiot_id"] == updated_ocena.przedmiot_id:
                ocena["ocena"] = updated_ocena.ocena
                break

        with open("data/oceny.json", "w", encoding="utf-8") as file:
            json.dump(oceny_data, file, ensure_ascii=False, indent=4)

    def delete_oceny(user_id):
        with open("data/oceny.json", "r", encoding="utf-8") as file:
            oceny_data = json.load(file)

        updated_oceny = [ocena for ocena in oceny_data if ocena['student_id'] != str(user_id)]
        with open("data/oceny.json", "w", encoding="utf-8") as file:
            json.dump(updated_oceny, file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_srednia_ocen():
        with open("data/oceny.json", "r", encoding="utf-8") as file:
            oceny_data = json.load(file)

        oceny = [int(o["ocena"]) for o in oceny_data]

        if len(oceny) == 0:
            return "Brak ocen"

        avg_ocena = round(sum(oceny) / len(oceny), 2)

        return avg_ocena
    
    @staticmethod
    def get_srednia_dla_kierunku():
        with open("data/oceny.json", "r", encoding="utf-8") as f:
            oceny_data = json.load(f)
        
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as f:
            uzytkownicy_data = json.load(f)
        
        student_to_kierunek = {}

        # przypisanie studentowi jego kierunku
        for uzytkownik in uzytkownicy_data:
            if uzytkownik["rola"] == "Student":
                student_id = int(uzytkownik["id"])
                kierunek_id = uzytkownik["kierunek"]
                student_to_kierunek[student_id] = kierunek_id
        
        kierunek_oceny = {}

        # przypisanie kierunkowi oceny
        for ocena in oceny_data:
            student_id = int(ocena["student_id"])
            if student_id in student_to_kierunek:
                kierunek_id = student_to_kierunek[student_id]
                if kierunek_id not in kierunek_oceny:
                    kierunek_oceny[kierunek_id] = []
                
                kierunek_oceny[kierunek_id].append(int(ocena["ocena"]))
        
        avg_ocena_kierunek = {}

        # obliczenie sredniej dla kierunku
        for kierunek_id, oceny in kierunek_oceny.items():
            suma_ocen = sum(oceny)
            liczba_ocen = len(oceny)
            if liczba_ocen == 0:
                return "Brak ocen"
            srednia = suma_ocen / liczba_ocen if liczba_ocen > 0 else 0
            avg_ocena_kierunek[kierunek_id] = round(srednia, 2)
        
        return avg_ocena_kierunek
        
# ---------------------------------------------------------- EGZAMINY ----------------------------------------------------------

class Egzaminy:
    def __init__(self, id, data, przedmiot_id, wykladowca_id, grupa_id):
        self.id = id
        self.data = data
        self.wykladowca_id = wykladowca_id
        self.przedmiot_id = przedmiot_id
        self.grupa_id = grupa_id

    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data,
            "wykladowca_id": self.wykladowca_id,
            "przedmiot_id": self.przedmiot_id,
            "grupa_id": self.grupa_id
        }

    @staticmethod
    def from_json(data):
        return Egzaminy(
            id=data["id"],
            data=data["data"],
            wykladowca_id=data["wykladowca_id"],
            przedmiot_id=data["przedmiot_id"],
            grupa_id=data["grupa_id"]
        )

    @staticmethod
    def get_all_egzaminy():
        with open("data/egzaminy.json", "r", encoding="utf-8") as file:
            egzaminy_data = json.load(file)
            return [Egzaminy.from_json(egzamin) for egzamin in egzaminy_data]

    @staticmethod
    def save_egzamin(new_egzamin):
        with open("data/egzaminy.json", "r", encoding="utf-8") as file:
            egzaminy_data = json.load(file)

        egzaminy_data.append(new_egzamin.to_dict())

        with open("data/egzaminy.json", "w", encoding="utf-8") as file:
            json.dump(egzaminy_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def update_egzamin(updated_egzamin):
        with open("data/egzaminy.json", "r", encoding="utf-8") as file:
            egzaminy_data = json.load(file)

        for egzamin in egzaminy_data:
            if egzamin["grupa_id"] == updated_egzamin.grupa_id and egzamin["przedmiot_id"] == updated_egzamin.przedmiot_id:
                egzamin["data"] = updated_egzamin.data
                break

        with open("data/egzaminy.json", "w", encoding="utf-8") as file:
            json.dump(egzaminy_data, file, ensure_ascii=False, indent=4)

    def delete_egzamin(egzamin_id):
        with open("data/egzaminy.json", "r", encoding="utf-8") as file:
            egzaminy_data = json.load(file)

        updated_egzaminy = [egzamin for egzamin in egzaminy_data if egzamin['id'] != egzamin_id]
        
        with open("data/egzaminy.json", "w", encoding="utf-8") as file:
            json.dump(updated_egzaminy, file, ensure_ascii=False, indent=4)

    @staticmethod
    def sorted_egzaminy():
        with open("data/egzaminy.json", "r", encoding="utf-8") as file:
            egzaminy = json.load(file)
            egzaminy_po_dacie = {}
        for egzamin in egzaminy:
            egzamin_data = egzamin["data"][:10]  # Wyciągnięcie daty (YYYY-MM-DD)
            if egzamin_data not in egzaminy_po_dacie:
                egzaminy_po_dacie[egzamin_data] = []
            egzaminy_po_dacie[egzamin_data].append(egzamin)
        return egzaminy_po_dacie

    @staticmethod
    def get_sredni_wynik():
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as file:
            egzaminy_data = json.load(file)

        egzaminy = [int(e["wynik"]) for e in egzaminy_data]

        if len(egzaminy) == 0:
            return "Brak wyników z egzaminów"

        avg_egzamin = round(sum(egzaminy) / len(egzaminy), 2)

        return avg_egzamin
    
    @staticmethod
    def get_srednia_wynikow_dla_kierunku():
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as f:
            wyniki_data = json.load(f)
        with open("data/uzytkownicy.json", "r", encoding="utf-8") as f:
            uzytkownicy_data = json.load(f)

        student_to_kierunek = {}

        # Przypisanie studentowi jego kierunku
        for uzytkownik in uzytkownicy_data:
            if uzytkownik["rola"] == "Student":
                student_id = int(uzytkownik["id"])
                kierunek_id = uzytkownik["kierunek"]
                student_to_kierunek[student_id] = kierunek_id

        kierunek_wyniki = {}

        # Przypisanie kierunkowi wyniku egzaminu
        for wynik in wyniki_data:
            student_id = int(wynik["student_id"])
            if student_id in student_to_kierunek:
                kierunek_id = student_to_kierunek[student_id]
                if kierunek_id not in kierunek_wyniki:
                    kierunek_wyniki[kierunek_id] = []

                kierunek_wyniki[kierunek_id].append(int(wynik["wynik"]))

        avg_wynik_kierunek = {}

        # Obliczenie średniego wyniku dla kierunku
        for kierunek_id, wyniki in kierunek_wyniki.items():
            suma_wynikow = sum(wyniki)
            liczba_wynikow = len(wyniki)
            if liczba_wynikow == 0:
                return "Brak wyników z egzaminów"
            srednia = suma_wynikow / liczba_wynikow if liczba_wynikow > 0 else 0
            avg_wynik_kierunek[kierunek_id] = round(srednia, 2)

        return avg_wynik_kierunek

# ---------------------------------------------------------- EGZAMINY WYNIKI----------------------------------------------------------

class Egzaminy_Wyniki:
    def __init__(self, id, egzamin_id, student_id, wynik):
        self.id = id
        self.egzamin_id = egzamin_id
        self.student_id = student_id
        self.wynik = wynik

    def to_dict(self):
        return {
            "id": self.id,
            "egzamin_id": self.egzamin_id,
            "student_id": self.student_id,
            "wynik": self.wynik
        }

    @staticmethod
    def from_json(data):
        return Egzaminy_Wyniki(
            id=data["id"],
            egzamin_id=data["egzamin_id"],
            student_id=data["student_id"],
            wynik=data["wynik"]
        )

    @staticmethod
    def get_all_egzaminy_wyniki():
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as file:
            egzaminy_wyniki_data = json.load(file)
            return [Egzaminy_Wyniki.from_json(egzamin_wynik) for egzamin_wynik in egzaminy_wyniki_data]
        
    def get_egzaminy_wyniki_student(user_id):
        user_id = str(user_id)
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as file:
            egzaminy_wyniki_data = json.load(file)

        egzaminy_wyniki = [e for e in egzaminy_wyniki_data if e.get("student_id") == user_id]
            
        return egzaminy_wyniki
        
    @staticmethod
    def save_egzamin_wynik(new_egzamin_wynik):
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as file:
            egzaminy_wyniki_data = json.load(file)

        egzaminy_wyniki_data.append(new_egzamin_wynik.to_dict())

        with open("data/egzaminy_wyniki.json", "w", encoding="utf-8") as file:
            json.dump(egzaminy_wyniki_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def update_egzamin_wynik(updated_egzamin_wynik):
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as file:
            egzaminy_wyniki_data = json.load(file)

        for egzamin_wynik in egzaminy_wyniki_data:
            if egzamin_wynik["student_id"] == updated_egzamin_wynik.student_id and egzamin_wynik["egzamin_id"] == updated_egzamin_wynik.egzamin_id:
                egzamin_wynik["wynik"] = updated_egzamin_wynik.wynik
                break

        with open("data/egzaminy_wyniki.json", "w", encoding="utf-8") as file:
            json.dump(egzaminy_wyniki_data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def delete_egzaminy(user_id):
        with open("data/egzaminy_wyniki.json", "r", encoding="utf-8") as file:
            egzaminy_data = json.load(file)

        updated_egzaminy = [egzamin for egzamin in egzaminy_data if egzamin['student_id'] != str(user_id)]
        with open("data/egzaminy_wyniki.json", "w", encoding="utf-8") as file:
            json.dump(updated_egzaminy, file, ensure_ascii=False, indent=4)
