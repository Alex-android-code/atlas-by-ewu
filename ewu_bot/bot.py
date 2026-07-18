import json
import os
import re
import time
from datetime import datetime, timezone
from html import escape as html_escape

import requests
import telebot
from telebot import apihelper
from telebot import types

from .ai import ai_next_turn, ai_reply, ai_summary
from .config import ADMIN_CHAT_ID, BANNER_FILE, DEFAULT_LANG, EWU_DATA_DIR, TELEGRAM_TOKEN
from .crm import ensure_dirs, load_backups, log_error, send_crm, update_status
from .ewu_id import new_candidate_id, new_case_id, new_employer_id
from .extractor import extract
from .i18n import t
from .keyboards import admin_keyboard, contact_keyboard, lang_keyboard, role_keyboard, yes_no_keyboard
from .language_detect import detect_lang, normalize_lang
from .learning import save_feedback, save_learning_note
from .notifier import leads, operations
from .pdf_card import make_candidate_pdf, make_vacancy_pdf
from . import qualification


if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN missing. Fill .env before running the bot.")


bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")
USERS = {}
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{7,18}\d)")
POLLING_NETWORK_ERRORS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout,
    requests.exceptions.Timeout,
    ConnectionResetError,
    TimeoutError,
    OSError,
)
POLLING_MIN_RESTART_DELAY = 5
POLLING_MAX_RESTART_DELAY = 60


def reset_telegram_http_session():
    try:
        session = apihelper._get_req_session()
        session.close()
    except Exception:
        pass
    apihelper.session = None


def run_polling_forever():
    delay = POLLING_MIN_RESTART_DELAY
    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=20,
                long_polling_timeout=20,
                restart_on_change=False,
                logger_level=None,
            )
            delay = POLLING_MIN_RESTART_DELAY
        except POLLING_NETWORK_ERRORS as exc:
            print(f"Polling network error, restarting in {delay}s:", exc, flush=True)
            log_error("polling_network", exc)
            reset_telegram_http_session()
            time.sleep(delay)
            delay = min(delay * 2, POLLING_MAX_RESTART_DELAY)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"Polling error, restarting in {delay}s:", exc, flush=True)
            log_error("polling", exc)
            reset_telegram_http_session()
            time.sleep(delay)
            delay = min(delay * 2, POLLING_MAX_RESTART_DELAY)
OK_WORDS = {"ok", "done", "готово", "готова", "готов", "так", "да", "yes", "finish", "koniec"}


CANDIDATE_FIELDS = [
    ("First_Name", {"pl": "Jak masz na imię?", "ua": "Як вас звати?", "ru": "Как вас зовут?", "en": "What is your first name?", "de": "Wie ist Ihr Vorname?", "es": "¿Cuál es su nombre?", "pt": "Qual é o seu nome?"}),
    ("Last_Name", {"pl": "Jakie jest Twoje nazwisko?", "ua": "Ваше прізвище?", "ru": "Ваша фамилия?", "en": "What is your last name?", "de": "Wie ist Ihr Nachname?", "es": "¿Cuál es su apellido?", "pt": "Qual é o seu apelido?"}),
    ("Date_of_birth", {"pl": "Podaj datę urodzenia.", "ua": "Вкажіть дату народження.", "ru": "Укажите дату рождения.", "en": "Date of birth?", "de": "Geburtsdatum?", "es": "Fecha de nacimiento?", "pt": "Data de nascimento?"}),
    ("Nationality", {"pl": "Jakie masz obywatelstwo?", "ua": "Яке у вас громадянство?", "ru": "Какое у вас гражданство?", "en": "Nationality?", "de": "Staatsangehörigkeit?", "es": "Nacionalidad?", "pt": "Nacionalidade?"}),
    ("Current_country", {"pl": "W jakim kraju jesteś teraz?", "ua": "У якій країні ви зараз?", "ru": "В какой стране вы сейчас?", "en": "Current country?", "de": "Aktuelles Land?", "es": "País actual?", "pt": "País atual?"}),
    ("Current_city", {"pl": "W jakim mieście jesteś?", "ua": "У якому місті?", "ru": "В каком городе?", "en": "Current city?", "de": "Aktuelle Stadt?", "es": "Ciudad actual?", "pt": "Cidade atual?"}),
    ("Profession", {"pl": "Jaka profesja lub specjalizacja?", "ua": "Яка професія або спеціалізація?", "ru": "Какая профессия или специализация?", "en": "Profession or specialization?", "de": "Beruf oder Spezialisierung?", "es": "Profesión o especialización?", "pt": "Profissão ou especialização?"}),
    ("Experience", {"pl": "Ile lat doświadczenia?", "ua": "Скільки років досвіду?", "ru": "Сколько лет опыта?", "en": "Years of experience?", "de": "Wie viele Jahre Erfahrung?", "es": "Años de experiencia?", "pt": "Anos de experiência?"}),
    ("Welding_methods", {"pl": "Jakie metody spawania znasz?", "ua": "Які методи зварювання знаєте?", "ru": "Какие методы сварки знаете?", "en": "Which welding methods do you use?", "de": "Welche Schweißverfahren nutzen Sie?", "es": "¿Qué métodos de soldadura usa?", "pt": "Que métodos de soldadura usa?"}),
    ("Foreign_experience", {"pl": "Czy masz doświadczenie pracy za granicą?", "ua": "Чи маєте досвід роботи за кордоном?", "ru": "Есть опыт работы за границей?", "en": "Do you have foreign work experience?", "de": "Haben Sie Auslandserfahrung?", "es": "¿Tiene experiencia laboral en el extranjero?", "pt": "Tem experiência no estrangeiro?"}),
    ("Countries_worked_in", {"pl": "W jakich krajach pracowałeś?", "ua": "У яких країнах працювали?", "ru": "В каких странах работали?", "en": "Countries previously worked in?", "de": "In welchen Ländern haben Sie gearbeitet?", "es": "¿En qué países ha trabajado?", "pt": "Em que países trabalhou?"}),
    ("Language_skills", {"pl": "Jakie języki znasz i na jakim poziomie?", "ua": "Які мови знаєте і на якому рівні?", "ru": "Какие языки знаете и на каком уровне?", "en": "Languages and level?", "de": "Sprachen und Niveau?", "es": "Idiomas y nivel?", "pt": "Idiomas e nível?"}),
    ("Certificates", {"pl": "Jakie certyfikaty posiadasz?", "ua": "Які сертифікати маєте?", "ru": "Какие сертификаты есть?", "en": "Which certificates do you have?", "de": "Welche Zertifikate haben Sie?", "es": "¿Qué certificados tiene?", "pt": "Que certificados tem?"}),
    ("Certificate_validity", {"pl": "Do kiedy certyfikaty są ważne?", "ua": "До коли дійсні сертифікати?", "ru": "До какого срока действуют сертификаты?", "en": "Certificate validity dates?", "de": "Gültigkeit der Zertifikate?", "es": "Validez de los certificados?", "pt": "Validade dos certificados?"}),
    ("Documents", {"pl": "Jaki jest status dokumentów?", "ua": "Який статус документів?", "ru": "Какой статус документов?", "en": "Documents status?", "de": "Dokumentenstatus?", "es": "Estado de documentos?", "pt": "Estado dos documentos?"}),
    ("Relocation_readiness", {"pl": "Od kiedy jesteś gotowy do relokacji?", "ua": "З якої дати готові до релокації?", "ru": "С какой даты готовы к релокации?", "en": "When are you ready to relocate?", "de": "Ab wann sind Sie umzugsbereit?", "es": "¿Desde cuándo puede reubicarse?", "pt": "Quando pode relocar-se?"}),
    ("Preferred_countries", {"pl": "W jakich krajach chcesz pracować?", "ua": "У яких країнах хочете працювати?", "ru": "В каких странах хотите работать?", "en": "Preferred countries?", "de": "Bevorzugte Länder?", "es": "Países preferidos?", "pt": "Países preferidos?"}),
    ("Overtime", {"pl": "Czy jesteś gotowy na nadgodziny?", "ua": "Чи готові до понаднормових?", "ru": "Готовы к сверхурочным?", "en": "Are you willing to work overtime?", "de": "Bereit für Überstunden?", "es": "¿Acepta horas extra?", "pt": "Aceita horas extra?"}),
    ("Travel_ready", {"pl": "Czy jesteś gotowy do delegacji?", "ua": "Чи готові до відряджень?", "ru": "Готовы к командировкам?", "en": "Are you willing to travel?", "de": "Bereit zu reisen?", "es": "¿Puede viajar?", "pt": "Pode viajar?"}),
    ("Team_lead_experience", {"pl": "Czy masz doświadczenie w prowadzeniu zespołu?", "ua": "Чи маєте досвід керування командою?", "ru": "Есть опыт руководства бригадой?", "en": "Experience leading teams?", "de": "Erfahrung in Teamleitung?", "es": "¿Experiencia liderando equipos?", "pt": "Experiência a liderar equipas?"}),
    ("Driving_Licence", {"pl": "Czy masz prawo jazdy?", "ua": "Чи маєте водійські права?", "ru": "Есть водительские права?", "en": "Do you have a driving licence?", "de": "Haben Sie einen Führerschein?", "es": "¿Tiene carnet de conducir?", "pt": "Tem carta de condução?"}),
    ("Driving_Categories", {"pl": "Jakie kategorie prawa jazdy?", "ua": "Які категорії прав?", "ru": "Какие категории прав?", "en": "Driving licence categories?", "de": "Führerscheinklassen?", "es": "Categorías del carnet?", "pt": "Categorias da carta?"}),
    ("Own_Vehicle", {"pl": "Czy masz własny samochód?", "ua": "Чи маєте власний автомобіль?", "ru": "Есть свой автомобиль?", "en": "Do you have your own vehicle?", "de": "Haben Sie ein eigenes Fahrzeug?", "es": "¿Tiene vehículo propio?", "pt": "Tem veículo próprio?"}),
    ("Phone", "phone"),
    ("WhatsApp", {"pl": "Podaj WhatsApp, jeśli jest inny niż telefon. Jeśli taki sam, napisz TAKI SAM.", "ua": "Вкажіть WhatsApp, якщо він інший. Якщо той самий, напишіть ТАК САМО.", "ru": "Укажите WhatsApp, если он отличается. Если такой же, напишите ТАКОЙ ЖЕ.", "en": "Share WhatsApp if different. If the same, write SAME.", "de": "WhatsApp falls abweichend. Wenn gleich, schreiben Sie SAME.", "es": "WhatsApp si es distinto. Si igual, escriba SAME.", "pt": "WhatsApp se for diferente. Se igual, escreva SAME."}),
]


EMPLOYER_FIELDS = [
    ("Company", {"pl": "Nazwa firmy?", "ua": "Назва компанії?", "ru": "Название компании?", "en": "Company name?", "de": "Firmenname?", "es": "Nombre de la empresa?", "pt": "Nome da empresa?"}),
    ("Contact_person", {"pl": "Osoba kontaktowa?", "ua": "Контактна особа?", "ru": "Контактное лицо?", "en": "Contact person?", "de": "Kontaktperson?", "es": "Persona de contacto?", "pt": "Pessoa de contacto?"}),
    ("Country", {"pl": "Kraj pracy?", "ua": "Країна роботи?", "ru": "Страна работы?", "en": "Country?", "de": "Land?", "es": "País?", "pt": "País?"}),
    ("City", {"pl": "Miasto pracy?", "ua": "Місто роботи?", "ru": "Город работы?", "en": "City?", "de": "Stadt?", "es": "Ciudad?", "pt": "Cidade?"}),
    ("Vacancy", {"pl": "Jakich specjalistów potrzebujecie?", "ua": "Які спеціалісти потрібні?", "ru": "Какие специалисты нужны?", "en": "Profession required?", "de": "Gesuchte Fachkräfte?", "es": "Profesión requerida?", "pt": "Profissão necessária?"}),
    ("Quantity", {"pl": "Ilu pracowników potrzeba?", "ua": "Скільки працівників потрібно?", "ru": "Сколько работников нужно?", "en": "Number of workers?", "de": "Anzahl der Mitarbeiter?", "es": "Número de trabajadores?", "pt": "Número de trabalhadores?"}),
    ("Project_description", {"pl": "Krótki opis projektu lub produkcji?", "ua": "Короткий опис проєкту або виробництва?", "ru": "Краткое описание проекта или производства?", "en": "Project or production description?", "de": "Projekt- oder Produktionsbeschreibung?", "es": "Descripción del proyecto?", "pt": "Descrição do projeto?"}),
    ("Contract_type", {"pl": "Typ umowy?", "ua": "Тип договору?", "ru": "Тип договора?", "en": "Contract type?", "de": "Vertragsart?", "es": "Tipo de contrato?", "pt": "Tipo de contrato?"}),
    ("Salary", {"pl": "Stawka lub wynagrodzenie?", "ua": "Ставка або зарплата?", "ru": "Ставка или зарплата?", "en": "Salary or rate?", "de": "Lohn oder Satz?", "es": "Salario o tarifa?", "pt": "Salário ou taxa?"}),
    ("Working_hours", {"pl": "Ile godzin miesięcznie?", "ua": "Скільки годин на місяць?", "ru": "Сколько часов в месяц?", "en": "Working hours?", "de": "Arbeitsstunden?", "es": "Horas de trabajo?", "pt": "Horas de trabalho?"}),
    ("Shifts", {"pl": "Zmiany i grafik?", "ua": "Зміни та графік?", "ru": "Смены и график?", "en": "Shifts and schedule?", "de": "Schichten und Zeitplan?", "es": "Turnos y horario?", "pt": "Turnos e horário?"}),
    ("Accommodation", {"pl": "Czy jest zakwaterowanie?", "ua": "Чи є проживання?", "ru": "Есть проживание?", "en": "Accommodation availability?", "de": "Unterkunft verfügbar?", "es": "¿Hay alojamiento?", "pt": "Há alojamento?"}),
    ("Transport", {"pl": "Czy jest transport?", "ua": "Чи є транспорт?", "ru": "Есть транспорт?", "en": "Transport availability?", "de": "Transport verfügbar?", "es": "¿Hay transporte?", "pt": "Há transporte?"}),
    ("Work_clothing", {"pl": "Informacja o odzieży roboczej?", "ua": "Інформація про робочий одяг?", "ru": "Информация о рабочей одежде?", "en": "Work clothing information?", "de": "Information zu Arbeitskleidung?", "es": "Información sobre ropa laboral?", "pt": "Informação sobre roupa de trabalho?"}),
    ("Meals", {"pl": "Wyżywienie lub dopłaty?", "ua": "Харчування або доплати?", "ru": "Питание или доплаты?", "en": "Meals or allowance?", "de": "Verpflegung oder Zuschüsse?", "es": "Comidas o ayudas?", "pt": "Refeições ou subsídio?"}),
    ("Starting_date", {"pl": "Planowana data startu?", "ua": "Планована дата старту?", "ru": "Планируемая дата старта?", "en": "Starting date?", "de": "Startdatum?", "es": "Fecha de inicio?", "pt": "Data de início?"}),
    ("Phone", "phone"),
]


MODULE_FIELDS = {
    "legalization": [
        ("Topic", {"pl": "Jaki temat legalizacji?", "ua": "Яка тема легалізації?", "ru": "Какая тема легализации?", "en": "Which legalization topic?", "de": "Welches Legalisierungsthema?", "es": "¿Qué tema de legalización?", "pt": "Qual tema de legalização?"}),
        ("Description", {"pl": "Opisz sytuację krótko.", "ua": "Коротко опишіть ситуацію.", "ru": "Кратко опишите ситуацию.", "en": "Briefly describe the situation.", "de": "Beschreiben Sie kurz die Situation.", "es": "Describa brevemente la situación.", "pt": "Descreva brevemente a situação."}),
        ("Phone", "phone"),
    ],
    "relocation": [("Destination", {"pl": "Do jakiego kraju planujesz wyjazd?", "ua": "До якої країни плануєте переїзд?", "ru": "В какую страну планируете переезд?", "en": "Which destination country?", "de": "Welches Zielland?", "es": "¿País de destino?", "pt": "País de destino?"}), ("Description", {"pl": "W czym dokładnie mamy pomóc?", "ua": "З чим саме допомогти?", "ru": "С чем именно помочь?", "en": "What exactly should EWU help with?", "de": "Wobei soll EWU helfen?", "es": "¿En qué debe ayudar EWU?", "pt": "Em que deve a EWU ajudar?"}), ("Phone", "phone")],
    "family": [("Family_need", {"pl": "Jaka sprawa rodzinna: szkoła, przedszkole, adaptacja?", "ua": "Яке сімейне питання: школа, садок, адаптація?", "ru": "Какой семейный вопрос: школа, сад, адаптация?", "en": "Family topic: school, kindergarten, adaptation?", "de": "Familienthema: Schule, Kindergarten, Integration?", "es": "Tema familiar: escuela, guardería, adaptación?", "pt": "Tema familiar: escola, jardim, adaptação?"}), ("Description", {"pl": "Opisz potrzeby rodziny.", "ua": "Опишіть потреби родини.", "ru": "Опишите потребности семьи.", "en": "Describe your family needs.", "de": "Beschreiben Sie den Bedarf der Familie.", "es": "Describa las necesidades familiares.", "pt": "Descreva as necessidades familiares."}), ("Phone", "phone")],
    "business": [("Business_topic", {"pl": "Jaki temat biznesowy?", "ua": "Яка бізнес-тема?", "ru": "Какая бизнес-тема?", "en": "Which business topic?", "de": "Welches Business-Thema?", "es": "¿Qué tema de negocio?", "pt": "Que tema de negócio?"}), ("Description", {"pl": "Opisz plan lub pytanie.", "ua": "Опишіть план або питання.", "ru": "Опишите план или вопрос.", "en": "Describe your plan or question.", "de": "Beschreiben Sie Plan oder Frage.", "es": "Describa su plan o pregunta.", "pt": "Descreva o plano ou questão."}), ("Phone", "phone")],
    "help": [("Description", {"pl": "W czym potrzebujesz wsparcia EWU?", "ua": "У чому потрібна підтримка EWU?", "ru": "В чём нужна поддержка EWU?", "en": "What EWU support do you need?", "de": "Welche EWU Unterstützung benötigen Sie?", "es": "¿Qué soporte EWU necesita?", "pt": "Que suporte EWU precisa?"}), ("Phone", "phone")],
    "education": [("Training_topic", {"pl": "Jaki kurs lub rozwój Cię interesuje?", "ua": "Який курс або розвиток цікавить?", "ru": "Какой курс или развитие интересует?", "en": "Which course or development topic interests you?", "de": "Welcher Kurs interessiert Sie?", "es": "¿Qué curso le interesa?", "pt": "Que curso lhe interessa?"}), ("Phone", "phone")],
    "protection": [("Concern", {"pl": "Opisz problem: wynagrodzenie, zakwaterowanie, konflikt lub oszustwo.", "ua": "Опишіть проблему: зарплата, житло, конфлікт або шахрайство.", "ru": "Опишите проблему: зарплата, жильё, конфликт или мошенничество.", "en": "Describe the concern: salary, accommodation, conflict or suspected fraud.", "de": "Beschreiben Sie das Problem: Lohn, Unterkunft, Konflikt oder Betrugsverdacht.", "es": "Describa el problema: salario, alojamiento, conflicto o fraude.", "pt": "Descreva o problema: salário, alojamento, conflito ou fraude."}), ("Phone", "phone")],
    "membership": [("Membership_Status", {"pl": "Jaki typ członkostwa: free, paid czy hybrid?", "ua": "Який тип членства: free, paid чи hybrid?", "ru": "Какой тип членства: free, paid или hybrid?", "en": "Membership type: free, paid or hybrid?", "de": "Mitgliedschaft: free, paid oder hybrid?", "es": "Membresía: free, paid o hybrid?", "pt": "Adesão: free, paid ou hybrid?"}), ("Phone", "phone")],
    "referral": [("Referring_member", {"pl": "Kto poleca kandydata?", "ua": "Хто рекомендує кандидата?", "ru": "Кто рекомендует кандидата?", "en": "Who is referring the candidate?", "de": "Wer empfiehlt den Kandidaten?", "es": "¿Quién recomienda al candidato?", "pt": "Quem recomenda o candidato?"}), ("Referred_worker", {"pl": "Kogo polecasz?", "ua": "Кого рекомендуєте?", "ru": "Кого рекомендуете?", "en": "Who is the referred worker?", "de": "Wer ist der empfohlene Arbeiter?", "es": "¿A quién recomienda?", "pt": "Quem está a recomendar?"}), ("Phone", "phone")],
}


def q(lang, question):
    if question == "phone":
        return t(lang, "phone")
    return question.get(lang) or question.get("en") or next(iter(question.values()))


def state(uid):
    if uid not in USERS:
        USERS[uid] = {
            "lang": DEFAULT_LANG if DEFAULT_LANG else "pl",
            "role": "",
            "data": {},
            "messages": [],
            "photo_path": "",
            "production_photos": [],
            "accommodation_photos": [],
            "photo_mode": "",
            "awaiting_candidate_photo": False,
            "awaiting_employer_photos": False,
            "asked_fields": [],
            "last_asked_field": "",
            "completed": False,
        }
    return USERS[uid]


def norm_phone(raw):
    phone = re.sub(r"[^\d+]", "", raw or "")
    if phone.startswith("00"):
        phone = "+" + phone[2:]
    if phone.startswith("48") and not phone.startswith("+"):
        phone = "+" + phone
    return phone


def find_phone(text):
    match = PHONE_RE.search(text or "")
    return norm_phone(match.group(1)) if match else ""


def safe_send(chat_id, text, **kwargs):
    for attempt in range(1, 4):
        try:
            return bot.send_message(chat_id, text, **kwargs)
        except Exception as exc:
            log_error("telegram_send", exc)
            time.sleep(attempt)
    return None


def safe_answer_callback(callback):
    try:
        bot.answer_callback_query(callback.id)
    except Exception as exc:
        log_error("telegram_callback", exc)


def send_start(chat_id, lang):
    if BANNER_FILE and os.path.exists(BANNER_FILE):
        try:
            with open(BANNER_FILE, "rb") as f:
                bot.send_photo(chat_id, f, caption=t(lang, "start"), reply_markup=role_keyboard(lang))
                return
        except Exception as exc:
            log_error("banner", exc)
    safe_send(chat_id, t(lang, "start"), reply_markup=role_keyboard(lang))


def fields_for(role):
    if role == "candidate":
        return CANDIDATE_FIELDS
    if role == "employer":
        return EMPLOYER_FIELDS
    return MODULE_FIELDS.get(role, [])


def missing_field(user):
    for field, question in fields_for(user["role"]):
        if not str(user["data"].get(field, "")).strip():
            return field, question
    return None, None


def remember_asked_field(user, field):
    asked = user.setdefault("asked_fields", [])
    if field and field not in asked:
        asked.append(field)
    user["last_asked_field"] = field or ""


def ask_next(message, user):
    field, question = missing_field(user)
    if field:
        remember_asked_field(user, field)
        text = ai_next_turn(user["lang"], user["role"], user, "", q(user["lang"], question), field)
        if question == "phone":
            safe_send(message.chat.id, text, reply_markup=contact_keyboard(user["lang"]))
        else:
            safe_send(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())
        return

    if user["role"] == "candidate" and not user.get("awaiting_candidate_photo") and not user.get("completed"):
        user["awaiting_candidate_photo"] = True
        safe_send(message.chat.id, t(user["lang"], "photo_explain"))
        safe_send(message.chat.id, f"{t(user['lang'], 'send_photo')}\n{t(user['lang'], 'skip_photo')}", reply_markup=types.ReplyKeyboardRemove())
        return

    if user["role"] == "employer" and not user.get("awaiting_employer_photos") and not user.get("completed"):
        user["awaiting_employer_photos"] = True
        safe_send(message.chat.id, t(user["lang"], "prod_photo"), reply_markup=yes_no_keyboard(user["lang"], "prodphoto"))
        return

    finalize(message, user)


def reply_and_ask_next(message, user, user_text):
    field, question = missing_field(user)
    if field:
        remember_asked_field(user, field)
        next_question = q(user["lang"], question)
        text = ai_next_turn(user["lang"], user["role"], user, user_text, next_question, field)
        markup = contact_keyboard(user["lang"]) if question == "phone" else types.ReplyKeyboardRemove()
        safe_send(message.chat.id, text, reply_markup=markup)
        return

    if user_text:
        safe_send(message.chat.id, ai_reply(user["lang"], user["role"], user, user_text), reply_markup=types.ReplyKeyboardRemove())
    ask_next(message, user)


def full_name(data):
    name = " ".join([data.get("First_Name", ""), data.get("Last_Name", "")]).strip()
    return data.get("Full_Name") or name or data.get("Company", "") or data.get("Name", "")


def persist_record(user):
    role = user["role"]
    folder = "Employers" if role == "employer" else "Candidates" if role == "candidate" else "Backups"
    path = os.path.join(EWU_DATA_DIR, folder, f"{user['data'].get('EWU_ID', 'EWU')}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(user["data"], f, ensure_ascii=False, indent=2)


def finalize_qualification(message, user):
    q_data, report = qualification.report(user)
    data = user.setdefault("data", {})
    data.update(q_data)
    data.update({
        "Language": user["lang"],
        "Telegram_ID": data.get("Telegram_ID") or (message.from_user.id if message.from_user else ""),
        "Telegram": data.get("Telegram") or (message.from_user.username if message.from_user else ""),
        "Type": "qualification",
        "Source": "Telegram",
        "Current_Status": "Qualification Completed",
        "AI_Summary": f"Qualification score: {q_data.get('Qualification_Score')}/100. Level: {q_data.get('Qualification_Level')}. PL salary: {q_data.get('Salary_PL')}. DE salary: {q_data.get('Salary_DE')}.",
    })
    if not data.get("EWU_ID"):
        data["EWU_ID"] = new_case_id("qualification")
    name = full_name(data) or "Qualification lead"
    send_crm("upsert", "EWU Leads", {
        "Date": datetime.now(timezone.utc).isoformat(),
        "EWU_ID": data["EWU_ID"],
        "Type": "qualification",
        "Name": name,
        "Language": user["lang"],
        "Phone": data.get("Phone", ""),
        "Source": "Telegram",
        "Status": "Qualification Completed",
        "Comment": data.get("AI_Summary", ""),
    })
    send_crm("upsert", "EWU Operations", data)
    persist_record(user)
    operations(bot, f"EWU Qualification completed\nID: {data['EWU_ID']}\nName: {name}\nPhone: {data.get('Phone', '')}\nScore: {q_data.get('Qualification_Score')}/100", None, data["EWU_ID"])
    leads(bot, f"EWU qualification lead: {data['EWU_ID']} - {q_data.get('Qualification_Score')}/100")
    user["completed"] = True
    user.setdefault("qualification", {})["done"] = True
    safe_send(message.chat.id, report, reply_markup=types.ReplyKeyboardRemove())


def finalize(message, user):
    if user.get("completed"):
        return
    role = user["role"]
    data = user["data"]
    lang = user["lang"]

    if not data.get("EWU_ID"):
        if role == "candidate":
            data["EWU_ID"] = new_candidate_id()
        elif role == "employer":
            data["EWU_ID"] = new_employer_id()
        else:
            data["EWU_ID"] = new_case_id(role)

    if role == "candidate":
        data["Full_Name"] = full_name(data)
    data.update({
        "Language": lang,
        "Telegram_ID": data.get("Telegram_ID") or (message.from_user.id if message.from_user else ""),
        "Telegram": data.get("Telegram") or (message.from_user.username if message.from_user else ""),
        "Type": role,
        "Source": "Telegram",
        "Current_Status": "Application Completed",
        "AI_Summary": ai_summary(lang, role, data, user["messages"]),
    })

    if role == "membership":
        data.setdefault("Membership_Status", "free")
    if role == "referral":
        data.setdefault("Referral_Status", "New")
        data.setdefault("Reward_Eligibility", "Pending")

    name = full_name(data) or role.title()
    lead = {
        "Date": datetime.now(timezone.utc).isoformat(),
        "EWU_ID": data["EWU_ID"],
        "Type": role,
        "Name": name,
        "Language": lang,
        "Phone": data.get("Phone", ""),
        "Source": "Telegram",
        "Status": "New Lead",
        "Comment": data.get("AI_Summary", ""),
    }
    pipeline = {
        "EWU_ID": data["EWU_ID"],
        "Current_stage": "Application Completed",
        "Transition_date": datetime.now(timezone.utc).isoformat(),
        "Responsible_manager": "",
        "Next_step": "Coordinator follow-up",
        "Deadline": "",
    }

    send_crm("upsert", "EWU Leads", lead)
    send_crm("upsert", "EWU Operations", data)
    send_crm("pipeline", "Pipeline", pipeline)
    persist_record(user)

    pdf = None
    if role == "candidate":
        pdf = make_candidate_pdf(data, user.get("photo_path"))
    elif role == "employer":
        pdf = make_vacancy_pdf(data, user.get("production_photos", []), user.get("accommodation_photos", []))

    note = (
        f"New EWU lead\n"
        f"ID: {data['EWU_ID']}\nType: {role}\nName: {name}\n"
        f"Phone: {data.get('Phone', '')}\n\n{data.get('AI_Summary', '')}"
    )
    operations(bot, note, pdf, data["EWU_ID"])
    leads(bot, f"EWU new {role} lead: {data['EWU_ID']} - {name}")

    user["completed"] = True
    safe_send(message.chat.id, t(lang, "saved").format(id=data["EWU_ID"]), reply_markup=types.ReplyKeyboardRemove())


def start_role(callback, role):
    user = state(callback.from_user.id)
    if role == "language":
        safe_send(callback.message.chat.id, t(user["lang"], "choose_lang"), reply_markup=lang_keyboard(user["lang"]))
        return
    if role == "qualification":
        user.update({
            "role": "qualification",
            "messages": [],
            "photo_path": "",
            "production_photos": [],
            "accommodation_photos": [],
            "photo_mode": "",
            "awaiting_candidate_photo": False,
            "awaiting_employer_photos": False,
            "asked_fields": [],
            "last_asked_field": "",
            "completed": False,
        })
        user["data"] = {
            "EWU_ID": new_case_id("qualification"),
            "Language": user["lang"],
            "Telegram_ID": callback.from_user.id,
            "Telegram": callback.from_user.username or "",
            "Source": "Telegram",
            "Type": "qualification",
        }
        user.pop("qualification", None)
        qualification.begin(callback.message, user, safe_send, contact_keyboard)
        return

    user.update({
        "role": role,
        "messages": [],
        "photo_path": "",
        "production_photos": [],
        "accommodation_photos": [],
        "photo_mode": "",
        "awaiting_candidate_photo": False,
        "awaiting_employer_photos": False,
        "asked_fields": [],
        "last_asked_field": "",
        "completed": False,
    })
    if role == "candidate":
        eid = new_candidate_id()
    elif role == "employer":
        eid = new_employer_id()
    else:
        eid = new_case_id(role)
    user["data"] = {
        "EWU_ID": eid,
        "Language": user["lang"],
        "Telegram_ID": callback.from_user.id,
        "Telegram": callback.from_user.username or "",
        "Source": "Telegram",
        "Type": role,
    }
    ask_next(callback.message, user)


def is_admin(uid):
    return ADMIN_CHAT_ID and str(uid) == str(ADMIN_CHAT_ID)


@bot.message_handler(commands=["start"])
def start(message):
    user = state(message.from_user.id)
    telegram_lang = normalize_lang(getattr(message.from_user, "language_code", ""), DEFAULT_LANG or "pl")
    user.update({
        "lang": telegram_lang,
        "role": "",
        "data": {},
        "messages": [],
        "photo_path": "",
        "production_photos": [],
        "accommodation_photos": [],
        "photo_mode": "",
        "awaiting_candidate_photo": False,
        "awaiting_employer_photos": False,
        "asked_fields": [],
        "last_asked_field": "",
        "completed": False,
    })
    user.pop("qualification", None)
    send_start(message.chat.id, user["lang"])


@bot.message_handler(commands=["admin"])
def admin(message):
    if not is_admin(message.from_user.id):
        safe_send(message.chat.id, t(state(message.from_user.id)["lang"], "not_authorized"))
        return
    safe_send(message.chat.id, t(state(message.from_user.id)["lang"], "admin"), reply_markup=admin_keyboard())


@bot.message_handler(commands=["feedback"])
def feedback(message):
    user = state(message.from_user.id)
    text = message.text.split(maxsplit=1)
    if len(text) < 2 or not text[1].strip():
        safe_send(message.chat.id, "Напишите так: /feedback что нужно улучшить")
        return
    save_feedback(message.from_user.id, user["lang"], user.get("role", ""), text[1].strip(), user.get("data", {}))
    send_crm("upsert", "EWU Backup", {
        "Table": "Feedback",
        "Payload": text[1].strip(),
        "EWU_ID": user.get("data", {}).get("EWU_ID", ""),
    })
    safe_send(message.chat.id, "Спасибо. Я передал обратную связь в память EWU.")


@bot.message_handler(commands=["learn"])
def learn(message):
    if not is_admin(message.from_user.id):
        safe_send(message.chat.id, t(state(message.from_user.id)["lang"], "not_authorized"))
        return
    text = message.text.split(maxsplit=1)
    if len(text) < 2 or not text[1].strip():
        safe_send(message.chat.id, "Usage: /learn approved EWU rule or correction")
        return
    save_learning_note(message.from_user.id, text[1].strip())
    safe_send(message.chat.id, "Saved to approved EWU learning notes.")


@bot.message_handler(commands=["find"])
def find_record(message):
    if not is_admin(message.from_user.id):
        safe_send(message.chat.id, t(state(message.from_user.id)["lang"], "not_authorized"))
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        safe_send(message.chat.id, "Usage: /find EWU_ID")
        return
    eid = parts[1].strip()
    for folder in ["Candidates", "Employers", "Backups"]:
        path = os.path.join(EWU_DATA_DIR, folder, f"{eid}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                safe_send(message.chat.id, f"<pre>{html_escape(f.read()[:3500])}</pre>")
            return
    safe_send(message.chat.id, "Record not found locally.")


@bot.message_handler(commands=["export"])
def export_backup(message):
    if not is_admin(message.from_user.id):
        safe_send(message.chat.id, t(state(message.from_user.id)["lang"], "not_authorized"))
        return
    backups = load_backups(5)
    if backups:
        safe_send(message.chat.id, f"Recent backup records: {len(backups)}")
    backup_file = os.path.join(EWU_DATA_DIR, "Backups", "local_backup_leads.jsonl")
    if os.path.exists(backup_file):
        with open(backup_file, "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        safe_send(message.chat.id, "No local backup file yet.")


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang:"))
def cb_lang(callback):
    safe_answer_callback(callback)
    user = state(callback.from_user.id)
    user["lang"] = callback.data.split(":", 1)[1]
    send_start(callback.message.chat.id, user["lang"])


@bot.callback_query_handler(func=lambda c: c.data.startswith("role:"))
def cb_role(callback):
    safe_answer_callback(callback)
    start_role(callback, callback.data.split(":", 1)[1])


@bot.callback_query_handler(func=lambda c: c.data.startswith("status:"))
def cb_status(callback):
    safe_answer_callback(callback)
    if not is_admin(callback.from_user.id):
        safe_send(callback.message.chat.id, "Only admin can change statuses.")
        return
    _, eid, status = callback.data.split(":", 2)
    ok, info = update_status(eid, status, str(callback.from_user.id))
    safe_send(callback.message.chat.id, "Status updated." if ok else f"Status update failed: {info}")


@bot.callback_query_handler(func=lambda c: c.data.startswith("prodphoto:") or c.data.startswith("accomphoto:"))
def cb_photos(callback):
    safe_answer_callback(callback)
    user = state(callback.from_user.id)
    prefix, value = callback.data.split(":", 1)
    if prefix == "prodphoto":
        if value == "yes":
            user["photo_mode"] = "production"
            safe_send(callback.message.chat.id, t(user["lang"], "send_photos"))
        else:
            user["photo_mode"] = ""
            safe_send(callback.message.chat.id, t(user["lang"], "acc_photo"), reply_markup=yes_no_keyboard(user["lang"], "accomphoto"))
    elif prefix == "accomphoto":
        if value == "yes":
            user["photo_mode"] = "accommodation"
            safe_send(callback.message.chat.id, t(user["lang"], "send_photos"))
        else:
            user["photo_mode"] = ""
            finalize(callback.message, user)


@bot.callback_query_handler(func=lambda c: c.data.startswith("admin:"))
def cb_admin(callback):
    safe_answer_callback(callback)
    if not is_admin(callback.from_user.id):
        safe_send(callback.message.chat.id, "Only admin.")
        return
    safe_send(callback.message.chat.id, "Use /find EWU_ID to search or /export to download local backups.")


@bot.message_handler(content_types=["contact"])
def contact(message):
    user = state(message.from_user.id)
    if not user.get("role"):
        user["lang"] = normalize_lang(getattr(message.from_user, "language_code", ""), user.get("lang", DEFAULT_LANG or "pl"))
        safe_send(message.chat.id, t(user["lang"], "start"), reply_markup=role_keyboard(user["lang"]))
        return
    phone = norm_phone(message.contact.phone_number if message.contact else "")
    if phone:
        user["data"]["Phone"] = phone
        if user.get("role") == "qualification" and user.get("qualification"):
            user["qualification"]["data"]["Phone"] = phone
            if not qualification.ask_next(message, user, safe_send, contact_keyboard):
                finalize_qualification(message, user)
            return
    ask_next(message, user)


@bot.message_handler(content_types=["photo"])
def photo(message):
    user = state(message.from_user.id)
    if not user.get("role"):
        user["lang"] = normalize_lang(getattr(message.from_user, "language_code", ""), user.get("lang", DEFAULT_LANG or "pl"))
        safe_send(message.chat.id, t(user["lang"], "start"), reply_markup=role_keyboard(user["lang"]))
        return
    ensure_dirs()
    try:
        info = bot.get_file(message.photo[-1].file_id)
        content = bot.download_file(info.file_path)
        eid = user["data"].get("EWU_ID", "photo")
        path = os.path.join(EWU_DATA_DIR, "Photos", f"{eid}_{message.photo[-1].file_id}.jpg")
        with open(path, "wb") as f:
            f.write(content)
        if user.get("role") == "qualification" and user.get("qualification"):
            qualification.handle_photo(message, user, path, safe_send)
            return
        if user.get("photo_mode") == "production":
            user["production_photos"].append(path)
            user["data"]["Production_Photos"] = ";".join(user["production_photos"])
        elif user.get("photo_mode") == "accommodation":
            user["accommodation_photos"].append(path)
            user["data"]["Accommodation_Photos"] = ";".join(user["accommodation_photos"])
        else:
            user["photo_path"] = path
            user["data"]["Photo"] = path
            user["awaiting_candidate_photo"] = False
            safe_send(message.chat.id, t(user["lang"], "photo_ok"))
            if user["role"] == "candidate":
                finalize(message, user)
                return
        safe_send(message.chat.id, t(user["lang"], "photo_ok"))
    except Exception as exc:
        log_error("photo", exc)
        safe_send(message.chat.id, "Photo could not be saved. Please try again.")


@bot.message_handler(func=lambda m: True)
def dialog(message):
    user = state(message.from_user.id)
    text = message.text or ""
    clean = text.strip()
    low = clean.lower()

    if not user.get("role"):
        user["lang"] = detect_lang(clean)
        send_start(message.chat.id, user["lang"])
        return

    if user.get("completed"):
        user["lang"] = detect_lang(clean) if clean else user["lang"]
        safe_send(message.chat.id, t(user["lang"], "start"), reply_markup=role_keyboard(user["lang"]))
        return

    if low in OK_WORDS:
        if user.get("awaiting_candidate_photo"):
            user["awaiting_candidate_photo"] = False
            finalize(message, user)
            return
        if user.get("photo_mode") == "production":
            user["photo_mode"] = ""
            safe_send(message.chat.id, t(user["lang"], "acc_photo"), reply_markup=yes_no_keyboard(user["lang"], "accomphoto"))
            return
        if user.get("photo_mode") == "accommodation":
            user["photo_mode"] = ""
            finalize(message, user)
            return

    if user.get("role") == "qualification" and user.get("qualification"):
        _, q_field, _ = qualification.current_missing(user)
        if q_field == "Phone":
            phone = find_phone(clean)
            if not phone:
                safe_send(message.chat.id, "Укажите телефон или отправьте контакт.", reply_markup=contact_keyboard(user["lang"]))
                return
            user["data"]["Phone"] = phone
            clean = phone
        asked_next = qualification.handle_text(message, user, clean, safe_send, contact_keyboard)
        if not asked_next:
            finalize_qualification(message, user)
        return

    field, question = missing_field(user)
    if field == "Phone":
        phone = find_phone(clean)
        if not phone:
            safe_send(message.chat.id, q(user["lang"], question), reply_markup=contact_keyboard(user["lang"]))
            return
        user["data"]["Phone"] = phone
    elif field:
        for key, value in extract(clean, user["role"]).items():
            user["data"].setdefault(key, value)
        user["data"][field] = clean
    user["messages"].append({"user": clean})
    reply_and_ask_next(message, user, clean)


if __name__ == "__main__":
    ensure_dirs()
    print("EWU AI Coordinator 4.0 started", flush=True)
    run_polling_forever()
