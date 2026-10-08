import streamlit as st
from PIL import Image

from modules.ocr import extract_text_from_image
from modules.image_analysis import (
    analyze_image_against_claim
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Multimodal Misinformation Verifier",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    /* =========================================
       MAIN APPLICATION
       ========================================= */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(79, 70, 229, 0.18),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(14, 165, 233, 0.12),
                transparent 28%
            ),
            #080d1c;
    }


    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* =========================================
       GENERAL TEXT
       ========================================= */

    .stApp p,
    .stApp label {
        color: #dbe4f0;
    }


    .stApp small {
        color: #aebbd0;
    }


    /* =========================================
       SIDEBAR
       ========================================= */

    [data-testid="stSidebar"] {
        background: #0b1222;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }


    [data-testid="stSidebar"] p {
        color: #cbd5e1 !important;
        line-height: 1.65;
    }


    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
    }


    [data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }


    [data-testid="stSidebar"] hr {
        border-color: rgba(148, 163, 184, 0.16);
    }


    /* =========================================
       MAIN HEADINGS
       ========================================= */

    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.035em;
    }


    h2,
    h3 {
        color: #f8fafc !important;
    }


    /* =========================================
       HERO AREA
       ========================================= */

    .hero-caption {
        color: #a5b4fc !important;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }


    .hero-description {
        color: #b8c5d8 !important;
        font-size: 1rem;
        line-height: 1.7;
        max-width: 850px;
        margin-top: -0.3rem;
        margin-bottom: 1.6rem;
    }


    /* =========================================
       CONTAINERS / CARDS
       ========================================= */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
    }


    /* =========================================
       INPUTS
       ========================================= */

    textarea,
    input {
        border-radius: 12px !important;
    }


    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 15px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 0.4rem;
    }


    [data-testid="stFileUploader"] label {
        color: #dbe4f0 !important;
    }


    /* =========================================
       BUTTON
       ========================================= */

    .stButton > button {
        min-height: 3.1rem;
        border-radius: 13px;
        font-weight: 750;
        transition: all 0.2s ease;
    }


    .stButton > button:hover {
        transform: translateY(-1px);
    }


    /* =========================================
       METRICS
       ========================================= */

    [data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(30, 41, 59, 0.90),
                rgba(15, 23, 42, 0.95)
            );

        border: 1px solid rgba(148, 163, 184, 0.15);

        border-radius: 18px;

        padding: 1.2rem;
    }


    [data-testid="stMetricLabel"] {
        color: #aebbd0 !important;
    }


    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }


    /* =========================================
       TABLE
       ========================================= */

    [data-testid="stTable"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* =========================================
       ALERTS
       ========================================= */

    [data-testid="stAlert"] {
        border-radius: 14px;
    }


    /* =========================================
       DIVIDERS
       ========================================= */

    hr {
        border-color: rgba(148, 163, 184, 0.14);
    }


    /* =========================================
       FOOTER
       ========================================= */

    .footer-text {
        text-align: center;
        color: #94a3b8 !important;
        font-size: 0.82rem;
        line-height: 1.6;
        padding-top: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HERO HEADER
# ==================================================

st.markdown(
    "### 🔎 AI • MULTIMODAL ANALYSIS • COLLEGE PROJECT"
)

st.title(
    "Multimodal Misinformation Verifier"
)

st.markdown(
    """
    <div class="hero-description">
    An AI-assisted system that checks whether a text claim is
    visually consistent with an uploaded image using OCR,
    CLIP-based semantic analysis, and visual concept comparison.
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("🔎 Project Overview")

    st.write(
        "This system performs visual consistency checking "
        "between a user-provided claim and an uploaded image."
    )

    st.divider()

    st.subheader("🧠 Components")

    st.markdown(
        """
        📝 **Text claim analysis**

        🖼️ **Image analysis**

        🔤 **OCR**

        🧠 **CLIP**

        📊 **Visual concept comparison**

        🔎 **Multimodal verification**
        """
    )

    st.divider()

    st.subheader("⚙️ System Pipeline")

    st.markdown(
        """
        **User Claim**

        ↓

        **Uploaded Image**

        ↓

        **OCR + CLIP**

        ↓

        **Image–Claim Analysis**

        ↓

        **Visual Concept Comparison**

        ↓

        **Final Assessment**
        """
    )

    st.divider()

    st.caption(
        "College Project Prototype"
    )


# ==================================================
# STEP 1 — CLAIM
# ==================================================

st.header("1️⃣ Enter the Claim")

st.caption(
    "Write the statement you want the system to check against the image."
)

claim = st.text_area(
    "Claim",
    placeholder="Example: A dog is sitting on grass.",
    height=100,
    label_visibility="collapsed"
)


# ==================================================
# STEP 2 — IMAGE
# ==================================================

st.header("2️⃣ Upload the Image")

st.caption(
    "Upload a JPG, JPEG, PNG, or WEBP image for visual analysis."
)

uploaded_file = st.file_uploader(
    "Choose an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
        "jfif"
    ],
    label_visibility="collapsed"
)


st.write("")


verify_button = st.button(
    "🔍  Verify Claim",
    type="primary",
    use_container_width=True
)


# ==================================================
# VERIFICATION
# ==================================================

if verify_button:

    if not claim.strip():

        st.error(
            "Please enter a claim."
        )

        st.stop()


    if uploaded_file is None:

        st.error(
            "Please upload an image."
        )

        st.stop()


    # ==================================================
    # OPEN IMAGE
    # ==================================================

    try:

        image = Image.open(
            uploaded_file
        ).convert("RGB")

    except Exception as error:

        st.error(
            f"Could not open image: {error}"
        )

        st.stop()


    # ==================================================
    # STEP 3 — INPUT
    # ==================================================

    st.header("3️⃣ Verification Input")

    input_col1, input_col2 = st.columns(
        [1.1, 0.9],
        gap="large"
    )


    with input_col1:

        st.subheader("🖼️ Uploaded Image")

        st.image(
            image,
            use_container_width=True
        )


    with input_col2:

        st.subheader("💬 Claim Being Analyzed")

        with st.container(
            border=True
        ):

            st.write(
                f"“{claim.strip()}”"
            )


    # ==================================================
    # STEP 4 — OCR
    # ==================================================

    st.header("4️⃣ Image Text Analysis")

    st.caption(
        "OCR checks whether readable text is present inside the uploaded image."
    )

    with st.spinner(
        "Reading text inside the image..."
    ):

        extracted_text = (
            extract_text_from_image(
                image
            )
        )


    if extracted_text:

        st.success(
            "✓ Text detected inside the image."
        )

        st.text_area(
            "OCR Extracted Text",
            value=extracted_text,
            height=150
        )

    else:

        st.info(
            "No readable text was detected inside the image."
        )


    # ==================================================
    # STEP 5 — IMAGE ANALYSIS
    # ==================================================

    st.header("5️⃣ Image ↔ Claim Analysis")

    st.caption(
        "CLIP compares the uploaded image with the claim and its visual concepts."
    )

    with st.spinner(
        "Analyzing the uploaded image..."
    ):

        image_analysis = (
            analyze_image_against_claim(
                image,
                claim
            )
        )


    full_claim_score = image_analysis[
        "full_claim_score"
    ]

    visual_terms = image_analysis[
        "visual_terms"
    ]

    visual_average = image_analysis[
        "visual_average"
    ]

    image_match_category = image_analysis[
        "image_match_category"
    ]

    strongest_claim_concept = image_analysis[
        "strongest_claim_concept"
    ]

    strongest_claim_probability = image_analysis[
        "strongest_claim_probability"
    ]

    strongest_competitor = image_analysis[
        "strongest_competitor"
    ]

    strongest_competitor_probability = image_analysis[
        "strongest_competitor_probability"
    ]

    strong_image_mismatch = image_analysis[
        "strong_image_mismatch"
    ]


    # ==================================================
    # SCORE CARDS
    # ==================================================

    score_col1, score_col2 = st.columns(
        2,
        gap="large"
    )


    with score_col1:

        st.metric(
            "Image ↔ Full Claim Similarity",
            f"{full_claim_score:.2f}%"
        )


    with score_col2:

        if visual_average is not None:

            st.metric(
                "Average Relative Claim Match",
                f"{visual_average:.2f}%"
            )

        else:

            st.metric(
                "Average Relative Claim Match",
                "N/A"
            )


    st.write("")


    # ==================================================
    # IMAGE ASSESSMENT
    # ==================================================

    if strong_image_mismatch:

        st.error(
            "🔴 The uploaded image does not strongly "
            "match the visual concepts in the claim."
        )

    else:

        st.info(
            f"Image assessment: "
            f"**{image_match_category}**"
        )


    # ==================================================
    # STRONGEST CONCEPTS
    # ==================================================

    concept_col1, concept_col2 = st.columns(
        2,
        gap="large"
    )


    with concept_col1:

        if strongest_claim_concept:

            with st.container(
                border=True
            ):

                st.caption(
                    "STRONGEST CLAIM CONCEPT"
                )

                st.subheader(
                    strongest_claim_concept
                )

                st.write(
                    f"Relative score: "
                    f"{strongest_claim_probability:.2f}%"
                )


    with concept_col2:

        if strongest_competitor:

            with st.container(
                border=True
            ):

                st.caption(
                    "STRONGEST COMPETING CONCEPT"
                )

                st.subheader(
                    strongest_competitor
                )

                st.write(
                    f"Relative score: "
                    f"{strongest_competitor_probability:.2f}%"
                )


    # ==================================================
    # VISUAL CONCEPT COMPARISON
    # ==================================================

    if visual_terms:

        st.subheader(
            "📊 Visual Concept Comparison"
        )

        st.caption(
            "Relative scores compare the visual concepts "
            "mentioned in the claim with other common "
            "visual concepts. They are not object-detection "
            "probabilities."
        )


        relative_probabilities = image_analysis[
            "relative_probabilities"
        ]

        claim_concept_scores = image_analysis[
            "claim_concept_scores"
        ]


        rows = []


        for term in visual_terms:

            rows.append(
                {
                    "Claim Concept": term,

                    "CLIP Similarity": (
                        f"{claim_concept_scores.get(term, 0):.2f}%"
                    ),

                    "Relative Match": (
                        f"{relative_probabilities.get(term, 0):.2f}%"
                    )
                }
            )


        st.table(
            rows
        )


        # ==================================================
        # RANKING
        # ==================================================

        ranking = image_analysis[
            "ranking"
        ]


        if ranking:

            st.subheader(
                "🏆 Image Concept Ranking"
            )

            ranking_text = " → ".join(
                ranking[:10]
            )

            st.info(
                ranking_text
            )


    else:

        st.info(
            "No clear visual concepts were detected "
            "from the claim."
        )


    # ==================================================
    # STEP 6 — FINAL ASSESSMENT
    # ==================================================

    st.header("6️⃣ Final Assessment")


    # IMPORTANT:
    # The improved image_analysis.py now calculates
    # the final visual consistency category.
    #
    # app.py should display that result instead of
    # recalculating the old competitor-gap logic.


    if strong_image_mismatch:

        final_assessment = (
            "Possible Image–Claim Mismatch"
        )

        final_explanation = (
            "The uploaded image is more strongly "
            "associated with a competing visual concept "
            "than with the main visual concepts in the claim."
        )

        result_icon = "🔴"


    elif image_match_category == (
        "Strong visual consistency"
    ):

        final_assessment = (
            "Strong Visual Consistency"
        )

        final_explanation = (
            "The image is strongly consistent with "
            "the main visual concepts in the claim. "
            "This indicates strong visual agreement "
            "between the uploaded image and the claim, "
            "but it does not independently prove that "
            "the claim is factually true."
        )

        result_icon = "🟢"


    elif image_match_category == (
        "Visually consistent — moderate confidence"
    ):

        final_assessment = (
            "Visually Consistent — Moderate Confidence"
        )

        final_explanation = (
            "The image is visually consistent with "
            "the main concepts in the claim, but the "
            "available visual evidence is not strong "
            "enough for a high-confidence conclusion."
        )

        result_icon = "🟡"


    elif image_match_category == (
        "Weak or uncertain visual consistency"
    ):

        final_assessment = (
            "Weak / Uncertain Visual Consistency"
        )

        final_explanation = (
            "The image provides some visual similarity "
            "to the claim, but the available evidence "
            "is not strong enough for a reliable visual "
            "consistency conclusion."
        )

        result_icon = "🟡"


    else:

        final_assessment = (
            "Insufficient Visual Information"
        )

        final_explanation = (
            "The image analysis does not provide "
            "enough clear visual information to "
            "evaluate the claim reliably."
        )

        result_icon = "⚪"


    # ==================================================
    # FINAL RESULT DISPLAY
    # ==================================================

    if final_assessment == (
        "Possible Image–Claim Mismatch"
    ):

        st.error(
            f"{result_icon} **{final_assessment}**\n\n"
            f"{final_explanation}"
        )


    elif final_assessment == (
        "Strong Visual Consistency"
    ):

        st.success(
            f"{result_icon} **{final_assessment}**\n\n"
            f"{final_explanation}"
        )


    elif final_assessment == (
        "Visually Consistent — Moderate Confidence"
    ):

        st.warning(
            f"{result_icon} **{final_assessment}**\n\n"
            f"{final_explanation}"
        )


    elif final_assessment == (
        "Weak / Uncertain Visual Consistency"
    ):

        st.warning(
            f"{result_icon} **{final_assessment}**\n\n"
            f"{final_explanation}"
        )


    else:

        st.info(
            f"{result_icon} **{final_assessment}**\n\n"
            f"{final_explanation}"
        )


    # ==================================================
    # LIMITATION
    # ==================================================

    st.subheader(
        "⚠️ Important Limitation"
    )

    with st.container(
        border=True
    ):

        st.write(
            "**This system performs visual consistency "
            "checking, not absolute fact verification.**"
        )

        st.write(
            "For example, if an image contains a dog and "
            "the claim says “A dog is sitting on grass”, "
            "the system can check whether the image is "
            "visually consistent with the claim."
        )

        st.write(
            "It cannot independently prove when or where "
            "the photograph was taken, who took it, whether "
            "the photograph has been edited, or whether "
            "the overall claim is factually true."
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    "<p style='text-align:center; color:#94a3b8;'>"
    "🔎 Multimodal Misinformation Verifier<br>"
    "AI-assisted visual consistency analysis • "
    "College Project Prototype"
    "</p>",
    unsafe_allow_html=True
)
