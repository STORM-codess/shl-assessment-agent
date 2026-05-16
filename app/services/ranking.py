
# ---------------------------------------------------
# Simple Reranking
# ---------------------------------------------------
def rerank_results(query, results):

    reranked = []

    query = query.lower()

    for result in results:

        score = 0

        # -----------------------------------
        # Remote boost
        # -----------------------------------

        if (
            "remote" in query
            and result["remote"] == "yes"
        ):
            score += 2

        # -----------------------------------
        # Adaptive boost
        # -----------------------------------

        if (
            "adaptive" in query
            and result["adaptive"] == "yes"
        ):
            score += 2

        # -----------------------------------
        # Online / virtual boost
        # -----------------------------------

        if (
            (
                "online" in query
                or "virtual" in query
            )
            and result["remote"] == "yes"
        ):
            score += 1

        # -----------------------------------
        # Save rerank score
        # -----------------------------------

        result["rerank_score"] = score

        reranked.append(result)

    # -----------------------------------
    # Sort by rerank score
    # -----------------------------------

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked


# ---------------------------------------------------
"""Reranking and diversity helpers used by the retrieval service.

This module contains small, pure helpers so the retrieval code can
focus on embeddings and index operations.
"""

from typing import List, Dict, Any


def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    primary_skills: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """Rerank results using skill-match, semantic distance and simple boosts.

    - `primary_skills`: optional list of required skills (e.g. ["java", "spring"]).
      If not provided, a small keyword extractor will derive likely skills from
      the `query` string so callers don't need to change.

    Scoring weights (tunable): skill_match=0.6, distance=0.3, other_boosts=0.1.
    """

    KNOWN_SKILLS = [
        "java",
        "spring",
        "rest",
        "sql",
        "aws",
        "docker",
        "angular",
        "ci/cd",
        "kubernetes",
        "jenkins",
        "cloud",
    ]

    q = (query or "").lower()

    # Derive primary skills from query if not passed explicitly
    if not primary_skills:
        derived = []
        for s in KNOWN_SKILLS:
            if s in q:
                derived.append(s)
        primary_skills = derived

    # Precompute distance normalization
    distances = [r.get("distance") for r in results if r.get("distance") is not None]
    max_d = max(distances) if distances else 0.0
    if max_d <= 0:
        max_d = 1.0

    reranked: List[Dict[str, Any]] = []

    for result in results:
        skill_score = 0.0
        # collect test type names
        test_type_names = set()
        for t in result.get("test_types", []):
            if isinstance(t, dict):
                name = t.get("name", "")
            else:
                name = str(t)
            if name:
                test_type_names.add(name.lower())

        # Count overlaps with primary skills
        if primary_skills:
            match_count = 0
            for ps in primary_skills:
                psl = ps.lower()
                for tn in test_type_names:
                    if psl in tn or tn in psl:
                        match_count += 1
                        break
            skill_score = match_count / max(1, len(primary_skills))

        # Distance score: closer (smaller distance) -> higher score
        dist = result.get("distance", 0.0)
        distance_score = 1.0 - (dist / max_d)
        if distance_score < 0:
            distance_score = 0.0

        # Other heuristic boosts (legacy behavior)
        other_boost = 0.0
        if "remote" in q and result.get("remote") == "yes":
            other_boost += 1.0
        if "adaptive" in q and result.get("adaptive") == "yes":
            other_boost += 1.0
        if ("online" in q or "virtual" in q) and result.get("remote") == "yes":
            other_boost += 0.5

        # Combine with weights
        skill_w = 0.6
        dist_w = 0.3
        other_w = 0.1

        combined = (skill_w * skill_score) + (dist_w * distance_score) + (other_w * other_boost)

        result["rerank_score"] = combined
        reranked.append(result)

    reranked.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    return reranked


def diversify_results(results: List[Dict[str, Any]], max_results: int = 10) -> List[Dict[str, Any]]:
    """Select a diverse subset of results prioritizing unique test types."""

    diversified: List[Dict[str, Any]] = []
    used_test_types = set()

    for result in results:
        current_types = set(
            t.get("name") for t in result.get("test_types", []) if t.get("name")
        )

        overlap = current_types.intersection(used_test_types)

        if len(overlap) == 0 or len(diversified) < 3:
            diversified.append(result)
            used_test_types.update(current_types)

        if len(diversified) >= max_results:
            return diversified

    existing_names = set(r.get("name") for r in diversified)

    for result in results:
        if result.get("name") not in existing_names:
            diversified.append(result)
            existing_names.add(result.get("name"))

        if len(diversified) >= max_results:
            break

    return diversified
