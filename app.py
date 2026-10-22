import math
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import streamlit as st

G = 9.8

st.set_page_config(page_title="Laboratorio virtual de caída libre", page_icon="⚛️", layout="wide")

# Tema visual
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #07152e 0%, #0b2450 55%, #103b76 100%); color: #eef5ff; }
section[data-testid="stSidebar"] { background: #07152e; }
h1,h2,h3,p,label,div { color: #eef5ff; }
div.stButton > button { background: #19b9c8; color: #06213b; border: 0; border-radius: 10px; font-weight: 700; }
div.stButton > button:hover { background: #65e6ef; color: #06213b; }
[data-testid="stMetric"] { background: rgba(12,31,62,.8); border: 1px solid #284b7c; padding: 14px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

if "historial" not in st.session_state:
    st.session_state.historial = []
if "ultimo" not in st.session_state:
    st.session_state.ultimo = None

st.sidebar.title("⚛️ Navegación del laboratorio")
seccion = st.sidebar.radio(
    "Ir a:",
    ["Simulador de laboratorio gráfico", "Cálculo de resultados", "Historial de simulaciones", "Diagrama de flujo"]
)
st.sidebar.markdown("---")
st.sidebar.caption("Modelo ideal · g = 9.8 m/s² · Sin resistencia del aire")

def validar(h, m):
    if not np.isfinite(h) or h <= 0:
        raise ValueError("La altura debe ser un número mayor que cero.")
    if not np.isfinite(m) or m <= 0:
        raise ValueError("La masa debe ser un número mayor que cero.")

def fisica(h, m):
    validar(h, m)
    t = math.sqrt(2 * h / G)
    v = G * t
    ep = m * G * h
    ec = 0.5 * m * v * v
    return {"tiempo": t, "velocidad": v, "ep_inicial": ep, "ec_final": ec}

def registrar(h, m, r, origen):
    st.session_state.historial.append({
        "N.º": len(st.session_state.historial) + 1,
        "Origen": origen,
        "Altura (m)": round(h, 3),
        "Masa (kg)": round(m, 3),
        "Tiempo (s)": round(r["tiempo"], 3),
        "Velocidad impacto (m/s)": round(r["velocidad"], 3),
        "Energía potencial inicial (J)": round(r["ep_inicial"], 3),
        "Energía cinética final (J)": round(r["ec_final"], 3),
    })

def graficas(h, m, fraccion, en_animacion=True):
    """Devuelve una escena de caída y la curva de energía en el mismo fotograma."""
    t_final = math.sqrt(2*h/G)
    t = fraccion * t_final
    distancia = min(0.5 * G * t*t, h)
    y_actual = max(h - distancia, 0)
    v = G*t
    ep = m*G*y_actual
    ec = min(0.5*m*v*v, m*G*h)
    em = m*G*h

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.1), gridspec_kw={"width_ratios":[0.85,1.5]})
    fig.patch.set_facecolor("#0b2040")
    for ax in (ax1, ax2):
        ax.set_facecolor("#10294e")
        ax.tick_params(colors="#d9e8ff", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#7596c6")
        ax.grid(True, color="#57749d", alpha=.25)

    # Panel único de pelota
    ax1.set_title("PELOTA EN CAÍDA LIBRE", color="white", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlim(-0.7, 0.7)
    ax1.set_ylim(-h*0.04, h*1.12)
    ax1.set_xticks([])
    ax1.set_ylabel("Altura (m)", color="#d9e8ff")
    ax1.axhline(0, color="#5eead4", linewidth=3)
    ax1.text(0, -h*0.025, "SUPERFICIE", color="#5eead4", ha="center", va="top", fontsize=8, fontweight="bold")
    ax1.plot([0,0], [0,h], color="#4cc9d0", alpha=.22, linewidth=1, linestyle=":")
    radius = max(h*0.025, 0.8)
    ball = Circle((0, y_actual), radius, facecolor="#ffe16b", edgecolor="#fff7c2", linewidth=2, zorder=5)
    ax1.add_patch(ball)
    ax1.scatter([0], [y_actual], s=25, color="#fff7c2", zorder=6)
    ax1.text(0.12, y_actual, f"{y_actual:.1f} m", color="#ffe16b", fontsize=9, va="center")
    ax1.text(0.03, h*1.055, f"t = {t:.2f} s", color="white", fontsize=9)

    # Gráfica de energía dibujada hasta el tiempo actual
    ax2.set_title("ENERGÍA VS. TIEMPO", color="white", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlabel("Tiempo (s)", color="#d9e8ff")
    ax2.set_ylabel("Energía (J)", color="#d9e8ff")
    ax2.set_xlim(0, t_final*1.04 if t_final > 0 else 1)
    ax2.set_ylim(0, em*1.12 if em > 0 else 1)
    ts = np.linspace(0, max(t, 0.0001), max(2, int(160*max(fraccion, .01))))
    dist = 0.5*G*ts**2
    eps = np.maximum(m*G*(h-dist), 0)
    ecs = np.minimum(0.5*m*(G*ts)**2, em)
    ax2.plot(ts, eps, color="#38bdf8", linewidth=3, label="Energía potencial")
    ax2.plot(ts, ecs, color="#fb923c", linewidth=3, label="Energía cinética")
    ax2.plot([0, t_final], [em, em], color="#22c55e", linewidth=2, linestyle="--", label="Energía mecánica total")
    ax2.scatter([t], [ep], color="#38bdf8", s=45, zorder=4)
    ax2.scatter([t], [ec], color="#fb923c", s=45, zorder=4)
    ax2.legend(loc="upper right", facecolor="#17365f", edgecolor="#5275a3", labelcolor="white", fontsize=8)
    ax2.text(.03, .05, f"Ep: {ep:,.1f} J   Ec: {ec:,.1f} J", transform=ax2.transAxes,
             color="white", fontsize=9, bbox=dict(facecolor="#07152e", alpha=.7, edgecolor="#385b89"))
    fig.tight_layout(pad=2)
    return fig, t, v, ep, ec, y_actual

st.title("Laboratorio virtual de Física")
st.markdown("### Simulador web de caída libre y energía mecánica")
st.caption("Simulación sincronizada en tiempo real · g = 9.8 m/s² · Modelo ideal")

if seccion == "Simulador de laboratorio gráfico":
    st.markdown("Ajusta los parámetros y ejecuta una sola animación: la pelota y la gráfica de energía avanzan sincronizadas.")
    with st.form("parametros_sim"):
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            altura = st.number_input("Altura inicial (m)", min_value=0.1, max_value=10000.0, value=100.0, step=10.0)
        with c2:
            masa = st.number_input("Masa del objeto (kg)", min_value=0.1, max_value=10000.0, value=5.0, step=1.0)
        with c3:
            velocidad_anim = st.select_slider("Velocidad de animación", options=["Lenta", "Normal", "Rápida"], value="Normal")
        iniciar = st.form_submit_button("▶ Iniciar simulación sincronizada")
    if iniciar:
        try:
            res = fisica(float(altura), float(masa))
            st.session_state.ultimo = {"altura": float(altura), "masa": float(masa), **res}
            # placeholders únicos: nunca se crea una segunda gráfica de pelota
            panel_graficas = st.empty()
            panel_estado = st.empty()
            panel_metricas = st.empty()
            pasos = {"Lenta": 30, "Normal": 20, "Rápida": 12}[velocidad_anim]
            pausa = {"Lenta": 0.012, "Normal": 0.004, "Rápida": 0.0}[velocidad_anim]
            for i in range(pasos + 1):
                f = i / pasos
                fig, t, v, ep, ec, y = graficas(float(altura), float(masa), f)
                panel_graficas.pyplot(fig, use_container_width=True)
                plt.close(fig)
                panel_estado.info(
                    f"{'🟢 Simulación en curso' if f < 1 else '✅ Impacto detectado'} · "
                    f"Progreso: {f*100:.0f}% · Altura: {y:.2f} m"
                )
                with panel_metricas.container():
                    a,b,c,d = st.columns(4)
                    a.metric("Tiempo", f"{t:.2f} s")
                    b.metric("Velocidad", f"{v:.2f} m/s")
                    c.metric("Energía potencial", f"{ep:,.2f} J")
                    d.metric("Energía cinética", f"{ec:,.2f} J")
                time.sleep(pausa)
            registrar(float(altura), float(masa), res, "Simulación animada")
        except ValueError as e:
            st.error(str(e))
    else:
        h0, m0 = 100.0, 5.0
        fig, *_ = graficas(h0, m0, 0.0)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.info("Ingresa los valores y pulsa «Iniciar simulación sincronizada». Ambos gráficos se moverán juntos.")
        st.caption("La vista inicial muestra una sola pelota y una sola gráfica de energía. La animación se ejecuta al iniciar.")

elif seccion == "Cálculo de resultados":
    st.subheader("Cálculo de resultados")
    with st.form("calculo"):
        c1, c2 = st.columns(2)
        h = c1.number_input("Altura inicial (m)", min_value=0.1, value=100.0, step=10.0, key="calc_h")
        m = c2.number_input("Masa del objeto (kg)", min_value=0.1, value=5.0, step=1.0, key="calc_m")
        ok = st.form_submit_button("Calcular resultados")
    if ok:
        try:
            r = fisica(float(h), float(m))
            registrar(float(h), float(m), r, "Cálculo")
            st.session_state.ultimo = {"altura": float(h), "masa": float(m), **r}
            a,b,c,d = st.columns(4)
            a.metric("Tiempo de caída", f"{r['tiempo']:.3f} s")
            b.metric("Velocidad de impacto", f"{r['velocidad']:.3f} m/s")
            c.metric("Energía potencial inicial", f"{r['ep_inicial']:,.3f} J")
            d.metric("Energía cinética final", f"{r['ec_final']:,.3f} J")
            st.success("Cálculo completado. Para ver los gráficos en movimiento, entra al simulador gráfico y pulsa Iniciar.")
        except ValueError as e:
            st.error(str(e))

elif seccion == "Historial de simulaciones":
    st.subheader("Historial de simulaciones")
    if st.session_state.historial:
        df = pd.DataFrame(st.session_state.historial)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇ Descargar historial CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name="historial_caida_libre.csv", mime="text/csv")
        if st.button("Limpiar historial"):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("Todavía no hay registros. Ejecuta una simulación o realiza un cálculo.")

else:
    st.subheader("Diagrama de flujo")
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;gap:8px">
      <div style="background:#173b55;border:2px solid #38bdf8;border-radius:28px;padding:12px 35px;font-weight:bold">INICIO</div>
      <div style="color:#38bdf8;font-size:24px">↓</div>
      <div style="background:#172f52;border:1px solid #4f719d;border-radius:10px;padding:12px 25px">Ingresar altura y masa</div>
      <div style="color:#38bdf8;font-size:24px">↓</div>
      <div style="background:#3a2c24;border:1px solid #fbbf24;border-radius:10px;padding:12px 25px">Validar valores positivos</div>
      <div style="color:#38bdf8;font-size:24px">↓</div>
      <div style="background:#172f52;border:1px solid #4f719d;border-radius:10px;padding:12px 25px">Calcular tiempo, velocidad y energías</div>
      <div style="color:#38bdf8;font-size:24px">↓</div>
      <div style="background:#172f52;border:1px solid #4f719d;border-radius:10px;padding:12px 25px">Animar pelota y gráfica sincronizadas</div>
      <div style="color:#38bdf8;font-size:24px">↓</div>
      <div style="background:#172f52;border:1px solid #4f719d;border-radius:10px;padding:12px 25px">Mostrar resultados y guardar historial</div>
      <div style="color:#38bdf8;font-size:24px">↓</div>
      <div style="background:#4a2330;border:2px solid #fb7185;border-radius:28px;padding:12px 35px;font-weight:bold">FIN / NUEVA SIMULACIÓN</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Modelo: objeto soltado desde el reposo, sin resistencia del aire. Energía mecánica ideal conservada.")
