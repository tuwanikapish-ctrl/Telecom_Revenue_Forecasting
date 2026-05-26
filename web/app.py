import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, render_template, redirect, url_for
import os
from src.pipeline import run_pipeline
from src.forecasting import run_forecast
import plotly.express as px

app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

UPLOAD_FOLDER = 'data/raw'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

import pandas as pd

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # ✅ Read file
    if file.filename.endswith('.csv'):
        df = pd.read_csv(filepath)

    elif file.filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(filepath)

    else:
        return "❌ Only CSV and Excel files are supported"
    # ✅ Clean column names
    df.columns = df.columns.str.strip().str.title()

    # ✅ Validate required columns
    required_cols = ['Date', 'Revenue']

    missing_columns = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_columns:
        return render_template(
        'index.html',
        error=f"Missing required column(s): {', '.join(missing_columns)}"
    )

    # ✅ Run pipeline only if valid
    run_pipeline(filepath)

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():

    df = pd.read_csv("data/processed/cleaned_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    # 🔥 CLEAN SERVICE COLUMN (IMPORTANT)
    if 'Service' in df.columns:
        df['Service'] = df['Service'].astype(str).str.strip().str.title()
    else:
        df['Service'] = "General"   # fallback if missing

    # 🔥 KEEP ORIGINAL
    df_original = df.copy()

    # 🔥 GET FILTER VALUE
    service = request.args.get('service')

    # 🔥 FILTER LOGIC
    if service:
        df = df_original[df_original['Service'] == service]
    else:
        df = df_original.groupby('Date')['Revenue'].sum().reset_index()

    # 🔥 REMOVE BAD VALUES
    df = df[df['Revenue'] > 100000]

    # =============================
    # 🔮 FORECAST (SAFE VERSION)
    # =============================
    try:
        if service:
            temp_path = "data/temp_filtered.csv"
            df_original[df_original['Service'] == service].to_csv(temp_path, index=False)
            forecast_df = run_forecast(temp_path)
        else:
            forecast_df = run_forecast("data/processed/cleaned_data.csv")

        forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])

    except Exception as e:
        print("Forecast skipped:", e)
        forecast_df = pd.DataFrame(columns=['Date', 'Forecast', 'Lower', 'Upper'])

    # =============================
    # 📊 KPI CALCULATIONS
    # =============================
    total_revenue = df['Revenue'].sum()
    avg_revenue = df['Revenue'].mean()
    highest_revenue = df['Revenue'].max()

    # Next month forecasted revenue
    if not forecast_df.empty:
        forecast_total_value = forecast_df['Forecast'].iloc[0]
    else:
        forecast_total_value = 0

    # Total services
    if 'Service' in df_original.columns:
        service_count_value = df_original['Service'].nunique()
    else:
        service_count_value = 1

    if len(df) > 1:
        latest = df.iloc[-1]['Revenue']
        previous = df.iloc[-2]['Revenue']
        growth = ((latest - previous) / previous) * 100 if previous != 0 else 0
    else:
        growth = 0

    # =============================
    # 🔗 CONNECT FORECAST
    # =============================
    if not forecast_df.empty:
        forecast_df = pd.concat([
            df.tail(1)[['Date', 'Revenue']].rename(columns={'Revenue': 'Forecast'}),
            forecast_df
        ], ignore_index=True)

        forecast_df['Lower'] = forecast_df['Lower'].clip(lower=0)
        forecast_df['Upper'] = forecast_df['Upper'].clip(upper=df['Revenue'].max() * 1.5)

    # =============================
    # 📈 COMBINE DATA
    # =============================
    actual_df = df[['Date', 'Revenue']].copy()
    actual_df['Type'] = 'Actual'

    if not forecast_df.empty:
        forecast_plot = forecast_df[['Date', 'Forecast']].rename(columns={'Forecast': 'Revenue'})
        forecast_plot['Type'] = 'Forecast'
        combined = pd.concat([actual_df, forecast_plot])
    else:
        combined = actual_df

    # =============================
    # 📊 PLOT
    # =============================
    fig = px.line(
        combined,
        x='Date',
        y='Revenue',
        color='Type',
        title='Revenue Trend'
    )

    # 🔥 CONFIDENCE BAND
    if not forecast_df.empty:
        fig.add_scatter(
            x=forecast_df['Date'],
            y=forecast_df['Upper'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        )

        fig.add_scatter(
            x=forecast_df['Date'],
            y=forecast_df['Lower'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(255,165,0,0.2)',
            line=dict(width=0),
            name='Confidence'
        )

    # =============================
    # 🎨 STYLING
    # =============================
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Date',
        yaxis_title='Revenue',
        title='Revenue Trend',
        title_x=0.05,
        height=650,
        yaxis=dict(range=[0, df['Revenue'].max() * 1.2]),
        legend=dict(
            orientation="h",
            y=1.15,
            x=0.5,
            xanchor="center"
        ),
        margin=dict(t=80)
    )

    graph_html = fig.to_html(full_html=False, config={'responsive': True})

    # =============================
    # 🔢 FORMATTING
    # =============================
    total = f"{total_revenue/1e6:.2f}M"
    avg = f"{avg_revenue/1e3:.2f}K"
    growth_value = round(growth, 2)
    highest = f"{highest_revenue/1e6:.2f}M"
    forecast_total = f"{forecast_total_value/1e6:.2f}M"
    service_count = f"{service_count_value}"

    # 🔥 FIX DROPDOWN SOURCE
    services = sorted(df_original['Service'].dropna().unique())

    return render_template(
    'dashboard.html',
    graph=graph_html,
    total=total,
    avg=avg,
    growth=growth_value,
    highest=highest,
    forecast_total=forecast_total,
    service_count=service_count,
    services=services,
    selected_service=service
)
if __name__ == '__main__':
    print("🚀 Flask is starting...")
    app.run(debug=False)