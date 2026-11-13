import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_azure_flowchart(output_png):
    # Set high DPI and canvas size
    fig, ax = plt.subplots(figsize=(9, 12), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Color definitions matching user's template
    CYAN_BLUE   = '#1E88E5'
    NAVY_BLUE   = '#1565C0'
    DARK_NAVY   = '#0D47A1'
    FOREST_GREEN = '#2E7D32'
    VIVID_PURPLE = '#7B1FA2'
    WARM_ORANGE  = '#E65100'

    # Node styling parameters
    box_w = 4.2
    box_h = 0.85
    center_x = 5.0

    # Helper function to draw rounded box with shadow & text
    def draw_box(x, y, w, h, bg_color, title, subtitle):
        # Drop shadow
        shadow = patches.FancyBboxPatch(
            (x - w/2 + 0.05, y - h/2 - 0.05), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor='#CBD5E1', edgecolor='none', alpha=0.6, zorder=2
        )
        ax.add_patch(shadow)

        # Main box
        rect = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=bg_color, edgecolor='#FFFFFF', linewidth=1.5, zorder=3
        )
        ax.add_patch(rect)

        # Main Title
        ax.text(
            x, y + 0.12, title,
            ha='center', va='center',
            color='white', fontsize=12, fontweight='bold',
            zorder=4, fontfamily='sans-serif'
        )
        # Subtitle
        ax.text(
            x, y - 0.18, subtitle,
            ha='center', va='center',
            color='#E2E8F0', fontsize=10, fontweight='normal',
            zorder=4, fontfamily='sans-serif'
        )

    # 1. Top Node: Historical Price Data
    draw_box(center_x, 11.8, box_w, box_h, CYAN_BLUE, "Historical Price Data", "(2023 - 2025 Karnataka Mandi CSVs)")

    # Line 1 -> 2
    ax.plot([center_x, center_x], [11.8 - box_h/2, 10.4 + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 2. Node: Azure Blob Storage
    draw_box(center_x, 10.4, box_w, box_h, DARK_NAVY, "Azure Blob Storage", "(raw-data container)")

    # Line 2 -> 3
    ax.plot([center_x, center_x], [10.4 - box_h/2, 9.0 + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 3. Node: ETL Preprocessing
    draw_box(center_x, 9.0, box_w, box_h, FOREST_GREEN, "ETL Preprocessing", "(data_preprocessing.py / 37 Features)")

    # Line 3 -> 4
    ax.plot([center_x, center_x], [9.0 - box_h/2, 7.6 + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 4. Node: Model Training
    draw_box(center_x, 7.6, box_w, box_h, VIVID_PURPLE, "Model Training", "(XGBoost Regressor: R² = 0.985)")

    # Fork connectors 4 -> 5a (left) and 4 -> 5b (right)
    split_w = 2.4
    left_x = center_x - 1.45
    right_x = center_x + 1.45
    split_y = 6.1

    ax.plot([center_x, left_x], [7.6 - box_h/2, split_y + box_h/2], color='#475569', lw=2.5, zorder=1)
    ax.plot([center_x, right_x], [7.6 - box_h/2, split_y + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 5a. Left Split Node: Azure Storage (Model Artifact)
    draw_box(left_x, split_y, split_w, box_h, WARM_ORANGE, "Azure Storage", "(best_model_latest.joblib)")

    # 5b. Right Split Node: Database Predictions
    draw_box(right_x, split_y, split_w, box_h, NAVY_BLUE, "Database Predictions", "(41 Mandi Daily JSON & DB)")

    # Line 5b -> 6
    ax.plot([right_x, right_x], [split_y - box_h/2, 4.7 + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 6. Node: API Backend (ACI)
    draw_box(right_x, 4.7, 3.4, box_h, FOREST_GREEN, "FastAPI Backend", "(Azure Container Instances - ACI)")

    # Line 6 -> 7
    ax.plot([right_x, right_x], [4.7 - box_h/2, 3.3 + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 7. Node: Azure Front Door
    draw_box(right_x, 3.3, 3.4, box_h, VIVID_PURPLE, "Azure Front Door", "(Global HTTPS CDN & Ingress)")

    # Line 7 -> 8
    ax.plot([right_x, right_x], [3.3 - box_h/2, 1.9 + box_h/2], color='#475569', lw=2.5, zorder=1)

    # 8. Node: React Frontend
    draw_box(right_x, 1.9, 3.4, box_h, CYAN_BLUE, "React Frontend Dashboard", "(Live Interactive Web UI)")

    # Header label top-left
    ax.text(0.5, 12.5, "RV College of Engineering®", fontsize=11, fontweight='bold', color='#1E293B', fontfamily='sans-serif')
    ax.text(0.5, 12.2, "Department of Master of Computer Applications", fontsize=9, color='#64748B', fontfamily='sans-serif')

    # Subtitle top-right
    ax.text(9.5, 12.5, "Azure Architecture Pipeline", fontsize=11, fontweight='bold', color='#0284C7', ha='right', fontfamily='sans-serif')
    ax.text(9.5, 12.2, "Automated Daily Tomato Price Forecasting", fontsize=9, color='#64748B', ha='right', fontfamily='sans-serif')

    plt.tight_layout()
    plt.savefig(output_png, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Flowchart successfully saved to: {output_png}")

if __name__ == "__main__":
    out_file = r"d:\All_projects\tomato_price_prediction\azure_pipeline_flowchart.png"
    draw_azure_flowchart(out_file)

