from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.controllers.rules import AGE_RANGE_YEARS, BLOOD_TYPES, DEFAULT_HOSPITALS, MIN_DONOR_WEIGHT_KG, case_blood_types
from app.models.case import Case
from app.models.hero import Hero
from app.views.stats_view import MetaView, StatsView


def get_stats(db: Session) -> StatsView:
    def count(*where):
        return db.scalar(select(func.count()).select_from(where[0]).where(*where[1:])) or 0

    return StatsView(
        cases_searching=count(Case, Case.status == "searching"),
        heroes_available=count(Hero, Hero.status == "ready"),
        cases_success=count(Case, Case.status == "success"),
    )


def get_meta(db: Session) -> MetaView:
    names = list(DEFAULT_HOSPITALS) + list(db.scalars(select(Case.hospital).distinct()))
    for hospitals in db.scalars(select(Hero.hospitals)):
        names += hospitals
    unique = {" ".join(n.split()).casefold(): " ".join(n.split()) for n in names}
    return MetaView(
        hospitals=sorted(unique.values()),
        hero_blood_types=BLOOD_TYPES,
        case_blood_types={s: case_blood_types(s) for s in BLOOD_TYPES},
        min_donor_weight=MIN_DONOR_WEIGHT_KG,
        age_range={s: list(r) for s, r in AGE_RANGE_YEARS.items()},
    )
