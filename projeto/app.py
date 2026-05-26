import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Powerlifting Dashboard",
    page_icon="🏋️",
    layout="wide"
)

# ── Carregar dados ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("powerlifting_dashboard.xlsx", sheet_name="Powerlifting Data")
    return df

df = load_data()

# ── Título ──────────────────────────────────────────────────────────────────
st.title("🏋️ Powerlifting Dashboard")
st.markdown("Análise de resultados de competição de powerlifting")
st.divider()

# ── Sidebar — filtros ───────────────────────────────────────────────────────
st.sidebar.header("Filtros")

weight_classes = ["Todas"] + sorted(df["Weight Class Range"].dropna().unique().tolist())
selected_class = st.sidebar.selectbox("Classe de Peso", weight_classes)

if selected_class != "Todas":
    df_filtered = df[df["Weight Class Range"] == selected_class]
else:
    df_filtered = df.copy()

# ── KPIs ────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Atletas", len(df_filtered))
with col2:
    st.metric("Melhor Total (kg)", f"{df_filtered['Total'].max():.1f}")
with col3:
    st.metric("Média de Idade", f"{df_filtered['Age'].mean():.1f}")
with col4:
    st.metric("Melhor Thrust/Weight", f"{df_filtered['Thrust-to-Weight Ratio'].max():.2f}")

st.divider()

# ── Linha 1: Tabela de classificação + gráfico de barras ───────────────────
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("🏆 Classificação")
    table_cols = ["Place", "Name", "Weight Class Range", "Bodyweight", "Total", "Thrust-to-Weight Ratio"]
    st.dataframe(
        df_filtered[table_cols].sort_values("Place"),
        use_container_width=True,
        hide_index=True
    )

with col_right:
    st.subheader("📊 Total por Atleta")
    fig_bar = px.bar(
        df_filtered.sort_values("Total", ascending=True),
        x="Total",
        y="Name",
        orientation="h",
        color="Total",
        color_continuous_scale="Oranges",
        labels={"Total": "Total (kg)", "Name": "Atleta"}
    )
    fig_bar.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Linha 2: Comparação squat/bench/deadlift + scatter ─────────────────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("💪 Melhor Tentativa por Movimento")

    # Usar a 3ª tentativa como resultado final (pode estar na col Squat3Kg, etc.)
    df_melhor = df_filtered[["Name", "Squat3Kg", "Bench3Kg", "Deadlift3Kg"]].copy()
    df_melhor.columns = ["Atleta", "Squat", "Bench", "Deadlift"]
    df_melt = df_melhor.melt(id_vars="Atleta", var_name="Movimento", value_name="Kg")

    fig_group = px.bar(
        df_melt,
        x="Atleta",
        y="Kg",
        color="Movimento",
        barmode="group",
        color_discrete_map={"Squat": "#e07b39", "Bench": "#5b8dd9", "Deadlift": "#4caf7d"},
        labels={"Kg": "Peso (kg)"}
    )
    fig_group.update_layout(height=400, xaxis_tickangle=-30)
    st.plotly_chart(fig_group, use_container_width=True)

with col_r2:
    st.subheader("⚖️ Peso Corporal vs Total")

    fig_scatter = px.scatter(
        df_filtered,
        x="Bodyweight",
        y="Total",
        text="Name",
        size="Thrust-to-Weight Ratio",
        color="Weight Class Range",
        labels={"Bodyweight": "Peso Corporal (kg)", "Total": "Total (kg)"},
        size_max=30
    )
    fig_scatter.update_traces(textposition="top center", textfont_size=9)
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ── Linha 3: Radar de comparação de atletas ─────────────────────────────────
st.subheader("🕸️ Radar — Comparar Atletas")

athletes = df_filtered["Name"].tolist()
selected_athletes = st.multiselect("Escolhe até 4 atletas", athletes, default=athletes[:2])

if selected_athletes:
    df_radar = df_filtered[df_filtered["Name"].isin(selected_athletes)]
    categories = ["Squat3Kg", "Bench3Kg", "Deadlift3Kg", "Total", "Thrust-to-Weight Ratio"]
    labels = ["Squat", "Bench", "Deadlift", "Total", "Thrust/Weight"]

    fig_radar = go.Figure()
    for _, row in df_radar.iterrows():
        values = [row[c] for c in categories]
        # Normalizar para 0-100 para melhor visualização
        max_vals = [df_filtered[c].max() for c in categories]
        values_norm = [v/m*100 if m > 0 else 0 for v, m in zip(values, max_vals)]
        fig_radar.add_trace(go.Scatterpolar(
            r=values_norm + [values_norm[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=row["Name"]
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=450
    )
    st.plotly_chart(fig_radar, use_container_width=True)