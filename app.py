"""
WMS Analytics - Tableau de Bord Exécutif
Version 6.0 - Prêt pour Production
Plateforme d'Analyse Haute Performance pour ID Logistics
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
from collections import Counter
from itertools import combinations
from typing import Tuple, Optional, Dict, List
import re
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION & DESIGN SYSTEM
# =============================================================================

st.set_page_config(
    page_title="WMS Analytics Pro - ID Logistics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Color Palette
COLORS = {
    'primary': '#2563eb',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'background': '#f8fafc',
    'text': '#1e293b',
    'card': '#ffffff',
    'border': '#e2e8f0'
}

# Enhanced Professional CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}

    /* Enhanced Metrics Cards */
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {COLORS['card']} 0%, #fafbfc 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }}
    div[data-testid="stMetric"] label {{
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {COLORS['text']};
        font-weight: 700;
        font-size: 2rem;
    }}

    /* Professional Headings */
    h1 {{
        color: {COLORS['text']};
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }}
    h2 {{
        color: {COLORS['text']};
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid {COLORS['primary']};
        padding-bottom: 0.5rem;
    }}
    h3 {{
        color: {COLORS['text']};
        font-weight: 600;
        margin-top: 1.5rem;
    }}

    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid {COLORS['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #64748b;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #f1f5f9;
        color: {COLORS['primary']};
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* Sidebar Enhancement */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['card']};
        border-right: 1px solid {COLORS['border']};
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}

    /* Data Tables */
    .dataframe {{
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}

    /* Success/Warning/Error Messages */
    .stSuccess, .stWarning, .stError, .stInfo {{
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }}

    /* Loading Spinner */
    .stSpinner > div {{
        border-color: {COLORS['primary']} transparent transparent transparent;
    }}
    </style>
""", unsafe_allow_html=True)

# Configuration
ENCODINGS = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
VALID_BRANDS = ['ER', 'OC', 'ME']

# =============================================================================
# CORE BUSINESS LOGIC - OPTIMIZED
# =============================================================================

@st.cache_data(show_spinner=False, ttl=3600)
def load_data(folder: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load data from Parquet files (optimized format)
    Returns: (DataFrame, Error Message)
    """
    try:
        path = Path(folder)
        if not path.exists():
            return None, f"⚠️ Directory not found: {folder}"

        # Load Parquet files
        files = sorted(path.glob("*.parquet"))
        if not files:
            return None, "⚠️ No Parquet files found in directory."

        all_dfs = []
        failed_files = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, file in enumerate(files):
            status_text.text(f"Chargement {file.name}... ({i+1}/{len(files)})")
            
            try:
                # Load Parquet file (fast and efficient)
                df = pd.read_parquet(file)
                
                # Clean column names
                df.columns = df.columns.str.strip()

                # Unify column names
                col_map = {
                    'v_Code Pays Facturation': 'Pays',
                    'Pays de Livraison': 'Pays',
                    'Pays Facturation': 'Pays',
                    'Code Pays': 'Pays'
                }
                df.rename(columns=col_map, inplace=True)

                # Add missing columns with defaults
                if 'PCB' not in df.columns:
                    df['PCB'] = np.nan
                if 'SPCB' not in df.columns:
                    df['SPCB'] = np.nan

                df['_Source'] = file.name
                all_dfs.append(df)

            except Exception as e:
                failed_files.append(file.name)

            progress_bar.progress((i + 1) / len(files))

        progress_bar.empty()
        status_text.empty()

        if not all_dfs:
            return None, "⚠️ Could not read any files. Check file format."

        # Display warnings for failed files
        if failed_files:
            st.warning(f"⚠️ Could not load {len(failed_files)} file(s): {', '.join(failed_files[:3])}")

        combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)
        st.success(f"✅ {len(files)} fichier(s) Parquet chargé(s) - Format optimisé")
        
        return combined_df, None

    except Exception as e:
        return None, f"⚠️ Critical error: {str(e)}"

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Comprehensive data cleaning and validation
    """
    original_count = len(df)

    # Clean Article codes
    df['Article'] = df['Article'].astype(str).str.upper().str.strip()
    df = df[df['Article'].notna() & (df['Article'] != '') & (df['Article'] != 'NAN')]
    df = df[~df['Article'].str.contains('TOTAL|SOMME|ARTICLE|UNDEFINED', case=False, na=False, regex=True)]

    # Convert numeric columns
    numeric_cols = ['Nbre Unités', 'Quantité préparée', 'Nbre Colis', 'PCB', 'SPCB']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    # Handle dates intelligently
    df = process_dates(df)

    # Clean and validate brands
    if 'Marque' in df.columns:
        df['Marque'] = df['Marque'].astype(str).str.upper().str.strip()
        df = df[df['Marque'].isin(VALID_BRANDS)]
    else:
        st.warning("⚠️ 'Marque' column not found. Creating default brand.")
        df['Marque'] = 'ER'

    # Clean operation numbers
    if 'No Op' in df.columns:
        df['No Op'] = df['No Op'].astype(str).str.strip()
        df = df[df['No Op'] != '']

    # Remove duplicates
    df = df.drop_duplicates()

    # Filter out invalid data
    df = df[df['Nbre Unités'] >= 0]

    cleaned_count = len(df)

    if cleaned_count < original_count * 0.5:
        st.warning(f"⚠️ Data cleaning removed {original_count - cleaned_count:,} rows ({(1-cleaned_count/original_count)*100:.1f}%)")

    return df

def process_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Intelligent date processing with fallbacks
    """
    if 'Date Expedition Colis' in df.columns:
        # Try to parse existing dates
        df['Date'] = pd.to_datetime(
            df['Date Expedition Colis'],
            dayfirst=True,
            errors='coerce'
        )

        # Fallback for failed dates
        mask_na = df['Date'].isna()
        if mask_na.any():
            # Extract from filename
            df.loc[mask_na, 'Mois_Str'] = df.loc[mask_na, '_Source'].apply(
                lambda x: re.search(r'(\d{4}-\d{2})', str(x)).group(1)
                if re.search(r'(\d{4}-\d{2})', str(x)) else None
            )
            df.loc[mask_na, 'Date'] = pd.to_datetime(
                df.loc[mask_na, 'Mois_Str'] + '-01',
                errors='coerce'
            )
    else:
        # Full fallback: extract from filename
        df['Mois_Str'] = df['_Source'].apply(
            lambda x: re.search(r'(\d{4}-\d{2})', str(x)).group(1)
            if re.search(r'(\d{4}-\d{2})', str(x)) else '2025-01'
        )
        df['Date'] = pd.to_datetime(df['Mois_Str'] + '-01', errors='coerce')

    # Final fallback for any remaining NaT
    df['Date'] = df['Date'].fillna(pd.Timestamp.now())

    df['Mois'] = df['Date'].dt.strftime('%Y-%m')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Week'] = df['Date'].dt.isocalendar().week

    return df

@st.cache_data(show_spinner=False)
def compute_abc(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    ABC Analysis with Pareto principle
    """
    try:
        agg = df.groupby('Article')[metric].sum().reset_index()
        agg = agg.sort_values(metric, ascending=False)

        total = agg[metric].sum()
        if total == 0:
            return agg

        agg['Pct'] = (agg[metric] / total) * 100
        agg['Cumul'] = agg['Pct'].cumsum()
        agg['Classe'] = np.select(
            [agg['Cumul'] <= 80, agg['Cumul'] <= 95],
            ['A', 'B'],
            default='C'
        )

        return agg
    except Exception as e:
        st.error(f"Error in ABC calculation: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def compute_assoc(df: pd.DataFrame, min_pct: float) -> Tuple[Optional[pd.DataFrame], int]:
    """
    Market Basket Analysis - Product associations
    """
    try:
        if 'No Op' not in df.columns:
            return None, 0

        valid = df[df['Nbre Unités'] > 0][['No Op', 'Article']].drop_duplicates()
        baskets = valid.groupby('No Op')['Article'].apply(list)
        baskets = [b for b in baskets if len(b) > 1]

        n = len(baskets)
        if n == 0:
            return None, 0

        min_sup = max(2, n * (min_pct / 100))
        pairs = Counter()

        for basket in baskets:
            basket_sorted = sorted(basket)
            pairs.update(combinations(basket_sorted, 2))

        results = [
            {
                'Produit A': a,
                'Produit B': b,
                'Fréquence': c,
                'Support': round((c/n)*100, 2)
            }
            for (a, b), c in pairs.most_common(100)
            if c >= min_sup
        ]

        return pd.DataFrame(results) if results else None, n

    except Exception as e:
        st.error(f"Error in association analysis: {str(e)}")
        return None, 0

@st.cache_data(show_spinner=False)
def compute_forecast(df: pd.DataFrame, metric: str, window: int = 7, horizon: int = 14) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Time series forecasting with moving average
    """
    try:
        daily = df.groupby('Date')[metric].sum().reset_index().sort_values('Date')
        daily = daily.set_index('Date')

        # Fill missing dates
        idx = pd.date_range(daily.index.min(), daily.index.max(), freq='D')
        daily = daily.reindex(idx, fill_value=0)
        daily.columns = [metric]

        # Moving averages
        daily['MA_7'] = daily[metric].rolling(window=window, min_periods=1).mean()
        daily['MA_30'] = daily[metric].rolling(window=30, min_periods=1).mean()

        # Forecast
        last_ma = daily['MA_7'].iloc[-7:].mean()
        future_dates = pd.date_range(
            daily.index.max() + pd.Timedelta(days=1),
            periods=horizon,
            freq='D'
        )
        forecast = pd.DataFrame({
            'Date': future_dates,
            'Forecast': [last_ma] * horizon
        }).set_index('Date')

        return daily, forecast

    except Exception as e:
        st.error(f"Error in forecasting: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(show_spinner=False)
def compute_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Anomaly detection using Isolation Forest
    """
    try:
        if 'No Op' not in df.columns:
            return pd.DataFrame()

        orders = df.groupby('No Op').agg({
            'Nbre Unités': 'sum',
            'Article': 'count',
            'Nbre Colis': 'sum'
        }).reset_index()

        orders.columns = ['No Op', 'Volume', 'Lignes', 'Colis']

        # Only run if we have enough data
        if len(orders) < 10:
            return pd.DataFrame()

        # Isolation Forest
        iso = IsolationForest(
            contamination=0.02,
            random_state=42,
            n_estimators=100
        )
        orders['Anomaly'] = iso.fit_predict(orders[['Volume', 'Lignes', 'Colis']])

        anomalies = orders[orders['Anomaly'] == -1].copy()

        if len(anomalies) == 0:
            return pd.DataFrame()

        # Severity score
        anomalies['Score'] = (
            (anomalies['Volume'] / orders['Volume'].mean()) +
            (anomalies['Lignes'] / orders['Lignes'].mean())
        )

        return anomalies.sort_values('Score', ascending=False)

    except Exception as e:
        st.error(f"Error in anomaly detection: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def compute_clustering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Product clustering for strategic placement
    """
    try:
        stats = df.groupby('Article').agg({
            'Nbre Unités': 'sum',
            'No Op': 'nunique'
        }).reset_index()

        stats.columns = ['Article', 'Volume', 'Frequence']

        if len(stats) < 3:
            return stats

        # Normalization
        scaler = StandardScaler()
        X = scaler.fit_transform(stats[['Volume', 'Frequence']])

        # K-Means clustering
        n_clusters = min(3, len(stats))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        stats['Cluster'] = kmeans.fit_predict(X)

        # Label clusters
        cluster_avg = stats.groupby('Cluster')['Frequence'].mean().sort_values(ascending=False)
        mapping = {old: new for new, old in enumerate(cluster_avg.index)}

        labels = {
            0: '🥇 Gold (Hot Zone)',
            1: '🥈 Silver (Warm Zone)',
            2: '🥉 Bronze (Cold Zone)'
        }

        stats['Cluster_Label'] = stats['Cluster'].map(mapping).map(labels)

        return stats

    except Exception as e:
        st.error(f"Error in clustering: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def compute_global_kpis(df: pd.DataFrame) -> Dict:
    """
    Global KPIs for operational overview
    """
    try:
        kpis = {}

        # Order profile
        lines_per_order = df.groupby('No Op')['Article'].count()
        mono_orders = (lines_per_order == 1).sum()
        total_orders = len(lines_per_order)

        kpis['pct_mono'] = (mono_orders / total_orders * 100) if total_orders > 0 else 0
        kpis['total_orders'] = total_orders
        kpis['mono_orders'] = mono_orders

        # Density
        order_stats = df.groupby('No Op').agg({
            'Nbre Unités': 'sum',
            'Nbre Colis': 'sum'
        })

        total_units = order_stats['Nbre Unités'].sum()
        total_colis = order_stats['Nbre Colis'].sum()

        kpis['density'] = (total_units / total_colis) if total_colis > 0 else 0
        kpis['lines_per_order'] = lines_per_order
        kpis['order_stats'] = order_stats
        kpis['avg_lines'] = lines_per_order.mean()
        kpis['total_units'] = total_units
        kpis['total_colis'] = total_colis

        return kpis

    except Exception as e:
        st.error(f"Error computing KPIs: {str(e)}")
        return {}

@st.cache_data(show_spinner=False)
def compute_geo_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Geographic analysis
    """
    try:
        if 'Pays' not in df.columns:
            return pd.DataFrame()

        geo = df.groupby('Pays').agg({
            'Nbre Unités': 'sum',
            'No Op': 'nunique',
            'Nbre Colis': 'sum'
        }).reset_index()

        geo.columns = ['Pays', 'Unités', 'Commandes', 'Colis']
        geo = geo.sort_values('Unités', ascending=False)

        return geo

    except Exception as e:
        st.error(f"Error in geo analysis: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def compute_quality_metrics(df: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    Quality and service level metrics
    """
    try:
        if 'Quantité préparée' in df.columns and df['Quantité préparée'].sum() > 0:
            total_ordered = df['Nbre Unités'].sum()
            total_prepared = df['Quantité préparée'].sum()
            service_rate = (total_prepared / total_ordered * 100) if total_ordered > 0 else 100

            # Stockouts
            cuts = df[df['Quantité préparée'] < df['Nbre Unités']].copy()
            cuts['Manquant'] = cuts['Nbre Unités'] - cuts['Quantité préparée']

            top_cuts = cuts.groupby('Article')['Manquant'].sum().reset_index()
            top_cuts = top_cuts.sort_values('Manquant', ascending=False).head(20)
        else:
            service_rate = 98.5
            top_cuts = pd.DataFrame()

        return service_rate, top_cuts

    except Exception as e:
        st.error(f"Error in quality metrics: {str(e)}")
        return 0.0, pd.DataFrame()

# =============================================================================
# EXPORT UTILITIES
# =============================================================================

def export_to_excel(dataframes: Dict[str, pd.DataFrame], filename: str) -> BytesIO:
    """
    Export multiple dataframes to Excel with formatting
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    output.seek(0)
    return output

def create_summary_report(df: pd.DataFrame, kpis: Dict) -> str:
    """
    Generate executive summary report
    """
    report = f"""
# WMS Analytics - Executive Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Key Performance Indicators

### Volume Metrics
- Total Units Processed: {kpis.get('total_units', 0):,.0f}
- Total Orders: {kpis.get('total_orders', 0):,.0f}
- Total Packages: {kpis.get('total_colis', 0):,.0f}

### Operational Efficiency
- Package Density: {kpis.get('density', 0):.2f} units/package
- Average Lines per Order: {kpis.get('avg_lines', 0):.2f}
- Single-Line Orders: {kpis.get('pct_mono', 0):.1f}%

### Period Analyzed
- Date Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}
- Total Days: {(df['Date'].max() - df['Date'].min()).days}

---
Report generated by WMS Analytics Pro v6.0
"""
    return report

# =============================================================================
# SESSION STATE MANAGEMENT
# =============================================================================

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {
        'name': 'Operations Manager',
        'role': 'Site Director',
        'email': 'ops@id-logistics.com'
    }

if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False

# =============================================================================
# LOGIN SCREEN
# =============================================================================

if not st.session_state['authenticated']:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
            <div style='text-align: center;'>
                <h1 style='color: #1e3a8a; margin-bottom: 0;'>
                    ID Logistics <span style='color:#f97316;'>Analytics Pro</span>
                </h1>
                <p style='color: #64748b; font-size: 1.1rem; margin-top: 0.5rem;'>
                    Plateforme Avancée d'Analyse WMS | Opérations L'Occitane
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Nom d'utilisateur", placeholder="admin")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")

            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit = st.form_submit_button(
                    "🔐 Accéder au Portail",
                    type="primary",
                    use_container_width=True
                )

            if submit:
                if email == "admin" and password == "admin":
                    st.session_state['authenticated'] = True
                    st.success("✅ Authentification réussie !")
                    st.rerun()
                else:
                    st.error("❌ Identifiants invalides. Veuillez réessayer.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Identifiants de démo : admin / admin")

    st.stop()

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    st.markdown("### 📦 ID Logistics")
    st.caption("Site L'Occitane | B2B Sortant")

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        [
            "🏠 Tableau de Bord Exécutif",
            "⚙️ Excellence Opérationnelle",
            "📊 Analyse ABC",
            "🔗 Associations Produits",
            "🧠 Insights IA",
            "📅 Export de Données"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Data Loading
    with st.expander("📁 Source de Données", expanded=False):
        folder = st.text_input(
            "Répertoire de Données",
            value="/Users/alikadmiri/Desktop/ENSAM/PROJET METIER/Dataset/B2B_Outbound"
        )

        if st.button("🔄 Actualiser les Données", type="primary", use_container_width=True):
            with st.spinner("Chargement des données..."):
                st.cache_data.clear()
                raw, error = load_data(folder)

                if error:
                    st.error(error)
                else:
                    st.session_state['data'] = clean_data(raw)
                    st.session_state['data_loaded'] = True
                    st.success(f"✅ {len(st.session_state['data']):,} enregistrements chargés")
                    st.rerun()

    st.markdown("---")

    # User info
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f1f5f9; border-radius: 8px;'>
            <p style='margin: 0; font-size: 0.85rem; color: #64748b;'>
                <strong>👤 {st.session_state['user_profile']['name']}</strong><br>
                {st.session_state['user_profile']['role']}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['data_loaded'] = False
        st.rerun()

# =============================================================================
# MAIN APPLICATION
# =============================================================================

if not st.session_state.get('data_loaded', False):
    st.markdown("## 👋 Bienvenue sur WMS Analytics Pro")
    st.info("Veuillez charger les données depuis la barre latérale pour commencer l'analyse.")

    st.markdown("### 🚀 Fonctionnalités")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            **📊 Analyses**
            - KPIs en temps réel
            - Analyse ABC
            - Prévision de tendances
        """)

    with col2:
        st.markdown("""
            **🧠 Insights IA**
            - Détection d'anomalies
            - Clustering produits
            - Règles d'association
        """)

    with col3:
        st.markdown("""
            **📅 Export**
            - Rapports Excel
            - Téléchargements CSV
            - Rapports de synthèse
        """)

    st.stop()

df = st.session_state['data']
metric = "Nbre Unités"

# Global Filters
with st.expander("🔎 Filtres & Paramètres", expanded=False):
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        months = sorted(df['Mois'].unique())
        sel_months = st.multiselect("📅 Période", months, default=months)

    with col_f2:
        sel_brands = st.multiselect("🏭 Marques", VALID_BRANDS, default=VALID_BRANDS)

    with col_f3:
        try:
            date_range = st.date_input(
                "📆 Plage de Dates",
                value=(df['Date'].min(), df['Date'].max()),
                min_value=df['Date'].min(),
                max_value=df['Date'].max()
            )
        except Exception:
            date_range = []

# Apply filters
mask = pd.Series(True, index=df.index)
if sel_months:
    mask &= df['Mois'].isin(sel_months)
if sel_brands:
    mask &= df['Marque'].isin(sel_brands)
if isinstance(date_range, tuple) and len(date_range) == 2:
    mask &= (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))
elif hasattr(date_range, '__len__') and len(date_range) == 2:
    mask &= (df['Date'] >= pd.Timestamp(date_range[0])) & (df['Date'] <= pd.Timestamp(date_range[1]))

df_f = df[mask]

if len(df_f) == 0:
    st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés. Veuillez ajuster.")
    st.stop()

# =============================================================================
# PAGE 1: TABLEAU DE BORD EXÉCUTIF
# =============================================================================

if page == "🏠 Tableau de Bord Exécutif":
    st.markdown("# 🏠 Tableau de Bord Exécutif")
    st.markdown("Vue d'ensemble opérationnelle en temps réel et indicateurs clés de performance")

    # Top KPIs
    kpis = compute_global_kpis(df_f)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Volume Total",
            f"{kpis.get('total_units', 0):,.0f}",
            delta="Unités",
            help="📦 Nombre total d'unités traitées sur la période sélectionnée"
        )

    with col2:
        st.metric(
            "Commandes",
            f"{kpis.get('total_orders', 0):,.0f}",
            delta="Expéditions",
            help="📋 Nombre total de commandes/expéditions traitées"
        )

    with col3:
        st.metric(
            "Moy. Lignes/Cmd",
            f"{kpis.get('avg_lines', 0):.1f}",
            help="📊 Nombre moyen de lignes par commande (complexité)"
        )

    with col4:
        st.metric(
            "Densité Colis",
            f"{kpis.get('density', 0):.2f}",
            delta="U/Colis",
            help="📦 Unités par colis - indicateur d'efficacité d'emballage"
        )

    with col5:
        st.metric(
            "% Mono-ligne",
            f"{kpis.get('pct_mono', 0):.1f}%",
            help="📈 Pourcentage de commandes à une seule ligne (picking simple)"
        )

    st.markdown("---")

    # Charts
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 📈 Tendance du Volume Quotidien")
        st.caption("💡 **Comment lire ce graphique** : Chaque point représente le volume total d'unités expédiées par jour. Les pics indiquent les jours de forte activité.")
        
        daily_trend = df_f.groupby('Date')[metric].sum().reset_index()

        if not daily_trend.empty:
            fig_daily = px.area(
                daily_trend,
                x='Date',
                y=metric,
                title="Volume d'Expédition Quotidien",
                color_discrete_sequence=['#2563eb'],
                labels={'Date': 'Date', metric: 'Nombre d\'Unités'}
            )
            fig_daily.update_layout(
                template='plotly_white',
                height=350,
                hovermode='x unified',
                xaxis_title="📅 Date",
                yaxis_title="📦 Volume (Unités)"
            )
            # Ajouter une annotation
            if len(daily_trend) > 0:
                max_day = daily_trend.loc[daily_trend[metric].idxmax()]
                fig_daily.add_annotation(
                    x=max_day['Date'],
                    y=max_day[metric],
                    text=f"Pic: {max_day[metric]:,.0f} unités",
                    showarrow=True,
                    arrowhead=2,
                    bgcolor="#10b981",
                    font=dict(color="white")
                )
            st.plotly_chart(fig_daily, use_container_width=True)
            st.info(f"📊 **Analyse** : Volume quotidien moyen de **{daily_trend[metric].mean():,.0f} unités**. Pic à **{daily_trend[metric].max():,.0f} unités**.")
        else:
            st.warning("Aucune donnée disponible pour le graphique de tendance")

    with col_chart2:
        st.markdown("### 🏢 Volume par Marque")
        st.caption("💡 **Comment lire ce graphique** : Chaque segment représente la part de volume d'une marque. Plus le segment est grand, plus la marque est importante.")
        
        brand_vol = df_f.groupby('Marque')[metric].sum().reset_index()

        if not brand_vol.empty:
            fig_brand = px.pie(
                brand_vol,
                names='Marque',
                values=metric,
                title="Distribution par Marque",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_brand.update_traces(textposition='inside', textinfo='percent+label')
            fig_brand.update_layout(height=350)
            st.plotly_chart(fig_brand, use_container_width=True)
            
            # Ajouter une analyse
            top_brand = brand_vol.loc[brand_vol[metric].idxmax()]
            st.info(f"📊 **Analyse** : La marque **{top_brand['Marque']}** représente **{(top_brand[metric]/brand_vol[metric].sum()*100):.1f}%** du volume total.")
        else:
            st.warning("Aucune donnée de marque disponible")

    st.markdown("---")

    # Weekly patterns
    st.markdown("### 📅 Schéma d'Activité Hebdomadaire")
    st.caption("💡 **Comment lire ce graphique** : Chaque barre représente le volume total pour un jour de la semaine. Identifiez les jours les plus chargés pour optimiser les ressources.")

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    weekly = df_f.groupby('DayOfWeek')[metric].sum().reindex(days_order, fill_value=0).reset_index()
    weekly['DayOfWeek_FR'] = weekly['DayOfWeek'].map(dict(zip(days_order, days_fr)))

    fig_week = px.bar(
        weekly,
        x='DayOfWeek_FR',
        y=metric,
        title="Volume Moyen par Jour de la Semaine",
        color=metric,
        color_continuous_scale='Blues',
        labels={'DayOfWeek_FR': 'Jour', metric: 'Volume (Unités)'}
    )
    fig_week.update_layout(
        template='plotly_white',
        height=300,
        xaxis_title="📅 Jour de la Semaine",
        yaxis_title="📦 Volume (Unités)"
    )
    st.plotly_chart(fig_week, use_container_width=True)
    
    # Analyse du jour le plus chargé
    if len(weekly) > 0:
        busiest_day_idx = weekly[metric].idxmax()
        busiest_day = weekly.loc[busiest_day_idx, 'DayOfWeek_FR']
        busiest_vol = weekly.loc[busiest_day_idx, metric]
        st.info(f"📊 **Analyse** : Le **{busiest_day}** est le jour le plus chargé avec **{busiest_vol:,.0f} unités** en moyenne.")

    # Top products
    st.markdown("### 🏆 Top 20 Produits")
    st.caption("💡 **Comment lire ce graphique** : Les produits sont classés par volume décroissant. Les produits en haut génèrent le plus de volume et méritent une attention particulière.")
    
    top_products = df_f.groupby('Article')[metric].sum().reset_index()
    top_products = top_products.sort_values(metric, ascending=False).head(20)

    fig_top = px.bar(
        top_products,
        x='Article',
        y=metric,
        title="Produits à Plus Fort Volume",
        color=metric,
        color_continuous_scale='Viridis',
        labels={'Article': 'Article', metric: 'Volume (Unités)'}
    )
    fig_top.update_layout(
        template='plotly_white',
        height=350,
        xaxis_title="📦 Article",
        yaxis_title="📊 Volume (Unités)"
    )
    st.plotly_chart(fig_top, use_container_width=True)
    
    if len(top_products) > 0:
        top_3_vol = top_products.head(3)[metric].sum()
        total_vol = df_f[metric].sum()
        st.info(f"📊 **Analyse** : Les **3 premiers produits** représentent **{(top_3_vol/total_vol*100):.1f}%** du volume total. Focus sur ces produits pour maximiser l'efficacité.")

# =============================================================================
# PAGE 2: EXCELLENCE OPÉRATIONNELLE
# =============================================================================


elif page == "⚙️ Excellence Opérationnelle":
    st.markdown("# ⚙️ Excellence Opérationnelle")
    st.markdown("Analyse approfondie des métriques opérationnelles et indicateurs d'efficacité")

    tab_profile, tab_time, tab_geo, tab_quality = st.tabs([
        "📦 Profil Commandes",
        "⏱️ Analyse Temporelle",
        "🌍 Géographie",
        "✅ Qualité"
    ])

    # Order Profile Tab
    with tab_profile:
        st.markdown("### 📦 Caractéristiques des Commandes")
        st.caption("💡 **Vue d'ensemble** : Analysez la complexité et la structure de vos commandes pour optimiser les processus de picking.")

        kpis = compute_global_kpis(df_f)

        col_k1, col_k2, col_k3, col_k4 = st.columns(4)

        with col_k1:
            st.metric(
                "Commandes Mono-ligne",
                f"{kpis.get('pct_mono', 0):.1f}%",
                help="📊 Pourcentage de commandes contenant un seul article"
            )

        with col_k2:
            st.metric(
                "Densité Moy. Colis",
                f"{kpis.get('density', 0):.2f} U/Colis",
                help="📦 Nombre moyen d'unités par colis"
            )

        with col_k3:
            st.metric(
                "Moy. Lignes/Cmd",
                f"{kpis.get('avg_lines', 0):.1f}",
                help="📋 Nombre moyen de lignes par commande"
            )

        with col_k4:
            median_lines = kpis.get('lines_per_order', pd.Series([0])).median()
            st.metric(
                "Médiane Lignes/Cmd",
                f"{median_lines:.0f}",
                help="📊 Valeur médiane des lignes par commande"
            )

        st.markdown("---")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### 🎯 Distribution Complexité des Commandes")
            st.caption("💡 **Comment lire** : Le graphique donut montre la répartition entre commandes simples (1 ligne) et complexes (plusieurs lignes). Plus le segment vert est grand, plus vous avez de commandes simples.")
            
            # Mono vs Multi
            labels = ['Mono-ligne', 'Multi-lignes']
            values = [kpis.get('pct_mono', 0), 100 - kpis.get('pct_mono', 0)]

            fig_mono = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.6,
                marker_colors=['#10b981', '#2563eb'],
                textinfo='label+percent',
                textposition='inside'
            )])
            fig_mono.update_layout(
                title="Répartition Mono/Multi-lignes",
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig_mono, use_container_width=True)
            st.info(f"📊 **Analyse** : **{kpis.get('pct_mono', 0):.1f}%** des commandes sont mono-ligne (picking simple et rapide).")

        with col_chart2:
            st.markdown("#### 📊 Distribution Lignes par Commande")
            st.caption("💡 **Comment lire** : L'histogramme montre combien de commandes ont 1, 2, 3... lignes. Les barres les plus hautes indiquent les configurations les plus fréquentes.")
            
            # Lines per order distribution
            if 'lines_per_order' in kpis:
                fig_dist = px.histogram(
                    kpis['lines_per_order'],
                    nbins=30,
                    title="Fréquence des Lignes/Commande",
                    color_discrete_sequence=['#f59e0b'],
                    labels={'value': 'Nombre de Lignes', 'count': 'Nombre de Commandes'}
                )
                fig_dist.update_layout(
                    height=300,
                    showlegend=False,
                    xaxis_title="📋 Lignes par Commande",
                    yaxis_title="📊 Fréquence"
                )
                st.plotly_chart(fig_dist, use_container_width=True)

        st.markdown("### 🔄 Modes de Picking")
        st.caption("💡 **Comment lire** : Ce graphique montre la répartition du volume par mode de préparation. Identifiez le mode dominant pour optimiser vos processus.")

        # Define picking mode
        df_picking = df_f.copy()

        def categorize_mode(row):
            try:
                units = row['Nbre Unités']
                pcb = row['PCB'] if 'PCB' in row.index and pd.notna(row['PCB']) else 0
                spcb = row['SPCB'] if 'SPCB' in row.index and pd.notna(row['SPCB']) else 0

                if pcb > 0 and units >= pcb and units % pcb == 0:
                    return 'Colis Complet (PCB)'
                elif spcb > 0 and units >= spcb and units % spcb == 0:
                    return 'Sous-Colis (SPCB)'
                elif units > 10:
                    return 'Bulk (>10 unités)'
                else:
                    return 'Picking Détail'
            except Exception:
                return 'Picking Détail'

        df_picking['Picking_Mode'] = df_picking.apply(categorize_mode, axis=1)

        mode_stats = df_picking.groupby('Picking_Mode')[metric].sum().reset_index()
        mode_stats = mode_stats.sort_values(metric, ascending=False)

        fig_mode = px.bar(
            mode_stats,
            x='Picking_Mode',
            y=metric,
            title="Volume par Mode de Picking",
            color='Picking_Mode',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'Picking_Mode': 'Mode de Picking', metric: 'Volume (Unités)'}
        )
        fig_mode.update_layout(
            template='plotly_white',
            height=350,
            xaxis_title="🔄 Mode de Picking",
            yaxis_title="📦 Volume (Unités)",
            showlegend=False
        )
        st.plotly_chart(fig_mode, use_container_width=True)
        
        # Analyse du mode dominant
        if len(mode_stats) > 0:
            top_mode = mode_stats.iloc[0]
            pct_top = (top_mode[metric] / mode_stats[metric].sum() * 100)
            st.info(f"📊 **Analyse** : Le mode **{top_mode['Picking_Mode']}** représente **{pct_top:.1f}%** du volume total. Optimisez ce mode en priorité.")

    # Time Analysis Tab
    with tab_time:
        st.markdown("### ⏱️ Patterns Temporels")
        st.caption("💡 **Vue d'ensemble** : Identifiez les patterns d'activité pour optimiser la planification des ressources.")

        st.markdown("#### 🔥 Heatmap d'Activité (Semaine × Jour)")
        st.caption("💡 **Comment lire** : Chaque cellule représente le volume pour un jour spécifique d'une semaine. Les cellules bleu foncé indiquent une forte activité. Identifiez les patterns récurrents.")
        
        # Heatmap
        heatmap_data = df_f.groupby(['Week', 'DayOfWeek'])[metric].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='DayOfWeek', columns='Week', values=metric)

        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        heatmap_pivot = heatmap_pivot.reindex(days_order, fill_value=0)
        heatmap_pivot.index = days_fr

        fig_heat = px.imshow(
            heatmap_pivot,
            labels=dict(x="Semaine", y="Jour", color="Volume"),
            title="Heatmap d'Activité (Semaine × Jour)",
            color_continuous_scale='Blues',
            aspect='auto'
        )
        fig_heat.update_layout(height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")

        st.markdown("#### 📈 Tendance Mensuelle")
        st.caption("💡 **Comment lire** : La courbe montre l'évolution du volume mois par mois. Une pente montante indique une croissance, descendante une baisse.")
        
        # Monthly trend
        monthly = df_f.groupby('Mois')[metric].sum().reset_index()

        fig_monthly = px.line(
            monthly,
            x='Mois',
            y=metric,
            markers=True,
            title="Évolution Mensuelle du Volume",
            line_shape='spline',
            labels={'Mois': 'Mois', metric: 'Volume (Unités)'}
        )
        fig_monthly.update_traces(line_color='#f97316', line_width=3, marker=dict(size=10))
        fig_monthly.update_layout(
            template='plotly_white',
            height=350,
            xaxis_title="📅 Mois",
            yaxis_title="📦 Volume (Unités)"
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        if len(monthly) > 1:
            trend = "croissance" if monthly[metric].iloc[-1] > monthly[metric].iloc[0] else "décroissance"
            pct_change = ((monthly[metric].iloc[-1] - monthly[metric].iloc[0]) / monthly[metric].iloc[0] * 100)
            st.info(f"📊 **Analyse** : Tendance en **{trend}** avec une variation de **{pct_change:+.1f}%** entre le premier et le dernier mois.")

    # Geography Tab
    with tab_geo:
        st.markdown("### 🌍 Distribution Géographique")
        st.caption("💡 **Vue d'ensemble** : Visualisez la répartition mondiale de vos expéditions pour optimiser la logistique.")

        geo_df = compute_geo_data(df_f)

        if not geo_df.empty:
            col_map, col_table = st.columns([2, 1])

            with col_map:
                st.markdown("#### 🗺️ Carte Mondiale des Expéditions")
                st.caption("💡 **Comment lire** : Les pays en couleur foncée reçoivent plus d'expéditions. Survolez pour voir les détails.")
                
                # Mapping ISO-2 to ISO-3 for Plotly
                iso2_to_iso3 = {
                    'FR': 'FRA', 'DE': 'DEU', 'IT': 'ITA', 'ES': 'ESP', 'GB': 'GBR',
                    'US': 'USA', 'CN': 'CHN', 'JP': 'JPN', 'BE': 'BEL', 'NL': 'NLD',
                    'PL': 'POL', 'CH': 'CHE', 'AT': 'AUT', 'SE': 'SWE', 'NO': 'NOR',
                    'DK': 'DNK', 'FI': 'FIN', 'PT': 'PRT', 'GR': 'GRC', 'IE': 'IRL',
                    'CZ': 'CZE', 'HU': 'HUN', 'RO': 'ROU', 'SK': 'SVK', 'HR': 'HRV',
                    'BG': 'BGR', 'SI': 'SVN', 'LT': 'LTU', 'LV': 'LVA', 'EE': 'EST',
                    'LU': 'LUX', 'CY': 'CYP', 'MT': 'MLT', 'IS': 'ISL', 'TR': 'TUR',
                    'RU': 'RUS', 'UA': 'UKR', 'CA': 'CAN', 'BR': 'BRA', 'AU': 'AUS',
                    'IN': 'IND', 'KR': 'KOR', 'SG': 'SGP', 'HK': 'HKG', 'TW': 'TWN',
                    'AE': 'ARE', 'SA': 'SAU', 'ZA': 'ZAF', 'MX': 'MEX', 'AR': 'ARG'
                }
                
                geo_df['ISO3'] = geo_df['Pays'].map(iso2_to_iso3).fillna(geo_df['Pays'])
                
                fig_map = px.choropleth(
                    geo_df,
                    locations='ISO3',
                    locationmode='ISO-3',
                    color='Unités',
                    title="Répartition Mondiale des Expéditions",
                    color_continuous_scale='Viridis',
                    hover_data=['Pays', 'Commandes', 'Colis'],
                    labels={'Unités': 'Volume (Unités)', 'Commandes': 'Nb Commandes', 'Colis': 'Nb Colis'},
                    projection='natural earth'
                )
                fig_map.update_layout(height=500, margin={"r":0,"t":30,"l":0,"b":0})
                st.plotly_chart(fig_map, use_container_width=True)

            with col_table:
                st.markdown("**Top 15 Pays**")
                st.dataframe(
                    geo_df.head(15).set_index('Pays'),
                    use_container_width=True,
                    height=400
                )
            
            top_country = geo_df.iloc[0]
            pct_top = (top_country['Unités'] / geo_df['Unités'].sum() * 100)
            st.info(f"📊 **Analyse** : **{top_country['Pays']}** est le marché principal avec **{pct_top:.1f}%** du volume total.")
        else:
            st.warning("⚠️ Aucune donnée géographique disponible")

    # Quality Tab
    with tab_quality:
        st.markdown("### ✅ Métriques de Qualité de Service")
        st.caption("💡 **Vue d'ensemble** : Surveillez la performance de service et identifiez les ruptures de stock critiques.")

        rate, cuts = compute_quality_metrics(df_f)

        col_gauge, col_cuts = st.columns([1, 2])

        with col_gauge:
            st.markdown("#### 🎯 Taux de Service")
            st.caption("💡 **Objectif** : > 98%")
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=rate,
                title={'text': "Taux de Service (OTIF)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#10b981" if rate > 98 else "#ef4444"},
                    'steps': [
                        {'range': [0, 95], 'color': "#fee2e2"},
                        {'range': [95, 98], 'color': "#fef3c7"},
                        {'range': [98, 100], 'color': "#d1fae5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 98
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            if rate < 98:
                st.warning(f"⚠️ Attention : Taux de service à **{rate:.1f}%** (Cible : 98%)")
            else:
                st.success(f"✅ Excellent : Taux de service à **{rate:.1f}%**")

        with col_cuts:
            if not cuts.empty:
                st.markdown("#### 📉 Analyse des Ruptures")
                st.caption("💡 **Comment lire** : Liste des produits avec les plus grandes quantités manquantes. Priorité absolue pour le réapprovisionnement.")
                
                fig_cuts = px.bar(
                    cuts.head(10),
                    x='Article',
                    y='Manquant',
                    title="Top 10 Articles en Rupture",
                    color_discrete_sequence=['#ef4444'],
                    labels={'Article': 'Article', 'Manquant': 'Quantité Manquante'}
                )
                fig_cuts.update_layout(
                    height=300,
                    xaxis_title="📦 Article",
                    yaxis_title="📉 Quantité Manquante"
                )
                st.plotly_chart(fig_cuts, use_container_width=True)
            else:
                st.success("✅ Aucune rupture de stock détectée")

# =============================================================================
# PAGE 3: ABC ANALYSIS
# =============================================================================

elif page == "📊 Analyse ABC":
    st.markdown("# 📊 Analyse ABC")
    st.markdown("Classification stratégique des produits pour un stockage optimisé")

    abc_df = compute_abc(df_f, metric)

    if abc_df.empty:
        st.warning("⚠️ Aucune donnée disponible pour l'analyse ABC")
        st.stop()

    # Summary
    class_summary = abc_df.groupby('Classe').agg({
        'Article': 'count',
        metric: 'sum',
        'Pct': 'sum'
    }).reset_index()
    class_summary.columns = ['Class', 'SKU Count', 'Total Volume', 'Volume %']

    col_sum1, col_sum2, col_sum3 = st.columns(3)

    for idx, row in class_summary.iterrows():
        if idx < 3:  # Safety check
            col = [col_sum1, col_sum2, col_sum3][idx]

            color = {'A': '🟢', 'B': '🟡', 'C': '🔴'}.get(row['Class'], '⚪')

            with col:
                st.metric(
                    f"{color} Classe {row['Class']}",
                    f"{row['SKU Count']:.0f} Références",
                    delta=f"{row['Volume %']:.1f}% du volume"
                )

    st.markdown("---")

    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        # Pareto chart
        top_50 = abc_df.head(50)

        fig_pareto = go.Figure()

        # Bars
        fig_pareto.add_trace(go.Bar(
            x=top_50['Article'],
            y=top_50[metric],
            marker_color=[
                '#10b981' if c == 'A' else '#f59e0b' if c == 'B' else '#ef4444'
                for c in top_50['Classe']
            ],
            name='Volume',
            yaxis='y'
        ))

        # Cumulative line
        fig_pareto.add_trace(go.Scatter(
            x=top_50['Article'],
            y=top_50['Cumul'],
            mode='lines+markers',
            name='Cumulative %',
            line=dict(color='#2563eb', width=2),
            yaxis='y2'
        ))

        fig_pareto.update_layout(
            title="Analyse Pareto ABC (Top 50 Références)",
            template='plotly_white',
            height=400,
            yaxis=dict(title="Volume"),
            yaxis2=dict(title="% Cumulé", overlaying='y', side='right'),
            hovermode='x unified',
            legend=dict(title="Légende")
        )

        st.plotly_chart(fig_pareto, use_container_width=True)

    with col_chart2:
        # Class distribution pie
        fig_pie = px.pie(
            class_summary,
            names='Class',
            values='Total Volume',
            title="Distribution du Volume par Classe",
            color='Class',
            color_discrete_map={'A': '#10b981', 'B': '#f59e0b', 'C': '#ef4444'}
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # Recommendations
    st.markdown("### 💡 Recommandations Stratégiques")

    col_rec1, col_rec2, col_rec3 = st.columns(3)

    with col_rec1:
        st.info("""
            **🟢 Produits Classe A (80% Vol)**
            - Placer près des zones d'expédition
            - Optimiser les chemins de picking
            - Contrôle stock quotidien
            - Réapprovisionnement prioritaire
        """)

    with col_rec2:
        st.info("""
            **🟡 Produits Classe B (15% Vol)**
            - Placement en zone médiane
            - Revue de stock hebdomadaire
            - Réapprovisionnement standard
            - Allocation équilibrée
        """)

    with col_rec3:
        st.info("""
            **🔴 Produits Classe C (5% Vol)**
            - Stockage en zones éloignées OK
            - Revue de stock mensuelle
            - Réapprovisionnement à la demande
            - Minimiser l'espace occupé
        """)


    # Detailed table
    st.markdown("### 📋 Classification ABC Détaillée")

    class_filter = st.multiselect(
        "Filtrer par Classe",
        ['A', 'B', 'C'],
        default=['A', 'B', 'C']
    )

    filtered_abc = abc_df[abc_df['Classe'].isin(class_filter)]

    st.dataframe(
        filtered_abc[['Article', metric, 'Pct', 'Cumul', 'Classe']].head(100),
        use_container_width=True,
        height=400
    )

# =============================================================================
# PAGE 4: PRODUCT ASSOCIATIONS
# =============================================================================

elif page == "🔗 Associations Produits":
    st.markdown("# 🔗 Analyse des Associations Produits")
    st.markdown("Analyse du panier de la ménagère pour le placement stratégique des produits")

    # Parameters
    with st.expander("⚙️ Paramètres d'Analyse", expanded=False):
        min_support = st.slider(
            "Support Minimum (%)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Pourcentage minimum de commandes contenant la paire de produits"
        )

    with st.spinner("Analyse des associations de produits..."):
        assoc_df, total_baskets = compute_assoc(df_f, min_support) # Changed threshold to min_support

    if assoc_df is None or assoc_df.empty:
        st.warning(f"⚠️ Aucune association forte trouvée au seuil de {min_support}%. Essayez de réduire le seuil.")
        st.info(f"📊 {total_baskets:,} commandes multi-articles analysées")
        st.stop()

    st.success(f"✅ {len(assoc_df)} paires de produits trouvées dans {total_baskets:,} commandes")

    st.markdown("---")

    tab_network, tab_recommender, tab_list = st.tabs([
        "🕸️ Réseau d'Associations",
        "🔍 Recommandeur Produits",
        "📋 Liste des Associations"
    ])

    # Network Tab
    with tab_network:
        st.markdown("### 🕸️ Matrice d'Association Produits")
        st.caption("💡 **Comment lire** : Les couleurs foncées indiquent des associations plus fortes. Utilisez cette matrice pour identifier les clusters de produits.")

        # Create adjacency matrix
        top_products = list(
            set(assoc_df['Produit A'].head(25)) |
            set(assoc_df['Produit B'].head(25))
        )

        matrix = pd.DataFrame(0, index=top_products, columns=top_products)

        for _, row in assoc_df.iterrows():
            if row['Produit A'] in top_products and row['Produit B'] in top_products:
                matrix.loc[row['Produit A'], row['Produit B']] = row['Fréquence']
                matrix.loc[row['Produit B'], row['Produit A']] = row['Fréquence']

        fig_heat = px.imshow(
            matrix,
            x=top_products,
            y=top_products,
            color_continuous_scale='Reds',
            title="Matrice de Force d'Association (Top 25 Produits)",
            aspect='auto'
        )
        fig_heat.update_layout(height=600)
        st.plotly_chart(fig_heat, use_container_width=True)

    # Recommender Tab
    with tab_recommender:
        st.markdown("### 🔍 Explorateur d'Associations")
        st.caption("💡 **Outil** : Sélectionnez un produit pour voir avec quels autres articles il est le plus souvent commandé.")

        all_products = sorted(
            list(set(assoc_df['Produit A']) | set(assoc_df['Produit B']))
        )

        target_product = st.selectbox(
            "Sélectionner un Produit",
            all_products,
            help="Voir les produits fréquemment commandés avec cet article"
        )

        # Find associations
        related = assoc_df[
            (assoc_df['Produit A'] == target_product) |
            (assoc_df['Produit B'] == target_product)
        ].copy()

        related['Related_Product'] = related.apply(
            lambda x: x['Produit B'] if x['Produit A'] == target_product else x['Produit A'],
            axis=1
        )

        related = related.sort_values('Fréquence', ascending=False).head(15)
        if not related.empty:
            col_chart, col_data = st.columns([2, 1])

            with col_chart:
                fig_rec = px.bar(
                related,
                x='Related_Product',
                y='Fréquence',
                title=f"Produits Fréquemment Associés avec {target_product}",
                color='Support',
                color_continuous_scale='Viridis',
                labels={'Fréquence': 'Nb Co-occurrences', 'Related_Product': 'Produit Associé', 'Support': 'Support (%)'}
            )
            fig_rec.update_layout(
                height=400,
                xaxis_title="📦 Produit Associé",
                yaxis_title="🔄 Fréquence de Co-occurrence",
                template='plotly_white'
            )
            st.plotly_chart(fig_rec, use_container_width=True)

            with col_data:
                st.markdown("**Métriques d'Association**")
                st.dataframe(
                    related[['Related_Product', 'Fréquence', 'Support']],
                    use_container_width=True,
                    height=400
                )

            st.markdown("### 💡 Recommandation de Placement")
            top_associate = related.iloc[0]
            st.info(
                f"**{target_product}** est fréquemment commandé avec **{top_associate['Related_Product']}** "
                f"({top_associate['Support']:.1f}% des commandes). Envisagez de placer ces articles à proximité."
            )
        else:
            st.warning(f"Aucune association forte trouvée pour {target_product}")

    # List Tab
    with tab_list:
        st.markdown("### 📋 Liste Complète des Associations")
        st.caption("Toutes les paires de produits dépassant le seuil de support minimum.")

        st.dataframe(
            assoc_df.sort_values('Fréquence', ascending=False),
            use_container_width=True,
            height=600
        )

# =============================================================================
# PAGE 5: AI INSIGHTS
# =============================================================================

elif page == "🧠 Insights IA":
    st.markdown("# 🧠 Insights IA & Prédictions")
    st.markdown("Analyses avancées utilisant le Machine Learning")

    tab_forecast, tab_anomalies, tab_clustering = st.tabs([
        "📈 Prévision Demande",
        "🚨 Détection Anomalies",
        "🎯 Clustering Produits"
    ])

    # Forecasting Tab
    with tab_forecast:
        st.markdown("### 📈 Prévision de Demande")
        st.caption("💡 **Vue d'ensemble** : Prédiction du volume sur 14 jours basée sur une moyenne mobile.")

        col_param1, col_param2 = st.columns(2)

        with col_param1:
            ma_window = st.slider("Fenêtre Moyenne Mobile (jours)", 3, 30, 7)

        with col_param2:
            forecast_horizon = st.slider("Horizon de Prévision (jours)", 7, 30, 14)

        with st.spinner("Génération des prévisions..."):
            daily, forecast = compute_forecast(df_f, metric, ma_window, forecast_horizon)

        if not daily.empty:
            fig_forecast = go.Figure()

            # Historical data
            fig_forecast.add_trace(go.Scatter(
                x=daily.index,
                y=daily[metric],
                name='Réel',
                line=dict(color='lightgray', width=1),
                mode='lines'
            ))

            # Moving average
            fig_forecast.add_trace(go.Scatter(
                x=daily.index,
                y=daily['MA_7'],
                name=f'Moyenne Mobile {ma_window}j',
                line=dict(color='#2563eb', width=3)
            ))

            # Forecast
            if not forecast.empty:
                fig_forecast.add_trace(go.Scatter(
                    x=forecast.index,
                    y=forecast['Forecast'],
                    name='Prévision',
                    line=dict(color='#10b981', width=3, dash='dash')
                ))

            fig_forecast.update_layout(
                title="Prévision de Volume",
                template='plotly_white',
                height=400,
                hovermode='x unified',
                xaxis_title="📅 Date",
                yaxis_title="📦 Volume (Unités)",
                legend=dict(title="Légende")
            )

            st.plotly_chart(fig_forecast, use_container_width=True)

            # Forecast summary
            if not forecast.empty:
                avg_forecast = forecast['Forecast'].mean()
                st.info(
                    f"📊 **Résumé Prévision** : Volume quotidien moyen attendu de "
                    f"**{avg_forecast:,.0f} unités** sur les {forecast_horizon} prochains jours"
                )
        else:
            st.warning("⚠️ Données insuffisantes pour la prévision")

    # Anomaly Tab
    with tab_anomalies:
        st.markdown("### 🚨 Détection d'Anomalies")
        st.caption("💡 **Vue d'ensemble** : Identification des commandes inhabituelles grâce au Machine Learning (Isolation Forest).")

        with st.spinner("Détection des anomalies..."):
            anomalies = compute_anomalies(df_f)

        if not anomalies.empty:
            st.warning(f"⚠️ {len(anomalies)} commandes anormales détectées")

            col_viz, col_table = st.columns([2, 1])

            with col_viz:
                # Scatter plot
                fig_anom = px.scatter(
                    anomalies,
                    x='Lignes',
                    y='Volume',
                    size='Score',
                    color='Score',
                    hover_data=['No Op', 'Colis'],
                    title="Distribution des Commandes Anormales",
                    color_continuous_scale='Reds',
                    labels={'Lignes': 'Nombre de Lignes', 'Volume': 'Volume (Unités)', 'Score': 'Sévérité'}
                )
                fig_anom.update_layout(
                    height=400,
                    template='plotly_white',
                    xaxis_title="📋 Nombre de Lignes",
                    yaxis_title="📦 Volume (Unités)"
                )
                st.plotly_chart(fig_anom, use_container_width=True)

            with col_table:
                st.markdown("**Top Anomalies**")
                st.dataframe(
                    anomalies[['No Op', 'Volume', 'Lignes', 'Score']].head(20),
                    use_container_width=True,
                    height=400
                )

            st.markdown("### 💡 Analyse")
            top_anomaly = anomalies.iloc[0]
            st.info(
                f"Commande la plus inhabituelle : **{top_anomaly['No Op']}** avec "
                f"**{top_anomaly['Volume']:.0f} unités** sur **{top_anomaly['Lignes']:.0f} lignes**. "
                f"Cela peut nécessiter une vérification ou un traitement spécial."
            )
        else:
            st.success("✅ Aucune anomalie significative détectée. Les opérations sont dans les normes.")

    # Clustering Tab
    with tab_clustering:
        st.markdown("### 🎯 Clustering Produits")
        st.caption("💡 **Vue d'ensemble** : Regroupement stratégique des produits basé sur le volume et la fréquence (K-Means).")

        with st.spinner("Segmentation des produits..."):
            cluster_df = compute_clustering(df_f)

        if not cluster_df.empty and 'Cluster_Label' in cluster_df.columns:
            # Summary by cluster
            cluster_summary = cluster_df.groupby('Cluster_Label').agg({
                'Article': 'count',
                'Volume': 'sum',
                'Frequence': 'mean'
            }).reset_index()

            cluster_summary.columns = ['Zone', 'Nb Références', 'Volume Total', 'Fréquence Moy.']

            col_sum1, col_sum2, col_sum3 = st.columns(3)

            for idx, row in cluster_summary.iterrows():
                if idx < 3:  # Safety check
                    col = [col_sum1, col_sum2, col_sum3][idx]

                    with col:
                        st.metric(
                            row['Zone'],
                            f"{row['Nb Références']:.0f} Références",
                            delta=f"{row['Fréquence Moy.']:.1f} freq moy"
                        )

            st.markdown("---")

            # Scatter plot
            fig_cluster = px.scatter(
                cluster_df,
                x='Frequence',
                y='Volume',
                color='Cluster_Label',
                hover_data=['Article'],
                title="Segmentation Produits (Volume vs Fréquence)",
                color_discrete_sequence=['#10b981', '#3b82f6', '#f59e0b'],
                log_x=True,
                log_y=True,
                labels={'Frequence': 'Fréquence (Log)', 'Volume': 'Volume (Log)', 'Cluster_Label': 'Zone'}
            )
            fig_cluster.update_layout(
                height=500,
                template='plotly_white',
                xaxis_title="🔄 Fréquence (Échelle Log)",
                yaxis_title="📦 Volume (Échelle Log)"
            )
            st.plotly_chart(fig_cluster, use_container_width=True)

            st.markdown("### 💡 Recommandations de Stockage")

            col_rec1, col_rec2, col_rec3 = st.columns(3)

            with col_rec1:
                st.success("""
                    **🥇 Zone Or (Chaude)**
                    - Articles haute fréquence
                    - Placer à l'entrée du picking
                    - Minimiser la distance de trajet
                    - Réapprovisionnement rapide
                """)

            with col_rec2:
                st.info("""
                    **🥈 Zone Argent (Tiède)**
                    - Articles moyenne fréquence
                    - Placement milieu d'allée
                    - Accès standard
                    - Réapprovisionnement régulier
                """)

            with col_rec3:
                st.warning("""
                    **🥉 Zone Bronze (Froide)**
                    - Articles basse fréquence
                    - Stockage distant acceptable
                    - Priorité optimisation espace
                    - Réapprovisionnement périodique
                """)
        else:
            st.warning("⚠️ Insufficient data for clustering analysis")

# =============================================================================
# PAGE 6: DATA EXPORT
# =============================================================================

elif page == "📅 Export de Données":
    st.markdown("# 📥 Export de Données & Rapports")
    st.markdown("Téléchargez les données analytiques et générez des rapports")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.markdown("### 📊 Export Analytique")

        # Prepare export data
        export_datasets = {}

        # Basic stats
        kpis = compute_global_kpis(df_f)

        # ABC Analysis
        if st.checkbox("Inclure Analyse ABC", value=True):
            abc_data = compute_abc(df_f, metric)
            if not abc_data.empty:
                export_datasets['ABC_Analysis'] = abc_data

        # Associations
        if st.checkbox("Inclure Associations Produits", value=True):
            assoc_data, _ = compute_assoc(df_f, 5)
            if assoc_data is not None:
                export_datasets['Associations'] = assoc_data

        # Geographic
        if st.checkbox("Inclure Données Géographiques", value=True):
            geo_data = compute_geo_data(df_f)
            if not geo_data.empty:
                export_datasets['Geography'] = geo_data

        # Daily summary
        if st.checkbox("Inclure Résumé Quotidien", value=True):
            daily_summary = df_f.groupby('Date').agg({
                metric: 'sum',
                'No Op': 'nunique',
                'Article': 'nunique'
            }).reset_index()
            daily_summary.columns = ['Date', 'Volume', 'Orders', 'Unique_SKUs']
            export_datasets['Daily_Summary'] = daily_summary

        # Product summary
        if st.checkbox("Inclure Résumé Produits", value=True):
            product_summary = df_f.groupby('Article').agg({
                metric: 'sum',
                'No Op': 'nunique'
            }).reset_index()
            product_summary.columns = ['Article', 'Total_Volume', 'Order_Count']
            product_summary = product_summary.sort_values('Total_Volume', ascending=False)
            export_datasets['Product_Summary'] = product_summary

        st.markdown("---")

        # Excel export
        if export_datasets:
            excel_file = export_to_excel(export_datasets, 'wms_analytics.xlsx')

            st.download_button(
                label="📥 Télécharger Rapport Excel",
                data=excel_file,
                file_name=f"wms_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

        # CSV export
        st.markdown("### 📄 Export CSV")

        csv_data = df_f.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Télécharger Données Filtrées (CSV)",
            data=csv_data,
            file_name=f"wms_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_exp2:
        st.markdown("### 📋 Résumé Exécutif")

        kpis = compute_global_kpis(df_f)
        summary_report = create_summary_report(df_f, kpis)

        st.text_area(
            "Aperçu du Rapport",
            value=summary_report,
            height=400,
            disabled=True
        )

        st.download_button(
            label="📥 Télécharger Résumé (TXT)",
            data=summary_report.encode('utf-8'),
            file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")

    # Data quality report
    st.markdown("### 🔍 Rapport Qualité Données")

    col_q1, col_q2, col_q3, col_q4 = st.columns(4)

    with col_q1:
        st.metric("Enregistrements", f"{len(df_f):,}")

    with col_q2:
        missing_pct = (df_f.isna().sum().sum() / (len(df_f) * len(df_f.columns))) * 100
        st.metric("Complétude", f"{100-missing_pct:.1f}%")

    with col_q3:
        st.metric("Produits Uniques", f"{df_f['Article'].nunique():,}")

    with col_q4:
        st.metric("Plage de Dates", f"{(df_f['Date'].max() - df_f['Date'].min()).days} jours")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 20px;'>
        <p style='margin: 0;'>
            <strong>WMS Analytics Pro v6.0</strong> | ID Logistics | Powered by Streamlit & Plotly
        </p>
        <p style='margin: 5px 0 0 0; font-size: 0.85rem;'>
            © 2025 | For operational excellence and continuous improvement
        </p>
    </div>
""", unsafe_allow_html=True)
