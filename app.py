import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd

st.set_page_config(layout="wide")

st.title("⚓ Simulador de Puerto Inteligente (Juego Multiequipo)")

# ===========================
# PARÁMETROS
# ===========================
lambda_input = st.slider("λ (tasa de llegada)", 0.1, 2.0, 0.7)
dias = st.slider("Días de simulación", 20, 100, 40)

niveles = ["Básico", "Medio", "Superior"]

mu_dict = {"Básico": 0.45, "Medio": 0.725, "Superior": 0.80}
cf = {"Básico": 840, "Medio": 1350, "Superior": 1500}
cop = {"Básico": 840, "Medio": 1350, "Superior": 1600}

# ===========================
# FUNCIÓN SIMULACIÓN
# ===========================
def simular(nivel, s, anim=False):

    mu = mu_dict[nivel]
    cola = []
    costo_total = 0
    historial = []
    llegadas_total = 0

    for dia in range(dias):

        llegadas = np.random.poisson(lambda_input)
        llegadas_total += llegadas

        for _ in range(llegadas):
            cola.append(0)

        atendidos = min(len(cola), s)

        for i in range(atendidos):
            cola[i] += np.random.exponential(1/mu)

        for i in range(len(cola)):
            cola[i] += 1

        costo_espera = sum(cola) * 2000
        uso = atendidos / s if s > 0 else 0
        costo_op = s * uso * cop[nivel]
        costo_f = s * cf[nivel]

        costo_total += costo_f + costo_op + costo_espera

        historial.append(len(cola))
        cola = cola[atendidos:]

        if anim:
            barcos = "🚢" * len(cola)

            info_anim.markdown(f"""
            ### Día {dia+1}
            🚢 Llegadas: {llegadas}  
            ⚙️ Atendidos: {atendidos}  
            🧱 Cola: {len(cola)}  
            {barcos}
            """)

            fig, ax = plt.subplots()
            ax.plot(historial, color="red")
            ax.set_title("Cola en el tiempo")

            grafico_anim.pyplot(fig)
            time.sleep(0.2)

    lambda_real = llegadas_total / dias
    rho = lambda_real / (s * mu)
    costo_prom = costo_total / dias

    return costo_prom, rho, lambda_real, historial


# ======================================================
# 🎮 SIMULACIÓN INDIVIDUAL
# ======================================================
st.header("🎮 Simulación individual")

colA, colB = st.columns([2,1])

grafico_anim = colA.empty()
info_anim = colA.empty()

nivel_ind = st.selectbox("Nivel", niveles)
s_ind = st.slider("Muelles", 1, 6)

if st.button("🚀 Simulación animada"):
    costo, rho, lam_real, hist = simular(nivel_ind, s_ind, anim=True)

    st.success(f"💰 Costo promedio: ${int(costo)}")
    st.write(f"λ real simulado: {lam_real:.3f}")
    st.write(f"ρ: {rho:.2f}")

    if rho > 1:
        st.error("❌ Sistema colapsa (ρ > 1)")
    elif rho > 0.85:
        st.warning("⚠️ Sistema saturado")
    elif rho < 0.4:
        st.info("💸 Sobredimensionado")
    else:
        st.success("✅ Sistema eficiente")


# ======================================================
# 📊 COMPARACIÓN AUTOMÁTICA
# ======================================================
st.header("📊 Comparación automática")

resultados = []

for nivel in niveles:
    for s in [1,2,3,4,5,6]:

        costo, rho, lam_real, _ = simular(nivel, s)

        if rho > 1:
            estado = "❌ Inestable"
            costo_num = np.inf
            costo_disp = "∞"
        elif rho < 0.4:
            estado = "💸 Sobredimensionado"
            costo_num = costo
            costo_disp = int(costo)
        elif rho > 0.85:
            estado = "⚠️ Saturado"
            costo_num = costo
            costo_disp = int(costo)
        else:
            estado = "✅ Óptimo"
            costo_num = costo
            costo_disp = int(costo)

        resultados.append({
            "Nivel": nivel,
            "Muelles": s,
            "Costo": costo_disp,
            "ρ": round(rho,2),
            "Estado": estado,
            "Costo_num": costo_num
        })

df = pd.DataFrame(resultados).sort_values("Costo_num")
df = df.drop(columns="Costo_num")

st.dataframe(df, use_container_width=True)


# ======================================================
# 🏆 MEJOR OPCIÓN
# ======================================================
if st.button("🏆 Encontrar mejor opción"):

    df_valid = df[df["Costo"] != "∞"]

    if not df_valid.empty:
        mejor = df_valid.loc[df_valid["Costo"].astype(int).idxmin()]

        st.success(f"""
        🥇 Mejor opción:
        Nivel: {mejor['Nivel']}
        Muelles: {mejor['Muelles']}
        Costo: ${mejor['Costo']}
        """)
    else:
        st.error("❌ Todas las configuraciones colapsan")


# ======================================================
# 👥 COMPETENCIA
# ======================================================
st.header("👥 Competencia entre equipos")

num_equipos = st.selectbox("Número de equipos", list(range(2,9)))

equipos = []

for i in range(num_equipos):
    col1, col2, col3 = st.columns(3)

    nombre = col1.text_input(f"Equipo {i+1}", key=f"eq{i}")
    nivel = col2.selectbox(f"Nivel {i+1}", niveles, key=f"niv{i}")
    muelles = col3.slider(f"Muelles {i+1}", 1, 6, key=f"m{i}")

    equipos.append((nombre, nivel, muelles))


if st.button("🏁 Ejecutar competencia"):

    resultados_eq = []

    for nombre, nivel, s in equipos:
        costo, rho, lam_real, _ = simular(nivel, s)

        if rho > 1:
            estado = "💥 Colapso"
            costo_disp = "∞"
            costo_num = np.inf
        else:
            costo_disp = int(costo)
            costo_num = costo

            if rho < 0.4:
                estado = "💸 Sobredimensionado"
            elif rho > 0.85:
                estado = "⚠️ Saturado"
            else:
                estado = "✅ Óptimo"

        resultados_eq.append({
            "Equipo": nombre,
            "Nivel": nivel,
            "Muelles": s,
            "Costo": costo_disp,
            "ρ": round(rho,2),
            "Estado": estado,
            "Costo_num": costo_num
        })

    resultados_eq = sorted(resultados_eq, key=lambda x: x["Costo_num"])

    df_eq = pd.DataFrame(resultados_eq).drop(columns="Costo_num")

    st.subheader("🏆 Ranking")
    st.dataframe(df_eq, use_container_width=True)

    validos = [r for r in resultados_eq if r["Estado"] != "💥 Colapso"]

    if validos:
        ganador = validos[0]

        st.success(f"""
        🥇 Ganador: {ganador['Equipo']}
        Nivel: {ganador['Nivel']}
        Muelles: {ganador['Muelles']}
        Costo: ${ganador['Costo']}
        """)
    else:
        st.error("❌ Todos colapsaron")

    st.subheader("🧠 Retroalimentación")

    for r in resultados_eq:
        if r["Estado"] == "💥 Colapso":
            st.write(f"❌ {r['Equipo']}: sistema imposible (ρ > 1)")
        elif "Sobredimensionado" in r["Estado"]:
            st.write(f"💸 {r['Equipo']}: exceso de infraestructura")
        elif "Saturado" in r["Estado"]:
            st.write(f"⚠️ {r['Equipo']}: alta congestión")
        else:
            st.write(f"✅ {r['Equipo']}: buen diseño")


# ======================================================
# 📐 FÓRMULAS
# ======================================================
st.header("📐 Fórmulas")

st.markdown("""
- ρ = λ / (s·μ)  
- Costo fijo = s × Cf  
- Costo operación = s × ρ × Cop  
- Costo espera = Σ(tiempo en cola) × 2000  
- Costo total = fijo + operación + espera  

👉 Si ρ > 1 → el sistema colapsa  
👉 Óptimo ≈ 0.4 ≤ ρ ≤ 0.85
""")