import gradio as gr
from google import genai
import tempfile
import os
from PIL import Image

# ==========================================
# GEMINI API CONFIGURATION
# ==========================================
client = genai.Client(
    api_key="YOUR_GEMINI_API_KEY"
)

# ==========================================
# AI SYSTEM PROMPT
# ==========================================
SYSTEM_PROMPT = """
You are DermaSense AI, a professional AI Dermatology Assistant.

Your responsibilities:
- Analyze skin conditions from uploaded images
- Give professional and medically responsible responses
- Maintain modern dermatology-report formatting
- Explain observations clearly

STRICT RULES:
- Never claim a final diagnosis
- Mention confidence level
- Mention this is not a replacement for doctors
- Recommend dermatologist consultation when needed
- Avoid fear-inducing language

Response Format:

# Skin Observation
# Possible Conditions
# Severity Level
# Recommended Care
# Helpful Ingredients
# When To See Dermatologist
# Confidence Level
# Medical Disclaimer
"""

# ==========================================
# MAIN AI FUNCTION
# ==========================================
def analyze_skin(image, concern_type, symptoms, extra_notes):

    try:

        if image is None:
            return "⚠️ Please upload a skin image."

        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            image.save(temp_file.name)
            temp_path = temp_file.name

        # Upload image to Gemini
        uploaded_file = client.files.upload(file=temp_path)

        # Final Prompt
        final_prompt = f"""
        {SYSTEM_PROMPT}

        Concern Type:
        {concern_type}

        Symptoms:
        {symptoms}

        Extra Notes:
        {extra_notes}

        Analyze this skin image professionally.
        """

        # Gemini Response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                uploaded_file,
                final_prompt
            ]
        )

        return response.text

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ==========================================
# SKINCARE ROUTINE GENERATOR
# ==========================================
def skincare_routine(skin_type):

    routines = {

        "Oily": """
## 🌞 Morning
- Salicylic Acid Cleanser
- Niacinamide Serum
- Oil-Free Moisturizer
- SPF 50 Sunscreen

## 🌙 Night
- Gentle Cleanser
- Retinol (2-3x weekly)
- Lightweight Moisturizer
""",

        "Dry": """
## 🌞 Morning
- Hydrating Cleanser
- Hyaluronic Acid Serum
- Ceramide Moisturizer
- SPF 50 Sunscreen

## 🌙 Night
- Cream Cleanser
- Hydrating Serum
- Thick Moisturizer
""",

        "Combination": """
## 🌞 Morning
- Gentle Cleanser
- Niacinamide Serum
- Gel Moisturizer
- SPF 50 Sunscreen

## 🌙 Night
- Gentle Cleanser
- Retinol
- Moisturizer
""",

        "Sensitive": """
## 🌞 Morning
- Fragrance-Free Cleanser
- Barrier Repair Cream
- Mineral Sunscreen

## 🌙 Night
- Gentle Cleanser
- Ceramide Moisturizer
"""
    }

    return routines.get(skin_type, "Please select a skin type.")


# ==========================================
# ACNE SEVERITY CHECKER
# ==========================================
def acne_checker(acne_count):

    acne_count = int(acne_count)

    if acne_count <= 5:
        return "🟢 Mild Acne"

    elif acne_count <= 20:
        return "🟠 Moderate Acne"

    else:
        return "🔴 Severe Acne — Dermatologist consultation recommended."


# ==========================================
# PROFESSIONAL THEME
# ==========================================
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="gray"
)

# ==========================================
# MAIN UI
# ==========================================
with gr.Blocks(
    theme=theme,
    title="DermaSense AI"
) as demo:

    # ======================================
    # HEADER
    # ======================================
    gr.HTML("""
    <div style="
        text-align:center;
        padding:30px;
        margin-bottom:20px;
        border-radius:22px;
        background:linear-gradient(90deg,#0f172a,#111827);
        color:white;
        box-shadow:0 8px 30px rgba(0,0,0,0.35);
    ">

    <h1 style="
        font-size:54px;
        font-weight:900;
        margin-bottom:10px;
        letter-spacing:1px;
    ">
    🩺 DermaSense AI
    </h1>

    <p style="
        font-size:20px;
        color:#cbd5e1;
        margin-bottom:8px;
    ">
    Professional AI Dermatology Assistant
    </p>

    <p style="
        font-size:14px;
        color:#94a3b8;
    ">
    AI-Powered Skin Analysis & Smart Skincare Guidance
    </p>

    </div>
    """)

    # ======================================
    # TABS
    # ======================================
    with gr.Tabs():

        # ==================================
        # TAB 1 - SKIN ANALYSIS
        # ==================================
        with gr.Tab("🔬 Skin Analysis"):

            with gr.Row(equal_height=True):

                # LEFT PANEL
                with gr.Column(scale=1):

                    image_input = gr.Image(
                        type="pil",
                        label="Upload Skin Image"
                    )

                    # ==================================
                    # SAMPLE IMAGES
                    # ==================================
                    gr.Examples(
                        examples=[
                            ["/content/skin.jpg"],
                            ["/content/skin1.jpg"],
                            ["/content/skin2.jpg"],
                            ["/content/skin3.jpg"]
                        ],
                        inputs=image_input
                    )

                    concern_dropdown = gr.Dropdown(
                        choices=[
                            "Acne",
                            "Pigmentation",
                            "Rash",
                            "Dry Skin",
                            "Eczema",
                            "Allergy",
                            "Mole",
                            "Other"
                        ],
                        label="Concern Type"
                    )

                    symptoms_input = gr.Textbox(
                        lines=3,
                        label="Symptoms",
                        placeholder="Redness, itching, swelling..."
                    )

                    notes_input = gr.Textbox(
                        lines=2,
                        label="Extra Notes",
                        placeholder="Duration, medications, pain level..."
                    )

                    analyze_btn = gr.Button(
                        "Analyze Skin",
                        variant="primary",
                        size="lg"
                    )

                # RIGHT PANEL
                with gr.Column(scale=1):

                    with gr.Accordion(
                        "📋 AI Dermatology Report",
                        open=True
                    ):

                        output = gr.Markdown()

            # ==================================
            # BUTTON ACTION
            # ==================================
            analyze_btn.click(
                fn=analyze_skin,
                inputs=[
                    image_input,
                    concern_dropdown,
                    symptoms_input,
                    notes_input
                ],
                outputs=output
            )

        # ==================================
        # TAB 2 - SKINCARE ROUTINE
        # ==================================
        with gr.Tab("🧴 Skincare Routine"):

            gr.Markdown("## Personalized Skincare Routine")

            skin_type = gr.Radio(
                choices=[
                    "Oily",
                    "Dry",
                    "Combination",
                    "Sensitive"
                ],
                label="Choose Skin Type"
            )

            routine_btn = gr.Button(
                "Generate Routine",
                variant="primary"
            )

            routine_output = gr.Markdown()

            routine_btn.click(
                fn=skincare_routine,
                inputs=skin_type,
                outputs=routine_output
            )

        # ==================================
        # TAB 3 - ACNE CHECKER
        # ==================================
        with gr.Tab("📊 Acne Severity Checker"):

            gr.Markdown("## Acne Severity Estimator")

            acne_slider = gr.Slider(
                minimum=0,
                maximum=50,
                step=1,
                label="Approximate Acne Count"
            )

            acne_btn = gr.Button(
                "Check Severity",
                variant="primary"
            )

            acne_output = gr.Textbox(
                label="Severity Result"
            )

            acne_btn.click(
                fn=acne_checker,
                inputs=acne_slider,
                outputs=acne_output
            )

        # ==================================
        # TAB 4 - ABOUT
        # ==================================
        with gr.Tab("ℹ️ About"):

            gr.Markdown("""
            # About DermaSense AI

            DermaSense AI is a professional AI-powered
            dermatology assistant built using:

            - Gemini 2.5 Flash
            - Gradio
            - Python
            - PIL

            ## Features
            ✅ AI Skin Analysis
            ✅ Acne Severity Detection
            ✅ Personalized Skincare Guidance
            ✅ Medical-style Reporting

            ## Disclaimer
            This application is NOT a replacement
            for licensed medical professionals.

            Always consult a dermatologist for
            prescriptions and proper diagnosis.
            """)

    # ======================================
    # FOOTER
    # ======================================
    gr.HTML("""
    <hr>

    <center>
    <p style="
        color:gray;
        font-size:14px;
        margin-top:10px;
    ">
    DermaSense AI © 2026 | Built with Gemini + Gradio
    </p>
    </center>
    """)

# ==========================================
# LAUNCH APP
# ==========================================
demo.launch(share=True)