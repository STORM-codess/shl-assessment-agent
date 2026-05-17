from app.services.response_formatter import (
    extract_recommendation_names,
    build_recommendations
)


def test_extract_numbered():
    reply = "1. OPQ Leadership Report\n2. Verify G+\n"
    assert extract_recommendation_names(reply) == [
        "OPQ Leadership Report",
        "Verify G+"
    ]


def test_extract_hyphen_block():
    reply = "Some text\nRECOMMENDED_ASSESSMENTS:\n- OPQ Leadership Report\n- Verify G+\n"
    names = extract_recommendation_names(reply)
    assert "OPQ Leadership Report" in names
    assert "Verify G+" in names


def test_build_recommendations():
    reply = "1. OPQ Leadership Report\nRECOMMENDED_ASSESSMENTS:\n- Verify G+\n"
    retrieved = [
        {"name": "OPQ Leadership Report", "url": "u", "test_types": [{"code": "PERS"}]},
        {"name": "Verify G+", "url": "v", "test_types": [{"code": "COG"}]}
    ]
    recs = build_recommendations(reply, retrieved)
    names = [r["name"] for r in recs]
    assert "OPQ Leadership Report" in names
    assert "Verify G+" in names
