import re

from models.clip_model import (
    calculate_image_text_similarity,
    calculate_relative_image_scores
)


# ============================================================
# NON-VISUAL WORDS
# ============================================================

NON_VISUAL_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "be", "been", "being", "am", "this", "that",
    "these", "those", "there", "here", "of", "to",
    "in", "on", "at", "for", "from", "with", "by",
    "and", "or", "but", "as", "it", "its", "he",
    "she", "they", "them", "his", "her", "their",
    "has", "have", "had", "do", "does", "did",
    "can", "could", "will", "would", "should",
    "may", "might", "must", "very", "really",
    "just", "not", "no", "yes", "today",
    "yesterday", "tomorrow", "recently", "always",
    "never", "probably", "possibly", "reportedly"
}


# ============================================================
# VISUAL WORDS
# ============================================================

VISUAL_WORDS = {
    "dog", "cat", "horse", "cow", "bird",
    "person", "people", "man", "woman", "child",
    "baby", "car", "bus", "truck", "train",
    "plane", "airplane", "boat", "ship",
    "motorcycle", "bicycle", "bike", "building",
    "house", "road", "street", "tree", "trees",
    "grass", "sky", "cloud", "clouds", "water",
    "river", "lake", "ocean", "mountain",
    "mountains", "forest", "beach", "field",
    "park", "room", "table", "chair", "food",
    "phone", "computer", "laptop", "camera",
    "shirt", "dress", "shoe", "shoes", "red",
    "blue", "green", "black", "white", "yellow",
    "orange", "sitting", "standing", "running",
    "walking", "lying", "flying", "driving",
    "riding", "holding", "wearing", "jumping",
    "playing", "sleeping", "eating"
}


# ============================================================
# COMMON COMPETING VISUAL CONCEPTS
# ============================================================

COMPETING_CONCEPTS = [
    "dog", "cat", "horse", "bird", "person",
    "car", "bus", "truck", "plane", "boat",
    "bicycle", "motorcycle", "building", "house",
    "tree", "grass", "sky", "water", "road",
    "mountain", "food"
]


# ============================================================
# EXTRACT VISUAL TERMS FROM CLAIM
# ============================================================

def extract_visual_terms(claim):

    if not claim:
        return []

    words = re.findall(
        r"[A-Za-z]+",
        claim.lower()
    )

    terms = []

    for word in words:

        if len(word) < 3:
            continue

        if word in NON_VISUAL_WORDS:
            continue

        if (
            word in VISUAL_WORDS
            and word not in terms
        ):
            terms.append(word)

    return terms


# ============================================================
# ANALYZE IMAGE AGAINST CLAIM
# ============================================================

def analyze_image_against_claim(
    image,
    claim
):

    # --------------------------------------------------------
    # FULL CLAIM SIMILARITY
    # --------------------------------------------------------

    full_claim_score = (
        calculate_image_text_similarity(
            image,
            claim
        )
    )


    # --------------------------------------------------------
    # EXTRACT VISUAL CONCEPTS
    # --------------------------------------------------------

    visual_terms = extract_visual_terms(
        claim
    )


    # --------------------------------------------------------
    # CREATE CANDIDATE CONCEPT LIST
    # --------------------------------------------------------

    candidate_concepts = []

    for concept in (
        visual_terms + COMPETING_CONCEPTS
    ):

        if concept not in candidate_concepts:

            candidate_concepts.append(
                concept
            )


    # --------------------------------------------------------
    # RELATIVE CLIP ANALYSIS
    # --------------------------------------------------------

    relative_result = (
        calculate_relative_image_scores(
            image,
            candidate_concepts
        )
    )

    scores = relative_result.get(
        "scores",
        {}
    )

    probabilities = relative_result.get(
        "probabilities",
        {}
    )

    ranking = relative_result.get(
        "ranking",
        []
    )


    # --------------------------------------------------------
    # CLAIM CONCEPT SCORES
    # --------------------------------------------------------

    claim_concept_scores = {}

    claim_probabilities = []

    for concept in visual_terms:

        claim_concept_scores[concept] = (
            scores.get(
                concept,
                0.0
            )
        )

        claim_probabilities.append(
            probabilities.get(
                concept,
                0.0
            )
        )


    # --------------------------------------------------------
    # VISUAL CONCEPT COVERAGE
    # --------------------------------------------------------
    #
    # A concept is considered reasonably supported when
    # its relative probability is at least 5%.
    #
    # This is NOT a truth probability.
    # It is only used internally to estimate how many
    # claim concepts receive meaningful visual support.
    #

    supported_concepts = []

    for concept in visual_terms:

        probability = probabilities.get(
            concept,
            0.0
        )

        if probability >= 5.0:

            supported_concepts.append(
                concept
            )


    if visual_terms:

        concept_coverage = (
            len(supported_concepts)
            /
            len(visual_terms)
        ) * 100

    else:

        concept_coverage = 0.0


    # --------------------------------------------------------
    # AVERAGE RELATIVE CLAIM MATCH
    # --------------------------------------------------------

    if claim_probabilities:

        visual_average = (
            sum(claim_probabilities)
            /
            len(claim_probabilities)
        )

    else:

        visual_average = None


    # --------------------------------------------------------
    # STRONGEST CLAIM CONCEPT
    # --------------------------------------------------------

    if visual_terms:

        strongest_claim_concept = max(
            visual_terms,
            key=lambda concept:
            probabilities.get(
                concept,
                0.0
            )
        )

        strongest_claim_probability = (
            probabilities.get(
                strongest_claim_concept,
                0.0
            )
        )

    else:

        strongest_claim_concept = None

        strongest_claim_probability = 0.0


    # --------------------------------------------------------
    # STRONGEST COMPETING CONCEPT
    # --------------------------------------------------------

    competing_concepts = [
        concept
        for concept in ranking
        if concept not in visual_terms
    ]

    if competing_concepts:

        strongest_competitor = (
            competing_concepts[0]
        )

        strongest_competitor_probability = (
            probabilities.get(
                strongest_competitor,
                0.0
            )
        )

    else:

        strongest_competitor = None

        strongest_competitor_probability = 0.0


    # --------------------------------------------------------
    # COMPETITOR GAP
    # --------------------------------------------------------

    competitor_gap = (
        strongest_claim_probability
        -
        strongest_competitor_probability
    )


    # --------------------------------------------------------
    # OVERALL VISUAL CONSISTENCY SCORE
    # --------------------------------------------------------
    #
    # This combines:
    #
    # 45% = full claim similarity
    # 35% = concept coverage
    # 20% = concept-vs-competitor strength
    #
    # This is a project-specific consistency score.
    # It is NOT a probability that the claim is true.
    #

    normalized_claim_similarity = (
        max(
            0.0,
            min(
                full_claim_score,
                100.0
            )
        )
    )

    normalized_coverage = (
        max(
            0.0,
            min(
                concept_coverage,
                100.0
            )
        )
    )

    if strongest_claim_probability > 0:

        if strongest_competitor_probability > 0:

            strength_ratio = (
                strongest_claim_probability
                /
                (
                    strongest_claim_probability
                    +
                    strongest_competitor_probability
                )
            ) * 100

        else:

            strength_ratio = 100.0

    else:

        strength_ratio = 0.0


    overall_consistency_score = (
        normalized_claim_similarity * 0.45
        +
        normalized_coverage * 0.35
        +
        strength_ratio * 0.20
    )


    overall_consistency_score = round(
        overall_consistency_score,
        2
    )


    # --------------------------------------------------------
    # MISMATCH DETECTION
    # --------------------------------------------------------

    strong_image_mismatch = False

    if (
        visual_terms
        and ranking
        and ranking[0] not in visual_terms
    ):

        # A mismatch is stronger when the competing
        # concept clearly beats the strongest claim concept.

        if (
            strongest_competitor_probability
            >
            strongest_claim_probability + 2
        ):

            strong_image_mismatch = True


    # --------------------------------------------------------
    # IMAGE MATCH CATEGORY
    # --------------------------------------------------------

    if not visual_terms:

        image_match_category = (
            "No clear visual concepts detected"
        )

    elif strong_image_mismatch:

        image_match_category = (
            "Possible image–claim mismatch"
        )

    elif (
        overall_consistency_score >= 70
        and concept_coverage >= 66
        and competitor_gap >= 5
    ):

        image_match_category = (
            "Strong visual consistency"
        )

    elif (
        overall_consistency_score >= 55
        and concept_coverage >= 33
        and competitor_gap >= 2
    ):

        image_match_category = (
            "Visually consistent — moderate confidence"
        )

    elif (
        overall_consistency_score >= 45
        and concept_coverage > 0
    ):

        image_match_category = (
            "Weak or uncertain visual consistency"
        )

    else:

        image_match_category = (
            "Weak or uncertain visual consistency"
        )


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "full_claim_score":
            round(
                full_claim_score,
                2
            ),

        "visual_terms":
            visual_terms,

        "claim_concept_scores":
            claim_concept_scores,

        "relative_probabilities":
            probabilities,

        "ranking":
            ranking,

        "supported_concepts":
            supported_concepts,

        "concept_coverage":
            round(
                concept_coverage,
                2
            ),

        "visual_average":
            (
                round(
                    visual_average,
                    2
                )
                if visual_average is not None
                else None
            ),

        "strongest_claim_concept":
            strongest_claim_concept,

        "strongest_claim_probability":
            round(
                strongest_claim_probability,
                2
            ),

        "strongest_competitor":
            strongest_competitor,

        "strongest_competitor_probability":
            round(
                strongest_competitor_probability,
                2
            ),

        "competitor_gap":
            round(
                competitor_gap,
                2
            ),

        "overall_consistency_score":
            overall_consistency_score,

        "strong_image_mismatch":
            strong_image_mismatch,

        "image_match_category":
            image_match_category
    }


# ============================================================
# IMAGE–EVIDENCE SIMILARITY
# ============================================================

def calculate_image_evidence_score(
    image,
    evidence_text
):

    if not evidence_text:
        return 0.0

    return calculate_image_text_similarity(
        image,
        evidence_text
    )