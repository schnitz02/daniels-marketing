# tests/test_models.py
from tests.conftest import *  # noqa

def test_idea_has_evidence_field(db):
    from src.db.models import Idea
    idea = Idea(title="Test", body="Body", evidence="Because competitor X did Y")
    db.add(idea)
    db.commit()
    fetched = db.query(Idea).filter_by(title="Test").first()
    assert fetched.evidence == "Because competitor X did Y"

def test_idea_evidence_nullable(db):
    from src.db.models import Idea
    idea = Idea(title="No evidence", body="Body")
    db.add(idea)
    db.commit()
    fetched = db.query(Idea).filter_by(title="No evidence").first()
    assert fetched.evidence is None
