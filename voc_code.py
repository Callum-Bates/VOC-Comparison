import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


df = pd.read_csv("voc_data.csv")
voc_counts = df['CHEMICAL'].value_counts()
print(voc_counts.head(10))

#Choose 5 VOCs based on frequency in data table
chemicals = ["Octanal", "Decanal", "Acetaldehyde", "Nonyl aldehyde (Nonanal)", "Cyclopentasiloxane, decamethyl"]
df_filtered = df[df['CHEMICAL'].isin(chemicals)]

# --- Get ratios function ---

def calculate_ratios(df_filtered):
    # Group by chemical and location, calculate mean concentration
    summary = df_filtered.groupby(['CHEMICAL', 'LOCATION'])['CONC'].agg(['mean', 'count']).reset_index()
    
    print("=== SUMMARY BY CHEMICAL AND LOCATION ===")
    print(summary)
    
    # get indoor and outdoor as separate columns
    pivot_data = summary.pivot_table(
        index='CHEMICAL', 
        columns='LOCATION', 
        values='mean'
    ).reset_index()
    
    print("\n=== PIVOT TABLE ===")
    print(pivot_data)
    
    # Calculate ratios if both indoor and outdoor data
    if 'Indoor' in pivot_data.columns and 'Outdoor' in pivot_data.columns:
        pivot_data['Indoor_Outdoor_Ratio'] = pivot_data['Indoor'] / pivot_data['Outdoor']
        pivot_data['Difference'] = pivot_data['Indoor'] - pivot_data['Outdoor']
        
        # Remove rows where don't have both indoor and outdoor data
        pivot_data = pivot_data.dropna(subset=['Indoor', 'Outdoor'])
        
        print("\n=== WITH RATIOS ===")
        print(pivot_data)
    
    return pivot_data

# Calculate the ratios
ratios_df = calculate_ratios(df_filtered)


# --- Clean data function ---

def prepare_dashboard_data(ratios_df):

    dashboard_data = ratios_df.copy()
    
    # Simplify chemical names 
    name_mapping = {
        "Octanal": "Octanal",
        "Acetaldehyde": "Acetaldehyde", 
        "Nonyl aldehyde (Nonanal)": "Nonanal",
        "Cyclopentasiloxane, decamethyl": "Siloxane D5"
    }
    
    dashboard_data['Chemical_Display'] = dashboard_data['CHEMICAL'].map(name_mapping).fillna(dashboard_data['CHEMICAL'])
    
    # ---- Guesstimated these based on brief reading ----
    def categorize_health_concern(chemical):
        if 'Octanal' in chemical:
            return 'High'
        elif 'Acetaldehyde' in chemical:
            return 'High'
        elif 'Decanal' in chemical or 'Nonanal' in chemical:
            return 'Medium'
        else:
            return 'Low'
    
    dashboard_data['Health_Concern'] = dashboard_data['CHEMICAL'].apply(categorize_health_concern)
    
    # Round values 
    dashboard_data['Indoor'] = dashboard_data['Indoor'].round(2)
    dashboard_data['Outdoor'] = dashboard_data['Outdoor'].round(2)
    dashboard_data['Indoor_Outdoor_Ratio'] = dashboard_data['Indoor_Outdoor_Ratio'].round(2)
    
    return dashboard_data



# Prepare final data
final_data = prepare_dashboard_data(ratios_df)



# --- Plot function ---

def create_basic_plots(final_data):

    # --- Plot 1: Indoor vs Outdoor concentrations ---

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        name='Indoor Average',
        x=final_data['Chemical_Display'],
        y=final_data['Indoor'],
        marker_color='red',
        text=final_data['Indoor'],
        textposition='auto'
    ))

    fig1.add_trace(go.Bar(
        name='Outdoor Average', 
        x=final_data['Chemical_Display'],
        y=final_data['Outdoor'],
        marker_color='blue',
        text=final_data['Outdoor'],
        textposition='auto'
    ))

    fig1.update_layout(
        title='Indoor vs Outdoor VOC Concentrations',
        xaxis_title='Volatile Organic Compounds',
        yaxis_title='Concentration (μg/m³)',
        barmode='group',
        height=500
    )


    # --- Plot 2: Indoor/Outdoor Ratios ---

    fig2 = px.bar(
        final_data, 
        x='Chemical_Display', 
        y='Indoor_Outdoor_Ratio',
        title='How Much Higher are Indoor VOC Levels?<br><sub>Indoor concentrations compared to outdoor</sub>',
        color='Health_Concern',
        color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'},
        text='Indoor_Outdoor_Ratio'
    )

    fig2.update_traces(texttemplate='%{text:.1f}x', textposition='outside')
    fig2.update_layout(
        height=500,
        xaxis_title="Volatile Organic Compounds (VOC)",
        yaxis_title="Indoor/Outdoor Ratio"
    )
    fig1.write_image("Indoor_vs_Outdoor.png", width=1200, height=600, scale=2)
    fig2.write_image("Indoor_Outdoor_Ratio.png", width=1200, height=600, scale=2)
    fig1.show(renderer="browser")
    fig2.show(renderer="browser")


    return fig1, fig2

# Create the plots
fig1, fig2 = create_basic_plots(final_data)

