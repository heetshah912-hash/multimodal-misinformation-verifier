import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel


# ============================================================
# LOAD CLIP MODEL
# ============================================================

MODEL_NAME = "openai/clip-vit-base-patch32"

print("Loading CLIP model...")

model = CLIPModel.from_pretrained(
    MODEL_NAME
)

processor = CLIPProcessor.from_pretrained(
    MODEL_NAME
)

model.eval()

print("CLIP model loaded successfully!")


# ============================================================
# INTERNAL EMBEDDING FUNCTION
# ============================================================

def _get_embeddings(image, texts):

    inputs = processor(
        text=texts,
        images=image,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():

        outputs = model(
            **inputs
        )

        image_embedding = F.normalize(
            outputs.image_embeds,
            p=2,
            dim=-1
        )

        text_embeddings = F.normalize(
            outputs.text_embeds,
            p=2,
            dim=-1
        )

    return (
        image_embedding,
        text_embeddings
    )


# ============================================================
# SINGLE IMAGE ↔ TEXT SIMILARITY
# ============================================================

def calculate_image_text_similarity(
    image,
    text
):

    """
    Calculate CLIP semantic similarity
    between one image and one text.

    IMPORTANT:
    This is NOT a truth probability.
    """

    image_embedding, text_embeddings = (
        _get_embeddings(
            image,
            [text]
        )
    )

    similarity = torch.sum(
        image_embedding
        *
        text_embeddings[0],
        dim=-1
    ).item()

    score = (
        (similarity + 1)
        /
        2
    ) * 100

    return round(
        score,
        2
    )


# ============================================================
# MULTIPLE IMAGE ↔ TEXT SIMILARITIES
# ============================================================

def calculate_image_text_similarities(
    image,
    texts
):

    """
    Calculate CLIP similarity between
    one image and multiple text descriptions.
    """

    if not texts:
        return {}

    clean_texts = []

    for text in texts:

        if text is None:
            continue

        text = str(
            text
        ).strip()

        if text:

            clean_texts.append(
                text
            )

    if not clean_texts:
        return {}

    image_embedding, text_embeddings = (
        _get_embeddings(
            image,
            clean_texts
        )
    )

    results = {}

    for index, text in enumerate(
        clean_texts
    ):

        similarity = torch.sum(
            image_embedding
            *
            text_embeddings[index],
            dim=-1
        ).item()

        score = (
            (similarity + 1)
            /
            2
        ) * 100

        results[text] = round(
            score,
            2
        )

    return results


# ============================================================
# RELATIVE IMAGE CONCEPT SCORES
# ============================================================

def calculate_relative_image_scores(
    image,
    concepts
):

    """
    Compare several visual concepts against
    the SAME uploaded image.

    Example:

        dog     -> high
        horse   -> lower
        plane   -> lower

    The ranking is useful for comparing concepts.

    IMPORTANT:
    These are relative CLIP scores.
    They are NOT object-detection probabilities.
    """

    if not concepts:

        return {
            "scores": {},
            "probabilities": {},
            "ranking": []
        }


    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique_concepts = []

    for concept in concepts:

        concept = str(
            concept
        ).strip().lower()

        if (
            concept
            and concept not in unique_concepts
        ):

            unique_concepts.append(
                concept
            )


    if not unique_concepts:

        return {
            "scores": {},
            "probabilities": {},
            "ranking": []
        }


    # --------------------------------------------------------
    # Create CLIP prompts
    # --------------------------------------------------------

    prompts = []

    for concept in unique_concepts:

        prompts.append(
            f"a photo of a {concept}"
        )


    # --------------------------------------------------------
    # Process image + prompts
    # --------------------------------------------------------

    inputs = processor(
        text=prompts,
        images=image,
        return_tensors="pt",
        padding=True
    )


    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            **inputs
        )

        image_embedding = F.normalize(
            outputs.image_embeds,
            p=2,
            dim=-1
        )

        text_embeddings = F.normalize(
            outputs.text_embeds,
            p=2,
            dim=-1
        )


    # --------------------------------------------------------
    # Calculate cosine similarity
    # --------------------------------------------------------

    cosine_scores = torch.matmul(
        image_embedding,
        text_embeddings.T
    ).squeeze(0)


    # --------------------------------------------------------
    # Convert similarities into relative
    # comparison scores
    # --------------------------------------------------------

    temperature = 0.07

    relative_probabilities = torch.softmax(
        cosine_scores / temperature,
        dim=0
    )


    scores = {}

    probabilities = {}


    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    for index, concept in enumerate(
        unique_concepts
    ):

        cosine_value = (
            cosine_scores[index]
            .item()
        )


        raw_score = (
            (cosine_value + 1)
            /
            2
        ) * 100


        scores[concept] = round(
            raw_score,
            2
        )


        probabilities[concept] = round(
            relative_probabilities[index]
            .item()
            * 100,
            2
        )


    # --------------------------------------------------------
    # Rank concepts
    # --------------------------------------------------------

    ranking = sorted(
        unique_concepts,
        key=lambda concept:
        probabilities[concept],
        reverse=True
    )


    return {
        "scores": scores,
        "probabilities": probabilities,
        "ranking": ranking
    }