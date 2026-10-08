import os
import re

import pytesseract

from PIL import (
    Image,
    ImageOps,
    ImageEnhance
)


# ============================================================
# TESSERACT LOCATION
# ============================================================

WINDOWS_TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if os.path.exists(WINDOWS_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = (
        WINDOWS_TESSERACT_PATH
    )


# ============================================================
# CHECK WHETHER OCR WORD LOOKS REAL
# ============================================================

def is_reasonable_word(
    text
):
    """
    Reject obvious OCR garbage.
    """

    text = text.strip()

    if not text:
        return False

    # Remove surrounding punctuation
    cleaned = re.sub(
        r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$",
        "",
        text
    )

    if len(cleaned) < 3:
        return False

    # Count letters
    letters = re.findall(
        r"[A-Za-z]",
        cleaned
    )

    digits = re.findall(
        r"[0-9]",
        cleaned
    )

    # Most useful OCR text contains letters
    if len(letters) >= 3:

        # Reject extremely strange letter patterns
        if len(
            set(
                letter.lower()
                for letter in letters
            )
        ) == 1:
            return False

        return True

    # Allow numbers only when they have at least
    # three digits.
    if len(digits) >= 3:
        return True

    return False


# ============================================================
# OCR FUNCTION
# ============================================================

def extract_text_from_image(
    image
):
    """
    Extract readable text using Tesseract.

    The function is intentionally conservative because
    photographs can cause Tesseract to interpret textures,
    reflections and objects as text.
    """

    try:

        # ----------------------------------------------------
        # Convert image
        # ----------------------------------------------------

        image = image.convert(
            "RGB"
        )

        # ----------------------------------------------------
        # Resize
        # ----------------------------------------------------

        width, height = image.size

        scale = 2

        image = image.resize(
            (
                width * scale,
                height * scale
            )
        )

        # ----------------------------------------------------
        # Grayscale
        # ----------------------------------------------------

        gray = ImageOps.grayscale(
            image
        )

        gray = ImageEnhance.Contrast(
            gray
        ).enhance(1.5)

        # ----------------------------------------------------
        # Run OCR using multiple page layouts
        # ----------------------------------------------------

        modes = [
            6,
            11,
            12
        ]

        detected = {}

        for mode in modes:

            try:

                data = (
                    pytesseract.image_to_data(
                        gray,
                        config=f"--psm {mode}",
                        output_type=(
                            pytesseract.Output.DICT
                        )
                    )
                )

            except Exception:

                continue

            total = len(
                data["text"]
            )

            for index in range(
                total
            ):

                raw_text = (
                    data["text"][index]
                )

                raw_text = raw_text.strip()

                if not raw_text:
                    continue

                # --------------------------------------------
                # Confidence
                # --------------------------------------------

                try:

                    confidence = float(
                        data["conf"][index]
                    )

                except Exception:

                    confidence = 0

                # Very low confidence = probably noise
                if confidence < 60:
                    continue

                if not is_reasonable_word(
                    raw_text
                ):
                    continue

                cleaned = re.sub(
                    r"[^A-Za-z0-9@#&%$.,:/\\-]",
                    "",
                    raw_text
                )

                normalized = (
                    cleaned.lower()
                )

                if normalized not in detected:

                    detected[
                        normalized
                    ] = {
                        "text": cleaned,
                        "count": 0,
                        "best_confidence": 0
                    }

                detected[
                    normalized
                ]["count"] += 1

                detected[
                    normalized
                ]["best_confidence"] = max(
                    detected[
                        normalized
                    ]["best_confidence"],
                    confidence
                )

        # ----------------------------------------------------
        # Select reliable text
        # ----------------------------------------------------

        reliable_words = []

        for key, info in detected.items():

            # If multiple OCR layouts detect the same
            # word, that is strong evidence.

            if info["count"] >= 2:

                reliable_words.append(
                    info["text"]
                )

                continue

            # A single detection must have very high
            # confidence.

            if (
                info["best_confidence"]
                >= 85
            ):

                reliable_words.append(
                    info["text"]
                )

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        final_words = []

        seen = set()

        for word in reliable_words:

            key = word.lower()

            if key in seen:
                continue

            seen.add(key)

            final_words.append(
                word
            )

        # ----------------------------------------------------
        # No reliable text
        # ----------------------------------------------------

        if not final_words:
            return ""

        return " ".join(
            final_words
        )

    except Exception as error:

        print(
            f"OCR Error: {error}"
        )

        return ""