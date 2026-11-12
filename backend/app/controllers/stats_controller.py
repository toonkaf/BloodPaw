from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.hero import Hero
from app.views.stats_view import StatsView


def get_stats(db: Session) -> StatsView:
    count = lambda q: db.scalar(q) or 0  # noqa: E731
    return StatsView(
        cases_searching=count(select(func.count()).select_from(Case).where(Case.status == "searching")),
        heroes_available=count(select(func.count()).select_from(Hero).where(Hero.available.is_(True))),
        cases_closed=count(select(func.count()).select_from(Case).where(Case.status == "closed")),
    )
