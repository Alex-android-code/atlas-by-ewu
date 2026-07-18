import re


def extract(text, role):
    raw = text or ""
    s = raw.lower()
    data = {}

    email = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", raw)
    if email:
        data["Email"] = email.group(0)

    date = re.search(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b", raw)
    if date:
        data["Date_of_birth"] = date.group(1)

    profession_map = {
        "tig": "TIG Welder",
        "mig": "MIG/MAG Welder",
        "mag": "MIG/MAG Welder",
        "mma": "MMA Welder",
        "pipe": "Pipe Welder",
        "stainless": "Stainless steel welder",
        "aluminium": "Aluminium welder",
        "aluminum": "Aluminium welder",
        "spaw": "Welder",
        "свар": "Welder",
        "звар": "Welder",
        "monter": "Fitter",
        "монтаж": "Fitter",
        "fitter": "Fitter",
        "locksmith": "Locksmith",
        "слес": "Locksmith",
        "ślus": "Locksmith",
        "cnc": "CNC",
        "electric": "Electrician",
        "элект": "Electrician",
        "елект": "Electrician",
    }
    for key, value in profession_map.items():
        if key in s:
            data["Vacancy" if role == "employer" else "Profession"] = value
            break

    if role == "employer":
        qty = re.search(
            r"\b(\d{1,3})\s*(osób|people|workers|pracownik|человек|людей|працівник)",
            s,
        )
        if qty:
            data["Quantity"] = qty.group(1)

    exp = re.search(r"\b(\d{1,2})\s*(lat|рок|лет|years|anos|años|jahre)\b", s)
    if exp:
        data["Experience"] = exp.group(0)

    salary = re.search(r"\b(\d{2,5})\s*(zł|zl|pln|eur|€|usd)\b", s)
    if salary:
        data["Salary"] = salary.group(0)

    for city in ["Gdańsk", "Gdansk", "Berlin", "Warszawa", "Wrocław", "Wroclaw", "Hamburg", "Rotterdam"]:
        if city.lower() in s:
            data["City" if role == "employer" else "Current_city"] = city
            break

    if any(x in s for x in ["prawo jazdy", "водитель", "права", "водій", "driver", "driving licence"]):
        data["Driving_Licence"] = "Yes"

    cats = re.findall(r"\b(CE|DE|A|B|C|D)\b", raw, flags=re.I)
    if cats:
        data["Driving_Categories"] = ", ".join(sorted({c.upper() for c in cats}))

    return data
