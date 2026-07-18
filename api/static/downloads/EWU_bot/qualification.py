from telebot import types


QUAL_FIELDS = [
    ("Profession", {
        "pl": "Jaka jest Twoja specjalizacja?\n\n1. Spawacz MIG/MAG\n2. TIG\n3. Monter\n4. Slusarz\n5. Elektryk\n6. CNC\n7. Inna specjalizacja",
        "ua": "Яка у вас спеціальність?\n\n1. Зварювальник MIG/MAG\n2. TIG\n3. Монтажник\n4. Слюсар\n5. Електрик\n6. CNC\n7. Інша спеціальність",
        "ru": "Какая у вас специальность?\n\n1. Сварщик MIG/MAG\n2. TIG\n3. Монтажник\n4. Слесарь\n5. Электрик\n6. CNC\n7. Другая специальность",
        "en": "What is your profession?\n\n1. MIG/MAG welder\n2. TIG\n3. Fitter\n4. Locksmith\n5. Electrician\n6. CNC\n7. Other profession",
    }),
    ("Experience", {
        "pl": "Jakie masz doswiadczenie?\n\n1. Do 1 roku\n2. 1-3 lata\n3. 3-5 lat\n4. Ponad 5 lat",
        "ua": "Який у вас досвід?\n\n1. До 1 року\n2. 1-3 роки\n3. 3-5 років\n4. Понад 5 років",
        "ru": "Какой у вас опыт?\n\n1. До 1 года\n2. 1-3 года\n3. 3-5 лет\n4. Более 5 лет",
        "en": "What is your experience?\n\n1. Up to 1 year\n2. 1-3 years\n3. 3-5 years\n4. More than 5 years",
    }),
    ("Countries", {
        "pl": "W jakich krajach masz doswiadczenie?\n\n1. Ukraina\n2. Polska\n3. Niemcy\n4. Inne kraje UE",
        "ua": "У яких країнах у вас був досвід роботи?\n\n1. Україна\n2. Польща\n3. Німеччина\n4. Інші країни ЄС",
        "ru": "В каких странах у вас был опыт работы?\n\n1. Украина\n2. Польша\n3. Германия\n4. Другие страны ЕС",
        "en": "In which countries do you have work experience?\n\n1. Ukraine\n2. Poland\n3. Germany\n4. Other EU countries",
    }),
    ("Drawings", {
        "pl": "Czy umiesz czytac rysunek techniczny?\n\n1. Tak\n2. Czesciowo\n3. Nie",
        "ua": "Чи вмієте читати технічні креслення?\n\n1. Так\n2. Частково\n3. Ні",
        "ru": "Умеете ли вы читать технические чертежи?\n\n1. Да\n2. Частично\n3. Нет",
        "en": "Can you read technical drawings?\n\n1. Yes\n2. Partly\n3. No",
    }),
    ("Certificates", {
        "pl": "Czy masz certyfikaty?\n\n1. ISO\n2. TÜV\n3. UDT\n4. Inne\n5. Nie",
        "ua": "Чи є сертифікати?\n\n1. ISO\n2. TÜV\n3. UDT\n4. Інші\n5. Ні",
        "ru": "Есть ли сертификаты?\n\n1. ISO\n2. TÜV\n3. UDT\n4. Другие\n5. Нет",
        "en": "Do you have certificates?\n\n1. ISO\n2. TÜV\n3. UDT\n4. Other\n5. No",
    }),
    ("Certificate_Document", {
        "pl": "Aby zaliczyc certyfikat do oceny, wyslij zdjecie lub skan dokumentu. Jesli nie masz go teraz, napisz OK.",
        "ua": "Щоб зарахувати сертифікат в оцінку, надішліть фото або скан документа. Якщо зараз немає, напишіть OK.",
        "ru": "Чтобы засчитать сертификат в оценку, отправьте фото или скан документа. Если сейчас его нет, напишите OK.",
        "en": "To count the certificate in the score, send a photo or scan of the document. If you do not have it now, write OK.",
    }),
    ("Work_Photos", {
        "pl": "Mozesz wyslac zdjecia spoin lub wykonanych prac. Jesli chcesz pominac, napisz OK.",
        "ua": "Можете надіслати фото швів або виконаних робіт. Якщо хочете пропустити, напишіть OK.",
        "ru": "Можете отправить фото сварочных швов или выполненных работ. Если хотите пропустить, напишите OK.",
        "en": "You can send photos of welds or completed work. If you want to skip, write OK.",
    }),
    ("Travel", {
        "pl": "Jaka gotowosc do wyjazdow?\n\n1. Tylko Polska\n2. Polska i Niemcy\n3. Cala Europa",
        "ua": "Яка готовність до відряджень?\n\n1. Тільки Польща\n2. Польща і Німеччина\n3. Вся Європа",
        "ru": "Какая готовность к командировкам?\n\n1. Только Польша\n2. Польша и Германия\n3. Вся Европа",
        "en": "What is your travel readiness?\n\n1. Poland only\n2. Poland and Germany\n3. All Europe",
    }),
    ("Phone", "phone"),
]


START_TEXT = {
    "pl": "Szybko ocenimy Twoj poziom zawodowy. To zajmie okolo 2 minut i pomoze zrozumiec realny poziom wynagrodzenia.",
    "ua": "Давайте швидко оцінимо ваш професійний рівень. Це займе близько 2 хвилин і допоможе зрозуміти реальний рівень зарплати.",
    "ru": "Давайте быстро оценим ваш профессиональный уровень. Это займет около 2 минут и поможет понять ваш реальный уровень зарплаты.",
    "en": "Let us quickly assess your professional level. It takes about 2 minutes and helps estimate your realistic salary level.",
}


def text(lang, payload):
    if payload == "phone":
        return {
            "pl": "Podaj numer telefonu lub udostepnij kontakt.",
            "ua": "Вкажіть телефон або поділіться контактом.",
            "ru": "Укажите телефон или отправьте контакт.",
            "en": "Share your phone number or contact.",
        }.get(lang, "Share your phone number or contact.")
    return payload.get(lang) or payload.get("en") or payload.get("ru") or next(iter(payload.values()))


def certificate_claimed(data):
    cert = (data.get("Certificates") or "").strip().lower()
    return bool(cert) and cert not in {"5", "no", "нет", "nie", "ні", "none"}


def seed_from_candidate(data):
    seeded = {}
    if data.get("Profession"):
        seeded["Profession"] = data["Profession"]
    if data.get("Experience"):
        seeded["Experience"] = data["Experience"]
    if data.get("Countries_worked_in"):
        seeded["Countries"] = data["Countries_worked_in"]
    elif data.get("Current_country"):
        seeded["Countries"] = data["Current_country"]
    if data.get("Certificates"):
        seeded["Certificates"] = data["Certificates"]
    if data.get("Travel_ready"):
        seeded["Travel"] = data["Travel_ready"]
    if data.get("Phone"):
        seeded["Phone"] = data["Phone"]
    return seeded


def begin(message, user, safe_send, contact_keyboard):
    user["qualification"] = {
        "step": 0,
        "data": seed_from_candidate(user.get("data", {})),
        "photos": [],
        "certificate_photos": [],
        "work_photos": [],
        "done": False,
    }
    safe_send(message.chat.id, text(user["lang"], START_TEXT))
    ask_next(message, user, safe_send, contact_keyboard)


def current_missing(user):
    data = user.get("qualification", {}).get("data", {})
    for idx, (field, question) in enumerate(QUAL_FIELDS):
        if field == "Certificate_Document" and not certificate_claimed(data):
            continue
        if not str(data.get(field, "")).strip():
            return idx, field, question
    return None, None, None


def ask_next(message, user, safe_send, contact_keyboard):
    idx, field, question = current_missing(user)
    if field is None:
        return False
    user["qualification"]["step"] = idx
    if question == "phone":
        safe_send(message.chat.id, text(user["lang"], question), reply_markup=contact_keyboard(user["lang"]))
    else:
        safe_send(message.chat.id, text(user["lang"], question), reply_markup=types.ReplyKeyboardRemove())
    return True


def normalize(field, value):
    raw = (value or "").strip()
    low = raw.lower()
    maps = {
        "Profession": {"1": "MIG/MAG Welder", "2": "TIG Welder", "3": "Fitter", "4": "Locksmith", "5": "Electrician", "6": "CNC", "7": raw or "Other"},
        "Experience": {"1": "Up to 1 year", "2": "1-3 years", "3": "3-5 years", "4": "More than 5 years"},
        "Countries": {"1": "Ukraine", "2": "Poland", "3": "Germany", "4": "Other EU countries"},
        "Drawings": {"1": "Yes", "2": "Partly", "3": "No"},
        "Certificates": {"1": "ISO", "2": "TÜV", "3": "UDT", "4": "Other", "5": "No"},
        "Travel": {"1": "Poland only", "2": "Poland and Germany", "3": "All Europe"},
    }
    return maps.get(field, {}).get(low, raw)


def handle_text(message, user, clean, safe_send, contact_keyboard):
    q = user.setdefault("qualification", {"step": 0, "data": {}, "photos": [], "certificate_photos": [], "work_photos": [], "done": False})
    _, field, _ = current_missing(user)
    if field is None:
        return False
    if field == "Certificate_Document":
        q["data"]["Certificate_Document"] = "Not provided"
        q["data"]["Certificate_Document_Verified"] = "No"
    elif field == "Work_Photos":
        q["data"]["Work_Photos"] = "Yes" if q.get("work_photos") else "No"
    elif field == "Phone":
        q["data"]["Phone"] = clean
    else:
        q["data"][field] = normalize(field, clean)
        if field == "Certificates" and not certificate_claimed(q["data"]):
            q["data"]["Certificate_Document"] = "Not required"
            q["data"]["Certificate_Document_Verified"] = "No"
    return ask_next(message, user, safe_send, contact_keyboard)


def handle_photo(message, user, path, safe_send):
    q = user.setdefault("qualification", {"step": 0, "data": {}, "photos": [], "certificate_photos": [], "work_photos": [], "done": False})
    _, field, _ = current_missing(user)
    q.setdefault("photos", []).append(path)
    if field == "Certificate_Document":
        q.setdefault("certificate_photos", []).append(path)
        q["data"]["Certificate_Document"] = path
        q["data"]["Certificate_Document_Verified"] = "Yes"
        q["data"]["Certificate_Document_Photos"] = ";".join(q["certificate_photos"])
        msg = {
            "pl": "Dokument zapisany. Certyfikat zostanie zaliczony do oceny.",
            "ua": "Документ збережено. Сертифікат буде врахований в оцінці.",
            "ru": "Документ сохранён. Сертификат будет учтён в оценке.",
            "en": "Document saved. The certificate will be counted in the score.",
        }
    else:
        q.setdefault("work_photos", []).append(path)
        q["data"]["Work_Photos"] = "Yes"
        q["data"]["Work_Photo_Files"] = ";".join(q["work_photos"])
        msg = {
            "pl": "Zdjecie pracy zapisane. Mozesz wyslac kolejne albo napisac OK.",
            "ua": "Фото роботи збережено. Можете надіслати ще або написати OK.",
            "ru": "Фото работы сохранено. Можно отправить ещё или написать OK.",
            "en": "Work photo saved. You can send more or write OK.",
        }
    safe_send(message.chat.id, msg.get(user["lang"], msg["en"]))


def score(data):
    points = 0
    exp = data.get("Experience", "").lower()
    if "more than 5" in exp or "более 5" in exp or "ponad 5" in exp:
        points += 25
    elif "3-5" in exp:
        points += 18
    elif "1-3" in exp:
        points += 12
    elif exp:
        points += 5

    drawings = data.get("Drawings", "")
    if drawings == "Yes" or drawings.lower() in {"да", "tak", "так"}:
        points += 20
    elif drawings == "Partly" or "част" in drawings.lower() or "cz" in drawings.lower():
        points += 10

    if data.get("Certificate_Document_Verified") == "Yes":
        points += 20

    if data.get("Work_Photos") == "Yes":
        points += 15

    countries = data.get("Countries", "").lower()
    if any(x in countries for x in ["poland", "germany", "eu", "польш", "герман", "ес", "polska", "niemcy", "ue"]):
        points += 10

    travel = data.get("Travel", "").lower()
    if "all europe" in travel or "вся европ" in travel or "cala europa" in travel:
        points += 10
    elif "germany" in travel or "герман" in travel or "niemcy" in travel:
        points += 7
    elif travel:
        points += 4
    return min(points, 100)


def level(points):
    if points >= 85:
        return "Премиум специалист"
    if points >= 71:
        return "Высокий уровень"
    if points >= 41:
        return "Средний уровень"
    return "Начинающий"


def rating(points):
    stars = 5 if points >= 85 else 4 if points >= 71 else 3 if points >= 41 else 2 if points >= 25 else 1
    return "★" * stars + "☆" * (5 - stars)


def salary(points, profession):
    high_value = any(x in profession.lower() for x in ["cnc", "electric", "tig"])
    if points >= 85:
        return ("9000-13000 zł netto", "3000-4200 € netto") if high_value else ("8500-12000 zł netto", "2800-4000 € netto")
    if points >= 71:
        return "7000-9500 zł netto", "2400-3200 € netto"
    if points >= 41:
        return "5500-7500 zł netto", "1900-2600 € netto"
    return "4200-5800 zł netto", "1500-2100 € netto"


def recommendations(profession):
    p = profession.lower()
    if "tig" in p:
        return ["TIG stainless steel welder", "Pipe welder", "Industrial welder"]
    if "mig" in p or "mag" in p:
        return ["MIG/MAG production welder", "Steel structure welder", "Shipyard welder"]
    if "fitter" in p or "monter" in p:
        return ["Industrial fitter", "Steel structure assembler", "Shipyard fitter"]
    if "locksmith" in p:
        return ["Industrial locksmith", "Assembler", "Maintenance worker"]
    if "electric" in p:
        return ["Industrial electrician", "Maintenance electrician", "Automation support"]
    if "cnc" in p:
        return ["CNC operator", "CNC setter", "Production technician"]
    return ["Industrial worker", "Production specialist", "EWU technical vacancy"]


def report(user):
    data = user.get("qualification", {}).get("data", {})
    points = score(data)
    pl_salary, de_salary = salary(points, data.get("Profession", ""))
    recs = recommendations(data.get("Profession", ""))
    cert_status = "подтверждены фото/сканом" if data.get("Certificate_Document_Verified") == "Yes" else "не подтверждены документом"
    result = {
        "Qualification_Score": points,
        "Qualification_Level": level(points),
        "Qualification_Rating": rating(points),
        "Salary_PL": pl_salary,
        "Salary_DE": de_salary,
        "Certificate_Verification_Status": cert_status,
    }
    data.update(result)
    extra = "\n\nЕсли хотите, EWU может предложить проверку работодателем или техническое собеседование." if points > 80 else ""
    text_report = (
        "📋 <b>EWU Qualification Report</b>\n\n"
        f"Специальность: {data.get('Profession', '')}\n"
        f"Опыт: {data.get('Experience', '')}\n"
        f"Документы квалификации: {cert_status}\n"
        f"Уровень: {result['Qualification_Level']}\n"
        f"Оценка: {points}/100\n\n"
        f"⭐ Рейтинг:\n{result['Qualification_Rating']}\n\n"
        "💰 <b>Ориентировочная зарплата:</b>\n\n"
        f"Польша:\n{pl_salary}\n\n"
        f"Германия:\n{de_salary}\n\n"
        "Рекомендация:\nКандидат подходит для следующих вакансий:\n\n"
        + "\n".join([f"* {item}" for item in recs])
        + extra
    )
    return data, text_report
