import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Página ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Powerlifting Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #0e1117; color: #e0e0e0; }
  [data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
  }
  .sidebar-section {
    font-size: 0.7rem; font-weight: 700; color: #e85d04;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1.2rem 0 0.4rem 0;
  }
  h1.dash-title { color: #f0f6fc; font-size: 2rem; margin-bottom: 0.2rem; }
  .dash-sub { color: #8b949e; font-size: 0.9rem; margin-bottom: 1.2rem; }

  .stTabs [data-baseweb="tab-list"] {
    background-color: #161b22; border-radius: 10px; padding: 4px; gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent; color: #8b949e;
    border-radius: 8px; padding: 0.4rem 1.1rem;
    font-size: 0.85rem; font-weight: 600;
  }
  .stTabs [aria-selected="true"] {
    background-color: #e85d04 !important; color: white !important;
  }

  .kpi-bar { display: flex; gap: 0.8rem; margin: 1rem 0 1.5rem 0; }
  .kpi-v {
    flex: 1; background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 0.9rem 1rem;
    transition: border-color 0.2s;
  }
  .kpi-v:hover { border-color: #e85d04; }
  .kpi-v-label { font-size: 0.65rem; color: #8b949e; text-transform: uppercase;
                 letter-spacing: 0.08em; margin-bottom: 0.3rem; }
  .kpi-v-value { font-size: 1.4rem; font-weight: 700; color: #f0f6fc; }
  .kpi-v-sub   { font-size: 0.7rem; color: #e85d04; margin-top: 0.15rem; }

  .section-title {
    font-size: 0.9rem; font-weight: 700; color: #f0f6fc;
    border-left: 3px solid #e85d04;
    padding-left: 0.6rem; margin: 1.4rem 0 0.7rem 0;
  }
  .info-box {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.8rem 1rem;
    font-size: 0.8rem; color: #8b949e; margin-bottom: 0.8rem;
  }
  .info-box strong { color: #f0f6fc; }

  .summary-box {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 1.2rem 1.5rem; margin-top: 0.8rem;
  }
  .summary-box h4 { color: #f0f6fc; margin: 0 0 0.8rem 0; font-size: 1rem; }
  .diff-row {
    display: flex; justify-content: space-between;
    padding: 0.35rem 0; border-bottom: 1px solid #21262d;
  }
  .diff-row:last-child { border-bottom: none; }
  .diff-label { color: #8b949e; font-size: 0.85rem; }
  .diff-pos { color: #3fb950; font-weight: 700; }
  .diff-neg { color: #f85149; font-weight: 700; }
  .diff-neu { color: #e3b341; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Dados ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_excel(
        "Powerlifting_Dashboard.xlsx",
        sheet_name="Base_Dados_Limpa"
    )
    # Potência mecânica (F=m*g, W=F*d, P=W/t) — deslocamentos estimados
    D_SQ, D_BP, D_DL = 0.5, 0.4, 0.7
    df["Potencia_Squat"]    = (df["Squat Máx (kg)"]    * 9.81 * D_SQ) / df["Tempo Squat (s)"]
    df["Potencia_Bench"]    = (df["Bench Máx (kg)"]    * 9.81 * D_BP) / df["Tempo Bench (s)"]
    df["Potencia_Deadlift"] = (df["Deadlift Máx (kg)"] * 9.81 * D_DL) / df["Tempo Deadlift (s)"]
    df["Potencia_Total"]    = df[["Potencia_Squat","Potencia_Bench","Potencia_Deadlift"]].sum(axis=1)
    df["Tempo_Total"]       = (df["Tempo Squat (s)"].fillna(0) +
                               df["Tempo Bench (s)"].fillna(0) +
                               df["Tempo Deadlift (s)"].fillna(0))
    df["Assimetria"] = (
        (df["Tempo Squat (s)"] - df["Tempo Deadlift (s)"]).abs() /
        ((df["Tempo Squat (s)"] + df["Tempo Deadlift (s)"]) / 2) * 100
    ).round(1)
    return df

df_all = load()
CLASSES = sorted(df_all["Categoria"].dropna().unique().tolist())

PLOT = dict(
    paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
    font=dict(color="#c9d1d9", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## Filtros")
    st.markdown("---")

    st.markdown("<div class='sidebar-section'>Classe de Peso</div>", unsafe_allow_html=True)
    sel_classes = st.multiselect(
        "classes", CLASSES, default=CLASSES, label_visibility="collapsed"
    )

    st.markdown("<div class='sidebar-section'>Idade</div>", unsafe_allow_html=True)
    age_min = int(df_all["Idade"].min())
    age_max = int(df_all["Idade"].max())
    sel_age = st.slider("Idade", age_min, age_max, (age_min, age_max), label_visibility="collapsed")

    st.markdown("<div class='sidebar-section'>Total de Peso (kg)</div>", unsafe_allow_html=True)
    total_min = float(df_all["Total (kg)"].min())
    total_max = float(df_all["Total (kg)"].max())
    sel_total = st.slider("Total", total_min, total_max, (total_min, total_max), label_visibility="collapsed")

# ── Filtros aplicados ─────────────────────────────────────────────────────────
df = df_all.copy()
if sel_classes:
    df = df[df["Categoria"].isin(sel_classes)]
df = df[(df["Idade"] >= sel_age[0]) & (df["Idade"] <= sel_age[1])]
df = df[(df["Total (kg)"] >= sel_total[0]) & (df["Total (kg)"] <= sel_total[1])]

# ════════════════════════════════════════════════════════════════
# CABEÇALHO
# ════════════════════════════════════════════════════════════════
st.markdown("<h1 class='dash-title'> Powerlifting Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='dash-sub'>Análise competitiva de powerlifting</p>", unsafe_allow_html=True)

search = st.text_input("Pesquisar atleta por nome", placeholder="Escreve o nome...")
df_view = df[df["Atleta"].str.contains(search, case=False, na=False)] if search else df

st.dataframe(
    df_view[["Atleta","Categoria","Squat Máx (kg)","Bench Máx (kg)","Deadlift Máx (kg)","Total (kg)"]]
    .sort_values("Total (kg)", ascending=False).reset_index(drop=True),
    use_container_width=True, hide_index=True, height=260,
    column_config={
        "Atleta":             st.column_config.TextColumn("Atleta"),
        "Categoria":          st.column_config.TextColumn("Classe"),
        "Squat Máx (kg)":     st.column_config.NumberColumn("Melhor Squat",    format="%d kg"),
        "Bench Máx (kg)":     st.column_config.NumberColumn("Melhor Bench",    format="%d kg"),
        "Deadlift Máx (kg)":  st.column_config.NumberColumn("Melhor Deadlift", format="%d kg"),
        "Total (kg)":         st.column_config.ProgressColumn(
                                  "Total", min_value=0,
                                  max_value=int(df_all["Total (kg)"].max()+50), format="%d kg"),
    }
)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Médias por Classe de Peso",
    "🏆 Ranking de Atletas",
    "🧍 Análise de Desempenho Pessoal",
    "⚡ Velocidade da Barra",
])

# ── TAB 1 — Médias por Classe ─────────────────────────────────────────────────
with tab1:
    avg = (
        df.groupby("Categoria")[["Squat Máx (kg)","Bench Máx (kg)","Deadlift Máx (kg)","Total (kg)"]]
        .mean().round(1).reset_index()
    )
    avg_melt = avg.melt(
        id_vars="Categoria",
        value_vars=["Squat Máx (kg)","Bench Máx (kg)","Deadlift Máx (kg)","Total (kg)"],
        var_name="Lift", value_name="kg"
    )
    avg_melt["Lift"] = avg_melt["Lift"].str.replace(" Máx (kg)","").str.replace(" (kg)","")

    fig_avg = px.bar(
        avg_melt,
        x="Categoria", y="kg", color="Lift", barmode="group",
        color_discrete_map={"Squat":"#e85d04","Bench":"#58a6ff","Deadlift":"#3fb950","Total":"#d2a8ff"},
        title="Média de Squat, Bench, Deadlift e Total por Classe de Peso",
        labels={"Categoria":"Classe de Peso","kg":"kg"},
        text_auto=".0f"
    )
    fig_avg.update_traces(textposition="outside", textfont_size=11)
    fig_avg.update_layout(**PLOT, height=420, title_font_size=13)
    st.plotly_chart(fig_avg, use_container_width=True)

    st.markdown("**Tabela de Médias por Classe**")
    avg_show = avg.copy()
    avg_show.columns = ["Classe","Média Squat","Média Bench","Média Deadlift","Média Total"]
    st.dataframe(avg_show, use_container_width=True, hide_index=True)

# ── TAB 2 — Ranking ───────────────────────────────────────────────────────────
with tab2:
    c1, c2 = st.columns([1, 1])
    with c1:
        n_top = st.number_input(
            "Número de atletas a mostrar", min_value=1,
            max_value=len(df), value=min(5, len(df)), step=1
        )
    with c2:
        rank_lift = st.radio(
            "Ordenar por",
            ["Squat Máx (kg)","Bench Máx (kg)","Deadlift Máx (kg)","Total (kg)"],
            format_func=lambda x: x.replace(" Máx (kg)","").replace(" (kg)",""),
            horizontal=True
        )

    df_top = (
        df[["Atleta","Categoria","Idade","Peso Corporal (kg)",
            "Squat Máx (kg)","Bench Máx (kg)","Deadlift Máx (kg)","Total (kg)"]]
        .sort_values(rank_lift, ascending=False)
        .head(int(n_top))
        .reset_index(drop=True)
    )
    df_top.index += 1

    label_lift = rank_lift.replace(" Máx (kg)","").replace(" (kg)","")
    fig_top = px.bar(
        df_top.sort_values(rank_lift),
        x=rank_lift, y="Atleta", orientation="h",
        color=rank_lift,
        color_continuous_scale=[[0,"#1c2130"],[0.5,"#e85d04"],[1,"#ff9a3c"]],
        title=f"Top {int(n_top)} — {label_lift}",
        labels={rank_lift:"kg","Atleta":""},
        text=df_top.sort_values(rank_lift)[rank_lift].apply(lambda x: f"{x:.0f} kg")
    )
    fig_top.update_traces(textposition="outside")
    fig_top.update_layout(**PLOT, height=max(300, int(n_top)*50),
                          title_font_size=13, coloraxis_showscale=False)
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown(f"**Top {int(n_top)} atletas — ordenado por {label_lift}**")
    st.dataframe(
        df_top, use_container_width=True,
        column_config={
            "Squat Máx (kg)":    st.column_config.NumberColumn("Squat",    format="%d kg"),
            "Bench Máx (kg)":    st.column_config.NumberColumn("Bench",    format="%d kg"),
            "Deadlift Máx (kg)": st.column_config.NumberColumn("Deadlift", format="%d kg"),
            "Total (kg)":        st.column_config.ProgressColumn(
                                     "Total", min_value=0,
                                     max_value=int(df_all["Total (kg)"].max()+50), format="%d kg"),
            "Peso Corporal (kg)":st.column_config.NumberColumn("Peso Corp.", format="%.1f kg"),
        }
    )

# ── TAB 3 — Desempenho Pessoal ────────────────────────────────────────────────
with tab3:
    st.markdown("#### Insere os teus dados")

    p1, p2, p3, p4 = st.columns(4)
    u_bw = p1.number_input("Peso Corporal (kg)", 40.0, 250.0, 80.0, 0.5, key="u_bw")
    u_sq = p2.number_input("Melhor Squat (kg)",    0.0, 700.0, 100.0, 2.5, key="u_sq")
    u_bp = p3.number_input("Melhor Bench (kg)",    0.0, 500.0,  80.0, 2.5, key="u_bp")
    u_dl = p4.number_input("Melhor Deadlift (kg)", 0.0, 700.0, 120.0, 2.5, key="u_dl")
    u_total = u_sq + u_bp + u_dl

    def closest_class(bw, classes):
        numeric = []
        for c in classes:
            try:
                numeric.append((float(c.replace("+","").replace("kg","")), c))
            except:
                pass
        numeric.sort()
        for val, label in numeric:
            if bw <= val:
                return label
        return numeric[-1][1] if numeric else classes[0]

    user_class = closest_class(u_bw, CLASSES)
    df_class   = df[df["Categoria"] == user_class]

    st.markdown(f"**Classe de peso detectada:** `{user_class}` — {len(df_class)} atletas nesta classe")
    st.markdown("---")

    if len(df_class) == 0:
        st.warning("Sem atletas nesta classe com os filtros actuais.")
    else:
        worst   = df_class.loc[df_class["Total (kg)"].idxmin()]
        avg_cls = df_class[["Squat Máx (kg)","Bench Máx (kg)","Deadlift Máx (kg)","Total (kg)"]].mean()

        labels = ["Squat","Bench","Deadlift","Total"]
        u_vals = [u_sq, u_bp, u_dl, u_total]
        w_vals = [worst["Squat Máx (kg)"], worst["Bench Máx (kg)"],
                  worst["Deadlift Máx (kg)"], worst["Total (kg)"]]

        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            name="Tu", x=labels, y=u_vals,
            marker_color="#e85d04",
            text=[f"{v:.0f}" for v in u_vals], textposition="outside"
        ))
        fig_cmp.add_trace(go.Bar(
            name=f"Pior — {worst['Atleta']}", x=labels, y=w_vals,
            marker_color="#30363d",
            text=[f"{v:.0f}" for v in w_vals], textposition="outside"
        ))
        fig_cmp.update_layout(
            **PLOT, barmode="group", height=380,
            title=f"Tu vs Pior Atleta da Classe {user_class}",
            yaxis_title="kg", title_font_size=13
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

        def diff_html(val):
            if val > 0:   return "diff-pos", f"+{val:.1f} kg acima"
            elif val < 0: return "diff-neg", f"{val:.1f} kg abaixo"
            else:         return "diff-neu", "igual"

        def build_rows(diffs):
            rows = ""
            for lift, val in diffs.items():
                cls, txt = diff_html(val)
                rows += (f"<div class='diff-row'><span class='diff-label'>{lift}</span>"
                         f"<span class='{cls}'>{txt}</span></div>")
            return rows

        diffs_worst = {
            "Squat":    u_sq  - worst["Squat Máx (kg)"],
            "Bench":    u_bp  - worst["Bench Máx (kg)"],
            "Deadlift": u_dl  - worst["Deadlift Máx (kg)"],
            "Total":    u_total - worst["Total (kg)"],
        }
        diffs_avg = {
            "Squat":    u_sq  - avg_cls["Squat Máx (kg)"],
            "Bench":    u_bp  - avg_cls["Bench Máx (kg)"],
            "Deadlift": u_dl  - avg_cls["Deadlift Máx (kg)"],
            "Total":    u_total - avg_cls["Total (kg)"],
        }

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(f"""
            <div class='summary-box'>
              <h4>📊 Tu vs Pior Atleta ({worst['Atleta']})</h4>
              {build_rows(diffs_worst)}
            </div>""", unsafe_allow_html=True)
        with col_r2:
            st.markdown(f"""
            <div class='summary-box'>
              <h4>📈 Tu vs Média da Classe {user_class}</h4>
              {build_rows(diffs_avg)}
              <div style='margin-top:0.8rem;font-size:0.75rem;color:#8b949e'>
                Médias: Squat {avg_cls['Squat Máx (kg)']:.0f} kg •
                Bench {avg_cls['Bench Máx (kg)']:.0f} kg •
                Deadlift {avg_cls['Deadlift Máx (kg)']:.0f} kg •
                Total {avg_cls['Total (kg)']:.0f} kg
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"**Todos os atletas da classe {user_class}**")
        st.dataframe(
            df_class[["Atleta","Peso Corporal (kg)","Squat Máx (kg)","Bench Máx (kg)",
                       "Deadlift Máx (kg)","Total (kg)"]]
            .sort_values("Total (kg)", ascending=False).reset_index(drop=True),
            use_container_width=True, hide_index=True,
            column_config={
                "Squat Máx (kg)":    st.column_config.NumberColumn("Squat",    format="%d kg"),
                "Bench Máx (kg)":    st.column_config.NumberColumn("Bench",    format="%d kg"),
                "Deadlift Máx (kg)": st.column_config.NumberColumn("Deadlift", format="%d kg"),
                "Total (kg)":        st.column_config.ProgressColumn(
                                         "Total", min_value=0,
                                         max_value=int(df_all["Total (kg)"].max()+50), format="%d kg"),
                "Peso Corporal (kg)":st.column_config.NumberColumn("Peso Corp.", format="%.1f kg"),
            }
        )

# ── TAB 4 — Velocidade da Barra ───────────────────────────────────────────────
with tab4:
    df_vel = df_all.dropna(subset=["Tempo Squat (s)","Tempo Bench (s)","Tempo Deadlift (s)"]).copy()

    if len(df_vel) == 0:
        st.warning("Sem dados de velocidade da barra disponíveis.")
    else:
        # Aplicar filtros da sidebar aos dados de velocidade
        df_vel = df_vel[df_vel["Categoria"].isin(sel_classes)] if sel_classes else df_vel

        idx_max_p = df_vel["Potencia_Total"].idxmax()
        idx_min_t = df_vel["Tempo_Total"].idxmin()
        idx_max_vs = df_vel["Vel Média Squat (m/s)"].idxmax()

        st.markdown(f"""
        <div class="kpi-bar">
          <div class="kpi-v">
            <div class="kpi-v-label">Maior Potência Total</div>
            <div class="kpi-v-value">{df_vel.loc[idx_max_p,'Potencia_Total']:.0f} W</div>
            <div class="kpi-v-sub">{df_vel.loc[idx_max_p,'Atleta']}</div>
          </div>
          <div class="kpi-v">
            <div class="kpi-v-label">Atleta Mais Explosivo</div>
            <div class="kpi-v-value">{df_vel.loc[idx_min_t,'Tempo_Total']:.2f} s</div>
            <div class="kpi-v-sub">{df_vel.loc[idx_min_t,'Atleta']} — menor tempo total</div>
          </div>
          <div class="kpi-v">
            <div class="kpi-v-label">Vel. Máx. Squat</div>
            <div class="kpi-v-value">{df_vel['Vel Média Squat (m/s)'].max():.3f} m/s</div>
            <div class="kpi-v-sub">{df_vel.loc[idx_max_vs,'Atleta']}</div>
          </div>
          <div class="kpi-v">
            <div class="kpi-v-label">Atletas com Dados</div>
            <div class="kpi-v-value">{len(df_vel)}</div>
            <div class="kpi-v-sub">de {len(df_all)} totais</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='info-box'>
          <strong>Nota metodológica:</strong>
          Potência calculada como <em>P = (m × g × d) / t</em>,
          com deslocamentos estimados: Squat 0,50 m · Bench 0,40 m · Deadlift 0,70 m.
          Velocidade média real disponível em m/s. Menor tempo = levantamento mais explosivo.
        </div>
        """, unsafe_allow_html=True)

        # ── 1. Correlação Carga vs Tempo ──────────────────────────
        st.markdown("<div class='section-title'>1. Correlação Carga vs Tempo</div>", unsafe_allow_html=True)
        st.markdown("Relação entre tempo total de execução e carga total levantada. "
                    "Atletas no canto inferior direito são mais fortes mas mais lentos (*grinders*); "
                    "no canto inferior esquerdo são explosivos e fortes.")

        fig_sc = px.scatter(
            df_vel,
            x="Tempo_Total", y="Total (kg)",
            text="Atleta", size="Peso Corporal (kg)", size_max=22,
            color="Categoria",
            color_discrete_sequence=["#e85d04","#58a6ff"],
            title="Tempo Total de Execução (s) vs Carga Total Levantada (kg)",
            labels={"Tempo_Total":"Tempo Total (s)","Total (kg)":"Total (kg)",
                    "Categoria":"Classe"}
        )
        fig_sc.update_traces(textposition="top center", textfont_size=10)
        t_med = df_vel["Tempo_Total"].median()
        c_med = df_vel["Total (kg)"].median()
        fig_sc.add_vline(x=t_med, line_dash="dash", line_color="#484f58",
                         annotation_text="Mediana tempo",
                         annotation_font_color="#8b949e", annotation_position="top right")
        fig_sc.add_hline(y=c_med, line_dash="dash", line_color="#484f58",
                         annotation_text="Mediana carga",
                         annotation_font_color="#8b949e", annotation_position="bottom right")
        fig_sc.update_layout(**PLOT, height=420, title_font_size=13)
        st.plotly_chart(fig_sc, use_container_width=True)

        # ── 2. Velocidade Média Real por Exercício ────────────────
        st.markdown("<div class='section-title'>2. Velocidade Média da Barra por Exercício (m/s)</div>",
                    unsafe_allow_html=True)
        st.markdown("Velocidade média real registada durante o levantamento. "
                    "Valores mais altos indicam maior explosividade no movimento.")

        vel_cols = ["Vel Média Squat (m/s)","Vel Média Bench (m/s)","Vel Média Deadlift (m/s)"]
        df_vel_plot = df_all.dropna(subset=vel_cols).copy()
        if sel_classes:
            df_vel_plot = df_vel_plot[df_vel_plot["Categoria"].isin(sel_classes)]
        vel_melt = df_vel_plot[["Atleta","Categoria"] + vel_cols].melt(
            id_vars=["Atleta","Categoria"], var_name="Exercício", value_name="m/s"
        )
        vel_melt["Exercício"] = (vel_melt["Exercício"]
                                 .str.replace("Vel Média ","")
                                 .str.replace(" (m/s)",""))
        vel_melt = vel_melt.sort_values(["Categoria","Atleta"])

        fig_vel = px.bar(
            vel_melt, x="Atleta", y="m/s", color="Exercício", barmode="group",
            color_discrete_map={"Squat":"#e85d04","Bench":"#58a6ff","Deadlift":"#3fb950"},
            title=f"Velocidade Média da Barra por Exercício e Atleta (m/s) — {len(df_vel_plot)} atletas com dados",
            labels={"m/s":"Velocidade (m/s)","Atleta":""},
            text_auto=".3f",
            facet_col="Categoria",
            facet_col_spacing=0.08
        )
        fig_vel.update_traces(textposition="outside", textfont_size=10)
        fig_vel.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1]}</b>",
                                                        font=dict(size=13, color="#f0f6fc")))
        fig_vel.update_layout(**PLOT, height=420, title_font_size=13, xaxis_tickangle=-20)
        fig_vel.update_xaxes(matches=None)
        st.plotly_chart(fig_vel, use_container_width=True)

        # ── 3. Potência Mecânica (Watts) ──────────────────────────
        st.markdown("<div class='section-title'>3. Potência Mecânica por Atleta (Watts)</div>",
                    unsafe_allow_html=True)
        st.markdown("Potência gerada em cada exercício. Destaque para quem produz mais potência, "
                    "não apenas quem levanta mais carga.")

        pot_melt = df_vel[["Atleta","Potencia_Squat","Potencia_Bench","Potencia_Deadlift"]].melt(
            id_vars="Atleta", var_name="Exercício", value_name="Watts"
        )
        pot_melt["Exercício"] = (pot_melt["Exercício"]
                                 .str.replace("Potencia_","")
                                 .str.replace("Bench","Bench Press"))

        fig_pot = px.bar(
            pot_melt, x="Atleta", y="Watts", color="Exercício", barmode="group",
            color_discrete_map={"Squat":"#e85d04","Bench Press":"#58a6ff","Deadlift":"#3fb950"},
            title="Potência Mecânica por Exercício e Atleta (W)",
            labels={"Watts":"Potência (W)","Atleta":""},
            text_auto=".0f"
        )
        fig_pot.update_traces(textposition="outside", textfont_size=9)
        fig_pot.update_layout(**PLOT, height=400, title_font_size=13)
        st.plotly_chart(fig_pot, use_container_width=True)

        best_pot = df_vel.loc[df_vel["Potencia_Total"].idxmax()]
        st.markdown(f"""
        <div class='info-box'>
          🏆 <strong>Maior potência total:</strong> {best_pot['Atleta']} com
          <strong>{best_pot['Potencia_Total']:.0f} W</strong>
          (Squat {best_pot['Potencia_Squat']:.0f} W ·
           Bench {best_pot['Potencia_Bench']:.0f} W ·
           Deadlift {best_pot['Potencia_Deadlift']:.0f} W)
        </div>
        """, unsafe_allow_html=True)

        # ── 4. Assimetria Temporal Squat vs Deadlift ──────────────
        st.markdown("<div class='section-title'>4. Assimetria Temporal — Squat vs Deadlift</div>",
                    unsafe_allow_html=True)
        st.markdown("Comparação do tempo de execução entre Squat e Deadlift. "
                    "Diferenças grandes indicam padrões neuromusculares distintos entre os movimentos.")

        col_l, col_r = st.columns(2)

        with col_l:
            fig_asym = go.Figure()
            fig_asym.add_trace(go.Bar(
                name="Squat", x=df_vel["Atleta"].tolist(),
                y=df_vel["Tempo Squat (s)"].tolist(),
                marker_color="#e85d04",
                text=[f"{v:.2f}s" for v in df_vel["Tempo Squat (s)"]],
                textposition="outside"
            ))
            fig_asym.add_trace(go.Bar(
                name="Deadlift", x=df_vel["Atleta"].tolist(),
                y=df_vel["Tempo Deadlift (s)"].tolist(),
                marker_color="#3fb950",
                text=[f"{v:.2f}s" for v in df_vel["Tempo Deadlift (s)"]],
                textposition="outside"
            ))
            fig_asym.update_layout(
                **PLOT, barmode="group", height=380,
                title="Tempo de Execução: Squat vs Deadlift (s)",
                yaxis_title="Tempo (s)", title_font_size=13,
                xaxis_tickangle=-25
            )
            st.plotly_chart(fig_asym, use_container_width=True)

        with col_r:
            fig_asi2 = px.bar(
                df_vel.sort_values("Assimetria", ascending=False),
                x="Atleta", y="Assimetria",
                color="Assimetria",
                color_continuous_scale=[[0,"#1c2130"],[0.5,"#e3b341"],[1,"#f85149"]],
                title="Índice de Assimetria Temporal Squat/Deadlift (%)",
                labels={"Assimetria":"Assimetria (%)","Atleta":""},
                text_auto=".1f"
            )
            fig_asi2.update_traces(textposition="outside")
            fig_asi2.update_layout(**PLOT, height=380, title_font_size=13,
                                   coloraxis_showscale=False,
                                   yaxis_title="Assimetria (%)",
                                   xaxis_tickangle=-25)
            st.plotly_chart(fig_asi2, use_container_width=True)

        # ── Tabela resumo ─────────────────────────────────────────
        st.markdown("**Tabela Resumo — Velocidade e Potência**")
        tbl = df_vel[[
            "Atleta","Categoria","Peso Corporal (kg)",
            "Tempo Squat (s)","Tempo Bench (s)","Tempo Deadlift (s)",
            "Vel Média Squat (m/s)","Vel Média Bench (m/s)","Vel Média Deadlift (m/s)",
            "Potencia_Squat","Potencia_Bench","Potencia_Deadlift","Potencia_Total",
            "Rácio Força/Peso","Assimetria"
        ]].reset_index(drop=True)

        st.dataframe(tbl, use_container_width=True, hide_index=True,
            column_config={
                "Atleta":                    st.column_config.TextColumn("Atleta"),
                "Categoria":                 st.column_config.TextColumn("Classe"),
                "Peso Corporal (kg)":        st.column_config.NumberColumn("Peso Corp.", format="%.1f kg"),
                "Tempo Squat (s)":           st.column_config.NumberColumn("T. Squat",    format="%.2f s"),
                "Tempo Bench (s)":           st.column_config.NumberColumn("T. Bench",    format="%.2f s"),
                "Tempo Deadlift (s)":        st.column_config.NumberColumn("T. Deadlift", format="%.2f s"),
                "Vel Média Squat (m/s)":     st.column_config.NumberColumn("V. Squat",    format="%.3f m/s"),
                "Vel Média Bench (m/s)":     st.column_config.NumberColumn("V. Bench",    format="%.3f m/s"),
                "Vel Média Deadlift (m/s)":  st.column_config.NumberColumn("V. Deadlift", format="%.3f m/s"),
                "Potencia_Squat":            st.column_config.NumberColumn("P. Squat",    format="%d W"),
                "Potencia_Bench":            st.column_config.NumberColumn("P. Bench",    format="%d W"),
                "Potencia_Deadlift":         st.column_config.NumberColumn("P. Deadlift", format="%d W"),
                "Potencia_Total":            st.column_config.ProgressColumn(
                                                 "Potência Total", min_value=0,
                                                 max_value=int(df_vel["Potencia_Total"].max()+200),
                                                 format="%d W"),
                "Rácio Força/Peso":          st.column_config.NumberColumn("Força/Peso", format="%.2f×"),
                "Assimetria":                st.column_config.NumberColumn("Assimetria", format="%.1f%%"),
            }
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#484f58;font-size:0.75rem'>"
    "Powerlifting Dashboard</p>",
    unsafe_allow_html=True
)