import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_azure_architecture(output_png):
    # Set high-res 16:9 widescreen canvas
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')

    # Palette
    AZURE_BLUE  = '#0078D4'
    DARK_BLUE   = '#102C57'
    SLATE_DARK  = '#1E293B'
    SLATE_MUTED = '#64748B'
    BORDER_COL  = '#CBD5E1'
    TIER_BG     = '#FFFFFF'
    TOMATO_RED  = '#E32636'
    GREEN_ACC   = '#16A34A'
    PURPLE_ACC  = '#7C3AED'
    ORANGE_ACC  = '#EA580C'

    # Title Banner
    ax.text(0.8, 8.4, "Azure Cloud System Architecture", fontsize=20, fontweight='bold', color=DARK_BLUE, fontfamily='sans-serif')
    ax.text(0.8, 8.05, "Automated Daily Tomato Price Forecasting & Alerting MLOps Pipeline across 41 Karnataka APMC Mandis", fontsize=11, color=SLATE_MUTED, fontfamily='sans-serif')

    # Draw 4 Tier Containers
    tier_y = 1.0
    tier_h = 6.6
    tier_w = 3.4

    tiers = [
        (0.8, "1. Ingestion & Storage Tier", "#E0F2FE", "Data Lake & Storage"),
        (4.5, "2. ML & Analytics Tier", "#F3E8FF", "XGBoost & Azure ML"),
        (8.2, "3. Serving & Compute Tier", "#DCFCE7", "Container Instances & API"),
        (11.9, "4. Ingress, Security & Delivery", "#FEF3C7", "Front Door & Key Vault")
    ]

    for x_pos, name, header_bg, sub in tiers:
        # Outer tier box
        rect = patches.FancyBboxPatch(
            (x_pos, tier_y), tier_w, tier_h,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=TIER_BG, edgecolor=BORDER_COL, linewidth=1.2, zorder=1
        )
        ax.add_patch(rect)

        # Header background pill
        h_rect = patches.FancyBboxPatch(
            (x_pos, tier_y + tier_h - 0.75), tier_w, 0.75,
            boxstyle="round,pad=0.03,rounding_size=0.1",
            facecolor=header_bg, edgecolor='none', zorder=2
        )
        ax.add_patch(h_rect)

        ax.text(x_pos + tier_w/2, tier_y + tier_h - 0.32, name, ha='center', va='center', fontsize=11, fontweight='bold', color=DARK_BLUE, zorder=3)
        ax.text(x_pos + tier_w/2, tier_y + tier_h - 0.55, sub, ha='center', va='center', fontsize=9, color=SLATE_MUTED, zorder=3)

    # Helper function to draw service cards inside tiers
    def add_service_card(x, y, w, h, title, subtitle, badge, badge_color):
        card = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.05,rounding_size=0.1",
            facecolor='#F8FAFC', edgecolor='#E2E8F0', linewidth=1.2, zorder=3
        )
        ax.add_patch(card)

        # Badge
        badge_box = patches.FancyBboxPatch(
            (x + 0.15, y + h - 0.32), len(badge)*0.11 + 0.25, 0.22,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=badge_color, edgecolor='none', zorder=4
        )
        ax.add_patch(badge_box)
        ax.text(x + 0.15 + (len(badge)*0.11 + 0.25)/2, y + h - 0.21, badge, ha='center', va='center', fontsize=7.5, fontweight='bold', color='white', zorder=5)

        # Title & Subtitle
        ax.text(x + 0.15, y + h - 0.55, title, fontsize=10.5, fontweight='bold', color=DARK_BLUE, zorder=4)
        ax.text(x + 0.15, y + h - 0.82, subtitle, fontsize=8.5, color=SLATE_MUTED, zorder=4)

    # Tier 1 Cards
    add_service_card(1.0, 5.8, 3.0, 1.0, "APMC Mandi Datasets", "3,000 records (2023–2025)\nKarnataka Tomato Prices", "RAW INPUT", TOMATO_RED)
    add_service_card(1.0, 4.3, 3.0, 1.0, "Azure Data Factory", "Resource: tomato-adf-egk79m\nAutomated ETL Orchestration", "ETL SERVICE", AZURE_BLUE)
    add_service_card(1.0, 2.8, 3.0, 1.0, "Azure Blob Storage", "Storage: tomatostoreegk79m\nContainers: raw-data, models", "DATA LAKE", AZURE_BLUE)
    add_service_card(1.0, 1.3, 3.0, 1.0, "Azure Event Grid", "System Topic: tomato-eg-blob\nBlobCreated Event Triggers", "PUB / SUB", PURPLE_ACC)

    # Tier 2 Cards
    add_service_card(4.7, 5.8, 3.0, 1.0, "Feature Engineering", "37 Time-Series Features\nLags t-1..t-14, 30d Rolling Avg", "PIPELINE", GREEN_ACC)
    add_service_card(4.7, 4.3, 3.0, 1.0, "XGBoost + RF Regressor", "Best Model R² = 0.985\nMAE = ₹37.07/qtl (41 Mandis)", "ML ENGINE", PURPLE_ACC)
    add_service_card(4.7, 2.8, 3.0, 1.0, "Azure ML Workspace", "Resource: tomato-mlws-egk79m\nModel Registry & Checkpoints", "MLOPS HUB", AZURE_BLUE)
    add_service_card(4.7, 1.3, 3.0, 1.0, "Model Checkpoint Store", "Artifact: best_model_latest.joblib\n+ metrics.json & metadata", "ARTIFACTS", ORANGE_ACC)

    # Tier 3 Cards
    add_service_card(8.4, 5.8, 3.0, 1.0, "Azure Container Registry", "Registry: tomatoacregk79m\nDocker Images: API & Frontend", "REGISTRY", AZURE_BLUE)
    add_service_card(8.4, 4.3, 3.0, 1.0, "Azure Container Instances", "Resource: tomato-aci-egk79m\nFastAPI Engine on Port 8000", "SERVERLESS", GREEN_ACC)
    add_service_card(8.4, 2.8, 3.0, 1.0, "Daily Scheduler Daemon", "Automated Cron at 06:00 IST\nETL, Predict & Cache Invalidate", "AUTOMATION", DARK_BLUE)
    add_service_card(8.4, 1.3, 3.0, 1.0, "Notification Dispatcher", "HTML Email Forecast Bulletin\nRecipient: priya@iservce...", "ALERTS", TOMATO_RED)

    # Tier 4 Cards
    add_service_card(12.1, 5.8, 3.0, 1.0, "Azure Front Door (CDN)", "Endpoint: tomato-fd-ep-egk79m\nGlobal HTTPS, SSL & Edge Cache", "INGRESS CDN", AZURE_BLUE)
    add_service_card(12.1, 4.3, 3.0, 1.0, "React Dashboard UI", "Web SPA: SVG Trend Curves\n41 Mandi Search, KPI Cards", "FRONTEND", GREEN_ACC)
    add_service_card(12.1, 2.8, 3.0, 1.0, "Azure Key Vault", "Resource: tomato-kv-egk79m\nHardware-Grade Secrets Store", "SECURITY", PURPLE_ACC)
    add_service_card(12.1, 1.3, 3.0, 1.0, "Application Insights & LAW", "App Insights + Log Analytics\nLatency, APM & HTTP Telemetry", "MONITORING", AZURE_BLUE)

    # Connection Arrows between Tiers
    arrow_style = dict(arrowstyle="-|>", color=SLATE_MUTED, lw=2, mutation_scale=15, zorder=6)

    # 1. Datasets -> ADF -> Blob
    ax.annotate("", xy=(2.5, 5.3), xytext=(2.5, 5.8), arrowprops=arrow_style)
    ax.annotate("", xy=(2.5, 3.8), xytext=(2.5, 4.3), arrowprops=arrow_style)
    ax.annotate("", xy=(2.5, 2.3), xytext=(2.5, 2.8), arrowprops=arrow_style)

    # 2. Blob -> Feature Eng (Tier 1 to Tier 2)
    ax.annotate("", xy=(4.7, 6.3), xytext=(4.0, 3.3), arrowprops=arrow_style)

    # 3. Feature Eng -> Model -> AML
    ax.annotate("", xy=(6.2, 5.3), xytext=(6.2, 5.8), arrowprops=arrow_style)
    ax.annotate("", xy=(6.2, 3.8), xytext=(6.2, 4.3), arrowprops=arrow_style)
    ax.annotate("", xy=(6.2, 2.3), xytext=(6.2, 2.8), arrowprops=arrow_style)

    # 4. Model -> ACR / ACI (Tier 2 to Tier 3)
    ax.annotate("", xy=(8.4, 6.3), xytext=(7.7, 4.8), arrowprops=arrow_style)
    ax.annotate("", xy=(9.9, 5.3), xytext=(9.9, 5.8), arrowprops=arrow_style)
    ax.annotate("", xy=(9.9, 3.8), xytext=(9.9, 4.3), arrowprops=arrow_style)
    ax.annotate("", xy=(9.9, 2.3), xytext=(9.9, 2.8), arrowprops=arrow_style)

    # 5. ACI -> Front Door -> React (Tier 3 to Tier 4)
    ax.annotate("", xy=(12.1, 6.3), xytext=(11.4, 4.8), arrowprops=arrow_style)
    ax.annotate("", xy=(13.6, 5.3), xytext=(13.6, 5.8), arrowprops=arrow_style)

    # Key Vault -> ACI (Secured credentials)
    ax.annotate("", xy=(11.4, 4.5), xytext=(12.1, 3.3), arrowprops=dict(arrowstyle="-|>", color=PURPLE_ACC, lw=1.8, linestyle="--", mutation_scale=12, zorder=6))

    # ACI -> App Insights
    ax.annotate("", xy=(12.1, 1.8), xytext=(11.4, 4.3), arrowprops=dict(arrowstyle="-|>", color=AZURE_BLUE, lw=1.8, linestyle=":", mutation_scale=12, zorder=6))

    # Bottom Legend
    leg_x = 0.8
    leg_y = 0.35
    ax.text(leg_x, leg_y, "Legend / Protocols:", fontsize=9.5, fontweight='bold', color=DARK_BLUE)
    ax.text(leg_x + 2.0, leg_y, "── Solid: Data Flow / Execution", fontsize=9, color=SLATE_MUTED)
    ax.text(leg_x + 5.2, leg_y, "-- Dashed: Secure Credential Retrieval", fontsize=9, color=PURPLE_ACC)
    ax.text(leg_x + 8.9, leg_y, "·· Dotted: APM Telemetry & Logs", fontsize=9, color=AZURE_BLUE)
    ax.text(15.2, leg_y, "Region: East US 2", fontsize=9, fontweight='bold', color=SLATE_DARK, ha='right')

    plt.tight_layout()
    plt.savefig(output_png, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Architecture diagram saved to: {output_png}")

if __name__ == "__main__":
    out_file = r"d:\All_projects\tomato_price_prediction\azure_system_architecture.png"
    draw_azure_architecture(out_file)

