from datetime import datetime
import random


def _new(prefix):
    return f"{prefix}-{datetime.now().year}-{random.SystemRandom().randint(1, 99999):05d}"


def new_candidate_id():
    return _new("EWU-PL")


def new_employer_id():
    return _new("EWU-EMP")


def new_case_id(kind="CASE"):
    return _new(f"EWU-{kind.upper()}")
