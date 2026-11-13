import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    NAVY = RGBColor(16, 44, 87)       # #102C57
    TOMATO = RGBColor(227, 38, 54)     # #E32636
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    DARK_TEXT = RGBColor(30, 41, 59)   # #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(241, 245, 249)
    BORDER_COLOR = RGBColor(203, 213, 225)
    AZURE_BLUE = RGBColor(0, 120, 212)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="Department of Master of Computer Applications | MCA462N - Internship – Phase I"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = AZURE_BLUE

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = NAVY
        p1.space_before = Pt(4)

        # Thin accent line under title
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = TOMATO
        line.line.color.rgb = TOMATO

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)

    # Background card
    bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = LIGHT_BG
    bg.line.fill.background()

    # Top banner bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.4))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = NAVY
    top_bar.line.fill.background()

    # Department & College
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.0))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "RV COLLEGE OF ENGINEERING®"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER

    p2 = tf1.add_paragraph()
    p2.text = "Department of Master of Computer Applications\nMCA462N - Internship – Phase I"
    p2.font.size = Pt(13)
    p2.font.color.rgb = MUTED_TEXT
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(4)

    # Main Project Title Card
    card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(2.2), Inches(10.933), Inches(1.8))
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = BORDER_COLOR

    c_tf = card.text_frame
    c_tf.word_wrap = True
    cp1 = c_tf.paragraphs[0]
    cp1.text = "Daily Tomato Price Prediction System"
    cp1.font.size = Pt(30)
    cp1.font.bold = True
    cp1.font.color.rgb = TOMATO
    cp1.alignment = PP_ALIGN.CENTER

    cp2 = c_tf.add_paragraph()
    cp2.text = "End-to-End Automated MLOps Pipeline & Real-Time Dashboard on Microsoft Azure"
    cp2.font.size = Pt(14)
    cp2.font.bold = True
    cp2.font.color.rgb = NAVY
    cp2.alignment = PP_ALIGN.CENTER
    cp2.space_before = Pt(8)

    # Student Names & Guide Card
    details_box = s1.shapes.add_textbox(Inches(1.2), Inches(4.3), Inches(10.933), Inches(2.5))
    dtf = details_box.text_frame
    dtf.word_wrap = True

    # 3-column layout simulation
    dp1 = dtf.paragraphs[0]
    dp1.text = "Presented by:"
    dp1.font.size = Pt(13)
    dp1.font.bold = True
    dp1.font.color.rgb = NAVY

    dp2 = dtf.add_paragraph()
    dp2.text = "• Achintya K  (1RV25MC002)\n• Priya N       (1RV25MC075)"
    dp2.font.size = Pt(14)
    dp2.font.bold = True
    dp2.font.color.rgb = DARK_TEXT
    dp2.space_before = Pt(4)

    dp3 = dtf.add_paragraph()
    dp3.text = "Under the Guidance of: Dr. Usha J, Professor, RV College of Engineering"
    dp3.font.size = Pt(13)
    dp3.font.bold = True
    dp3.font.color.rgb = NAVY
    dp3.space_before = Pt(12)

    dp4 = dtf.add_paragraph()
    dp4.text = "Internship carried out – RVCE-CoE: Women in Cloud (WiC) Center of Excellence"
    dp4.font.size = Pt(12)
    dp4.font.italic = True
    dp4.font.color.rgb = MUTED_TEXT
    dp4.space_before = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 2: AGENDA
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Agenda")

    agenda_items = [
        ("01", "Domain", "Cloud Computing, Data Engineering & Time-Series Machine Learning"),
        ("02", "Engineering Knowledge / Operational Procedures", "Automated daily cron, data integrity, 37 time-series features & Key Vault security"),
        ("03", "Design & Development of Solutions / Process Structure", "Architecture from raw mandi CSVs to XGBoost modeling and Azure cloud deployment"),
        ("04", "Modern Tools / Methods Explored & Technology Use", "Azure Container Instances (ACI), ACR, Front Door, Blob Storage, React & Terraform"),
        ("05", "Implementation Results & Conclusion", "98.5% R² model accuracy, sub-second inference, live web UI across 41 Karnataka mandis"),
        ("06", "Societal and Environmental Concern", "Empowering farmers with fair price intelligence; Green Cloud serverless efficiency"),
        ("07", "Application of Project Management Principles", "Modular design, error-handling fallbacks, version control & Terraform IaC"),
        ("08", "Summarization & Future Scope", "Key technical learnings and future roadmap for pan-India agricultural intelligence")
    ]

    for idx, (num, title, desc) in enumerate(agenda_items):
        col = idx % 2
        row = idx // 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.8 + row * 1.3)

        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.75), Inches(1.15))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = f"{num}. {title}"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(10.5)
        p_desc.font.color.rgb = DARK_TEXT
        p_desc.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 3: INTERNSHIP CARRIED OUT
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Internship Carried Out")

    # 3 Cards Layout
    cards_data = [
        ("Organization", "Women in Cloud (WiC)\nRVCE Center of Excellence (CoE)", "RVCE-CoE initiative committed to fostering cutting-edge cloud engineering, AI/ML, and scalable modern web solutions."),
        ("Category", "RVCE-CoE Project", "Executed directly within the college's advanced research incubator focusing on real-world industry cloud architectures."),
        ("What We Built", "Automated Azure Cloud ML Pipeline", "Built an end-to-end automated system on Microsoft Azure to ingest daily Karnataka mandi tomato prices, train predictive ML models, and serve live forecasts to stakeholders.")
    ]

    for i, (title, sub, body) in enumerate(cards_data):
        c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.95), Inches(1.9), Inches(3.75), Inches(4.8))
        c.fill.solid()
        c.fill.fore_color.rgb = WHITE
        c.line.color.rgb = BORDER_COLOR

        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TOMATO

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = NAVY
        p2.space_before = Pt(8)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.size = Pt(12)
        p3.font.color.rgb = DARK_TEXT
        p3.space_before = Pt(14)

    # -------------------------------------------------------------
    # SLIDE 4: DOMAIN
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Domain")

    d_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.1))
    d_box.fill.solid()
    d_box.fill.fore_color.rgb = WHITE
    d_box.line.color.rgb = BORDER_COLOR

    dtf = d_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_right = Inches(0.4)
    dtf.margin_top = Inches(0.3)

    p = dtf.paragraphs[0]
    p.text = "Main Domain: Cloud Computing & Software Engineering"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    sub_domains = [
        ("Machine Learning & Time-Series Forecasting", "Developing multi-market regression models (XGBoost & Random Forest) that predict tomorrow's modal, minimum, and maximum prices for 41 Karnataka APMC mandis with high precision (R² = 98.5%)."),
        ("Data Engineering & ETL Pipelines", "Automated ingestion, cleaning, validation, and multi-lag feature engineering (37 features) from historical Agricultural Produce Market Committee (APMC) records spanning 2023–2025."),
        ("Cloud Infrastructure & DevOps (MLOps)", "Provisioning 14 enterprise cloud services on Microsoft Azure using Terraform (Infrastructure as Code), containerizing apps with Docker, and orchestrating CI/CD pipelines."),
        ("Full-Stack Web Development", "Building a responsive React dashboard with dynamic SVG price curves, search filters, and a high-performance FastAPI asynchronous backend.")
    ]

    for title, text in sub_domains:
        sp1 = dtf.add_paragraph()
        sp1.text = f"• {title}: "
        sp1.font.size = Pt(13)
        sp1.font.bold = True
        sp1.font.color.rgb = TOMATO
        sp1.space_before = Pt(14)

        sp2 = dtf.add_paragraph()
        sp2.text = f"   {text}"
        sp2.font.size = Pt(12)
        sp2.font.color.rgb = DARK_TEXT
        sp2.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 5: ENGINEERING KNOWLEDGE / OPERATIONAL PROCEDURES
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Engineering Knowledge / Operational Procedures")

    ops = [
        ("Automatic Daily Workflow", "Built an automated scheduler daemon running inside the container that triggers daily at 06:00 IST without requiring manual intervention, fetching fresh data, generating predictions, and clearing stale caches."),
        ("Data Safety & Idempotent Pipelines", "Engineered safe database upsert logic (`INSERT OR IGNORE`) and atomic blob writes to prevent duplicate entries even if pipelines are re-triggered multiple times in a single day."),
        ("Temporal Time-Series Training", "Trained models strictly respecting chronological ordering (temporal train-test split) with 37 lag and rolling features, preventing lookahead bias and data leakage between past and future dates."),
        ("Cloud Security & Secret Management", "Implemented enterprise DevSecOps principles using Azure Key Vault to store database connection strings and registry credentials. Zero sensitive passwords are committed to source control.")
    ]

    for i, (title, desc) in enumerate(ops):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8 + i * 1.25), Inches(11.733), Inches(1.1))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COLOR

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = f"✔ {title}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 6: DESIGN & DEVELOPMENT OF SOLUTIONS / PROCESS STRUCTURE
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Design & Development of Solutions / Process Structure")

    steps = [
        ("Step 1: Ingestion", "Raw CSV datasets (2023-2025) stored in Azure Blob Storage (`raw-data` container)."),
        ("Step 2: Preprocessing", "Feature engineering pipeline generates 37 time-series features (lags, rolling averages, seasonality)."),
        ("Step 3: Training & Registry", "XGBoost regressor is trained; best model artifact (`best_model_latest.joblib`) saved to Azure Storage & ML Workspace."),
        ("Step 4: Inference Engine", "Batch inference calculates predicted modal, min, and max prices with confidence intervals for 41 Karnataka mandis."),
        ("Step 5: API & Front Door", "FastAPI container in Azure Container Instances (ACI) exposes REST endpoints, routed globally via Azure Front Door."),
        ("Step 6: Dashboard & Alerts", "Live React dashboard renders price curves; automated HTML forecast bulletin emailed to stakeholders.")
    ]

    for i, (st, desc) in enumerate(steps):
        row = i // 2
        col = i % 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.8 + row * 1.7)

        c = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.75), Inches(1.5))
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = BORDER_COLOR

        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.15)

        p = tf.paragraphs[0]
        p.text = st
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TOMATO

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 6B: PROCESS STRUCTURE FLOWCHART
    # -------------------------------------------------------------
    s6b = prs.slides.add_slide(blank_layout)
    add_header(s6b, "Process Structure / Pipeline Flowchart")

    # Left: Embed the Flowchart Image
    flowchart_img_path = os.path.join(os.path.dirname(output_path), "azure_pipeline_flowchart.png")
    if os.path.exists(flowchart_img_path):
        s6b.shapes.add_picture(flowchart_img_path, Inches(0.8), Inches(1.8), height=Inches(5.2))

    # Right: Explanatory card
    side_card = s6b.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.8), Inches(1.8), Inches(6.733), Inches(5.2))
    side_card.fill.solid()
    side_card.fill.fore_color.rgb = WHITE
    side_card.line.color.rgb = BORDER_COLOR

    s_tf = side_card.text_frame
    s_tf.word_wrap = True
    s_tf.margin_left = s_tf.margin_right = Inches(0.3)
    s_tf.margin_top = Inches(0.25)

    sp = s_tf.paragraphs[0]
    sp.text = "Step-by-Step Azure Architecture Flow"
    sp.font.size = Pt(15)
    sp.font.bold = True
    sp.font.color.rgb = NAVY

    flow_bullets = [
        ("1. Data Ingestion & Storage", "Historical APMC mandi price CSVs (2023–2025) are stored securely in Azure Blob Storage (`raw-data` container)."),
        ("2. Automated ETL Preprocessing", "`data_preprocessing.py` cleans and extracts 37 time-series features (multi-day price lags, rolling volatility, and seasonal cyclic encodings)."),
        ("3. Time-Series Model Training", "Trains an XGBoost Regressor ($R^2 = 0.985$, $MAE = ₹37.07$) with temporal validation to prevent data leakage."),
        ("4. Dual Artifact Persistence", "Best model artifact (`best_model_latest.joblib`) is saved to Azure Blob Storage; predictions across 41 Karnataka mandis are saved as JSON/DB."),
        ("5. Serverless Container Serving", "FastAPI backend runs inside Azure Container Instances (ACI) on port 8000, pulling predictions in sub-second response times."),
        ("6. Global CDN Delivery & Live UI", "Azure Front Door manages global HTTPS routing and SSL termination, serving the live React Dashboard directly to end users.")
    ]

    for b_title, b_desc in flow_bullets:
        p1 = s_tf.add_paragraph()
        p1.text = f"• {b_title}: "
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = TOMATO
        p1.space_before = Pt(8)

        p2 = s_tf.add_paragraph()
        p2.text = f"   {b_desc}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(1)

    # -------------------------------------------------------------
    # SLIDE 6C: AZURE CLOUD SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s6c = prs.slides.add_slide(blank_layout)
    add_header(s6c, "Azure Cloud System Architecture (End-to-End Tiers)")

    arch_img_path = os.path.join(os.path.dirname(output_path), "azure_system_architecture.png")
    if os.path.exists(arch_img_path):
        s6c.shapes.add_picture(arch_img_path, Inches(0.8), Inches(1.8), width=Inches(11.733))

    # -------------------------------------------------------------
    # SLIDE 7: MODERN TOOLS / METHODS EXPLORED & TECHNOLOGY USE
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Modern Tools / Methods Explored & Technology Use")

    tech_categories = [
        ("Azure Cloud Services", [
            "Azure Container Instances (ACI) - Serverless Docker container hosting",
            "Azure Container Registry (ACR) - Private container image repository",
            "Azure Front Door - Layer-7 global CDN, SSL routing & DDoS protection",
            "Azure Blob Storage - Data lake for datasets, models, and predictions",
            "Azure Key Vault - Hardware-level secret & credential management",
            "Azure ML Workspace & Application Insights - Experiment tracking & APM telemetry"
        ]),
        ("ML & Software Stack", [
            "Python 3.11 & FastAPI - High-speed asynchronous REST API framework",
            "XGBoost & Scikit-learn - Time-series ensemble gradient boosted decision trees",
            "Pandas & NumPy - High-throughput data transformation & feature engineering",
            "React & Vite - Interactive single-page dashboard with SVG trend rendering",
            "Docker - Multi-stage lightweight Linux containerization",
            "Terraform - Infrastructure as Code (IaC) automated cloud provisioning"
        ])
    ]

    for idx, (cat_title, items) in enumerate(tech_categories):
        left = Inches(0.8 + idx * 5.95)
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(5.75), Inches(5.1))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COLOR

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = cat_title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = NAVY

        for item in items:
            ip = tf.add_paragraph()
            ip.text = f"✔ {item}"
            ip.font.size = Pt(11.5)
            ip.font.color.rgb = DARK_TEXT
            ip.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 8: AZURE CLOUD SERVICES ARCHITECTURE & ROLES (TABLE)
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Azure Cloud Services Architecture & Roles")

    table_shape = s8.shapes.add_table(10, 3, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.1))
    table = table_shape.table

    table.columns[0].width = Inches(2.6)
    table.columns[1].width = Inches(2.4)
    table.columns[2].width = Inches(6.733)

    headers = ["Azure Service", "Resource Name in Portal", "Role in the Tomato Prediction System"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE

    rows_data = [
        ("Azure Container Instances", "tomato-aci-egk79m", "Runs backend FastAPI container & prediction engine 24/7 serverless"),
        ("Azure Container Registry", "tomatoacregk79m", "Private registry storing Docker images (tomato-prediction-api)"),
        ("Azure Front Door (CDN)", "tomato-fd-egk79m", "Global Layer-7 entry point, SSL termination & public HTTPS routing"),
        ("Azure Blob Storage", "tomatostoreegk79m", "Stores raw CSV datasets, trained XGBoost models, and daily JSON outputs"),
        ("Azure Key Vault", "tomato-kv-egk79m", "Centralized security vault managing connection strings & ACR credentials"),
        ("Azure Machine Learning", "tomato-mlws-egk79m", "Tracks model lineage, versions, R² / MAE metrics, and experiment runs"),
        ("Azure Data Factory", "tomato-adf-egk79m", "Cloud data integration pipeline service for automated data ingestion"),
        ("Azure Event Grid", "tomato-eg-blob-egk79m", "Pub/sub event triggers that detect new dataset uploads for retraining"),
        ("Application Insights", "tomato-appins-egk79m", "Monitors live request latency, HTTP status codes, and server health")
    ]

    for i, row_vals in enumerate(rows_data):
        for j, val in enumerate(row_vals):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 == 0 else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            p.font.color.rgb = DARK_TEXT
            if j == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY

    # -------------------------------------------------------------
    # SLIDE 9: IMPLEMENTATION RESULTS & CONCLUSION
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Implementation Results & Conclusion")

    results_data = [
        ("High Model Performance", "XGBoost Regressor achieved exceptional accuracy:\n• R² Score: 98.46% (0.9846)\n• Mean Absolute Error: ₹37.07 per quintal\n• Outperformed baseline Random Forest across all 41 mandis."),
        ("Live Cloud Deployment", "Hosted and live on Microsoft Azure:\n• Live URL: https://tomato-fd-ep-egk79m-azh7hsbbgte4gaez.a02.azurefd.net/\n• Sub-second response latency via Azure Front Door CDN\n• Interactive React UI with dynamic SVG historical & prediction curves."),
        ("Full Automation Lifecycle", "Zero manual maintenance required:\n• Background scheduler executes daily at 06:00 IST\n• Forecasts generated and saved for all 41 Karnataka mandis\n• Automated HTML email bulletin dispatched to priya@iservce.onmicrosoft.com.")
    ]

    for i, (title, body) in enumerate(results_data):
        c = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.95), Inches(1.8), Inches(3.75), Inches(3.8))
        c.fill.solid()
        c.fill.fore_color.rgb = WHITE
        c.line.color.rgb = BORDER_COLOR

        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(8)

    # Conclusion Banner at bottom
    concl = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.1))
    concl.fill.solid()
    concl.fill.fore_color.rgb = CARD_BG
    concl.line.color.rgb = TOMATO

    ctf = concl.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.3)
    ctf.margin_top = Inches(0.12)
    cp = ctf.paragraphs[0]
    cp.text = "Conclusion:"
    cp.font.size = Pt(12)
    cp.font.bold = True
    cp.font.color.rgb = TOMATO

    cp2 = ctf.add_paragraph()
    cp2.text = "Successfully implemented an end-to-end production MLOps system on Microsoft Azure, unifying data engineering, modern time-series ML, serverless containerization, and automated notifications into a reliable, enterprise-grade cloud architecture."
    cp2.font.size = Pt(10.5)
    cp2.font.color.rgb = DARK_TEXT
    cp2.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 10: SOCIETAL AND ENVIRONMENTAL CONCERN
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Societal and Environmental Concern")

    soc_cards = [
        ("Societal Benefit", [
            ("Empowering Agricultural Communities", "Tomato prices in India fluctuate drastically due to seasonal perishability. Forward-looking price intelligence helps farmers decide the ideal market to sell, avoiding distress sales."),
            ("Fair Market Transparency", "Democratizes APMC price data across 41 Karnataka mandis, giving smallholder farmers equal negotiating power against wholesale middlemen."),
            ("Women in Tech Initiative", "Engineered under the Women in Cloud (WiC) Center of Excellence at RV College of Engineering to build technology with social impact.")
        ]),
        ("Environmental Benefit (Green Cloud)", [
            ("Serverless & Containerized Architecture", "Using Azure Container Instances (ACI) eliminates the need for idle virtual machines running 24/7, significantly lowering electrical energy consumption."),
            ("Edge Caching Efficiency", "Azure Front Door caches static web assets globally, reducing backend server compute cycles and decreasing carbon footprint."),
            ("Resource Optimization", "Scheduled cron execution spins up prediction computations only when needed, adhering to Green Software Foundation standards.")
        ])
    ]

    for idx, (title, items) in enumerate(soc_cards):
        left = Inches(0.8 + idx * 5.95)
        card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(5.75), Inches(5.1))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COLOR

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TOMATO if idx == 0 else AZURE_BLUE

        for heading, body in items:
            hp = tf.add_paragraph()
            hp.text = f"• {heading}:"
            hp.font.size = Pt(11.5)
            hp.font.bold = True
            hp.font.color.rgb = NAVY
            hp.space_before = Pt(8)

            bp = tf.add_paragraph()
            bp.text = f"   {body}"
            bp.font.size = Pt(10.5)
            bp.font.color.rgb = DARK_TEXT
            bp.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 11: APPLICATION OF PROJECT MANAGEMENT PRINCIPLES
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Application of Project Management Principles")

    pm_cards = [
        ("Modular Architecture", "Decoupled into 5 standalone modules: `data/` for raw storage, `ml_pipeline/` for feature engineering, `api/` for FastAPI services, `frontend/` for React dashboard, and `terraform/` for IaC provisioning."),
        ("Defensive Error Handling", "Built automatic fallbacks: database fallbacks for SQLite/Azure SQL, in-memory cache fallbacks when Redis is absent, and CSV fallbacks if telemetry historical points are sparse."),
        ("Infrastructure as Code (IaC)", "Codified all 14 Azure services declaratively in Terraform, eliminating manual portal configuration and ensuring 100% reproducible deployments."),
        ("Clean Version Control", "Followed structured Git branching workflows (`main` -> `final`), automated `.dockerignore` context optimizations, and PowerShell deployment scripting (`deploy.ps1`).")
    ]

    for i, (title, desc) in enumerate(pm_cards):
        c = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8 + i * 1.25), Inches(11.733), Inches(1.1))
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = BORDER_COLOR

        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = f"📌 {title}"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 12: SUMMARIZATION & FUTURE SCOPE
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Summarization")

    sum_cards = [
        ("What We Learnt", [
            "End-to-end integration between Machine Learning pipelines and enterprise cloud infrastructure (Microsoft Azure).",
            "Effective feature engineering for agricultural time-series data with extreme volatility and seasonality.",
            "Containerizing applications with multi-stage Docker builds and managing images through Azure Container Registry.",
            "Automating cloud resource provisioning via Terraform and configuring Layer-7 routing with Azure Front Door."
        ]),
        ("Future Scope", [
            "Expanding data ingestion beyond Karnataka to all major tomato-producing states across India (Maharashtra, AP, MP).",
            "Integrating satellite weather APIs (rainfall, temperature) as external features to model climate shock events.",
            "Adding multi-channel alerting via WhatsApp and SMS gateway integrations for rural farmers without smartphones.",
            "Deploying distributed model retraining pipelines utilizing Azure Data Factory and Azure Synapse Analytics."
        ])
    ]

    for idx, (cat_title, items) in enumerate(sum_cards):
        left = Inches(0.8 + idx * 5.95)
        card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(5.75), Inches(5.1))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COLOR

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = cat_title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = NAVY

        for item in items:
            ip = tf.add_paragraph()
            ip.text = f"✔ {item}"
            ip.font.size = Pt(11.5)
            ip.font.color.rgb = DARK_TEXT
            ip.space_before = Pt(10)

    prs.save(output_path)
    print(f"Presentation successfully generated at: {output_path}")

if __name__ == "__main__":
    out_dir = r"d:\All_projects\tomato_price_prediction"
    out_file = os.path.join(out_dir, "Tomato_Price_Prediction_Azure_Presentation_v3.pptx")
    create_deck(out_file)

