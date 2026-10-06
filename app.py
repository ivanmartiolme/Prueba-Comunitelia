import streamlit as st
import pandas as pd
import plotly.express as px
import calculos

st.set_page_config(
    page_title="Cuadro de mando de dirección",
    page_icon="📊",
    layout="wide",
)

FECHA_REFERENCIA = getattr(calculos, "FECHA_REFERENCIA", pd.Timestamp("2026-09-30"))

mrr_mensual = getattr(calculos, "mrr_mensual", pd.DataFrame())
altas_bajas_contratos = getattr(calculos, "altas_bajas_contratos", pd.DataFrame())
mrr_por_cliente = getattr(calculos, "mrr_por_cliente", pd.DataFrame())
contratos_proximos_vencer = getattr(calculos, "contratos_proximos_vencer", pd.DataFrame())
clientes_un_servicio = getattr(calculos, "clientes_un_servicio", pd.DataFrame())
clientes_sin_actividad = getattr(calculos, "clientes_sin_actividad", pd.DataFrame())

clientes_margen = pd.DataFrame()
for nombre in ["clientes_margen", "margen_clientes", "margen_tecnico", "clientes_margen_tecnico"]:
    valor = getattr(calculos, nombre, None)
    if isinstance(valor, pd.DataFrame):
        clientes_margen = valor.copy()
        break


def euros(valor):
    if pd.isna(valor):
        return "—"
    return f"{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def porcentaje(valor):
    if pd.isna(valor):
        return "—"
    return f"{valor:.2f}%".replace(".", ",")


def col_existente(df, opciones):
    for c in opciones:
        if c in df.columns:
            return c
    return None


def resumen_demo():
    partes = []

    if not mrr_mensual.empty and "mrr" in mrr_mensual.columns:
        inicio = float(mrr_mensual.iloc[0]["mrr"])
        actual = float(mrr_mensual.iloc[-1]["mrr"])
        evolucion = (actual / inicio - 1) * 100 if inicio else 0
        partes.append(
            f"El MRR conocido actual es de {euros(actual)}, con una evolución "
            f"del {porcentaje(evolucion)} respecto al inicio del periodo analizado."
        )

    if not altas_bajas_contratos.empty:
        altas = int(altas_bajas_contratos["altas"].sum())
        bajas = int(altas_bajas_contratos["bajas"].sum())
        partes.append(
            f"En los últimos 12 meses se registran {altas} altas y {bajas} bajas "
            f"de contratos, con un saldo neto de {altas - bajas}."
        )

    if not mrr_por_cliente.empty and "porcentaje_mrr" in mrr_por_cliente.columns:
        top5 = mrr_por_cliente.head(5)["porcentaje_mrr"].sum()
        top10 = mrr_por_cliente.head(10)["porcentaje_mrr"].sum()
        partes.append(
            f"Los cinco mayores clientes representan el {porcentaje(top5)} del "
            f"MRR conocido y los diez mayores el {porcentaje(top10)}."
        )

    if not contratos_proximos_vencer.empty:
        c = col_existente(contratos_proximos_vencer, ["mrr", "cuota_mensual", "importe_mensual"])
        riesgo = pd.to_numeric(contratos_proximos_vencer[c], errors="coerce").sum() if c else 0
        partes.append(
            f"Hay {len(contratos_proximos_vencer)} contratos cuya permanencia "
            f"vence en los próximos 90 días, con al menos {euros(riesgo)} de MRR conocido."
        )

    partes.append(
        f"Se identifican {len(clientes_un_servicio)} clientes con un único servicio "
        f"activo y {len(clientes_sin_actividad)} clientes sin actividad técnica "
        f"reciente o registrada."
    )

    return " ".join(partes)


def prompt_llm():
    actual = float(mrr_mensual.iloc[-1]["mrr"]) if not mrr_mensual.empty else None
    inicio = float(mrr_mensual.iloc[0]["mrr"]) if not mrr_mensual.empty else None
    evolucion = (actual / inicio - 1) * 100 if inicio else None
    altas = int(altas_bajas_contratos["altas"].sum()) if not altas_bajas_contratos.empty else 0
    bajas = int(altas_bajas_contratos["bajas"].sum()) if not altas_bajas_contratos.empty else 0
    top5 = float(mrr_por_cliente.head(5)["porcentaje_mrr"].sum()) if "porcentaje_mrr" in mrr_por_cliente else None
    top10 = float(mrr_por_cliente.head(10)["porcentaje_mrr"].sum()) if "porcentaje_mrr" in mrr_por_cliente else None

    return f"""
Eres un analista de dirección de una empresa de servicios tecnológicos recurrentes.

Analiza los siguientes indicadores con fecha de referencia 30/09/2026 y redacta
un resumen ejecutivo para Dirección General.

DATOS:
- MRR actual conocido: {actual}
- MRR al inicio del periodo de 12 meses: {inicio}
- Evolución del MRR: {evolucion}%
- Altas de contratos: {altas}
- Bajas de contratos: {bajas}
- Saldo neto de contratos: {altas - bajas}
- Concentración Top 5: {top5}%
- Concentración Top 10: {top10}%
- Contratos con permanencia próxima a vencer: {len(contratos_proximos_vencer)}
- Clientes con un único servicio: {len(clientes_un_servicio)}
- Clientes sin actividad reciente o registrada: {len(clientes_sin_actividad)}

INSTRUCCIONES:
1. Resume la situación general en 5-7 frases.
2. Destaca primero los aspectos relevantes para Dirección.
3. Explica si existe crecimiento, estabilidad o contracción.
4. Señala riesgos comerciales concretos.
5. Señala oportunidades comerciales concretas.
6. No inventes datos.
7. Si un indicador está incompleto por calidad de datos, indícalo.
8. Usa un tono ejecutivo, claro y directo.
"""


st.markdown("# 📊 Cuadro de mando de dirección")
st.caption(
    f"Servicios tecnológicos recurrentes · Fecha de referencia: "
    f"{FECHA_REFERENCIA.strftime('%d/%m/%Y')}"
)

with st.sidebar:
    st.header("Contexto")
    st.write(f"**Fecha:** {FECHA_REFERENCIA.strftime('%d/%m/%Y')}")
    st.divider()
    st.write("📈 Evolución del negocio")
    st.write("💰 Ingresos y concentración")
    st.write("⚙️ Rentabilidad técnica")
    st.write("🎯 Riesgo comercial")
    st.write("🛒 Oportunidades")
    st.write("🤖 Resumen ejecutivo")

mrr_actual = float(mrr_mensual.iloc[-1]["mrr"]) if not mrr_mensual.empty else 0
mrr_inicio = float(mrr_mensual.iloc[0]["mrr"]) if not mrr_mensual.empty else 0
evolucion_mrr = (mrr_actual / mrr_inicio - 1) * 100 if mrr_inicio else 0

altas = int(altas_bajas_contratos["altas"].sum()) if not altas_bajas_contratos.empty else 0
bajas = int(altas_bajas_contratos["bajas"].sum()) if not altas_bajas_contratos.empty else 0
saldo = altas - bajas

top5 = float(mrr_por_cliente.head(5)["porcentaje_mrr"].sum()) if "porcentaje_mrr" in mrr_por_cliente else 0
top10 = float(mrr_por_cliente.head(10)["porcentaje_mrr"].sum()) if "porcentaje_mrr" in mrr_por_cliente else 0

riesgo = 0
if not contratos_proximos_vencer.empty:
    c_riesgo = col_existente(contratos_proximos_vencer, ["mrr", "cuota_mensual", "importe_mensual"])
    if c_riesgo:
        riesgo = pd.to_numeric(contratos_proximos_vencer[c_riesgo], errors="coerce").sum()

st.subheader("Situación actual")
k1, k2, k3, k4 = st.columns(4)
k1.metric("MRR actual conocido", euros(mrr_actual), f"{porcentaje(evolucion_mrr)} vs inicio 12M")
k2.metric("Saldo de contratos", saldo, f"{altas} altas / {bajas} bajas")
k3.metric("Concentración Top 5", porcentaje(top5), f"Top 10: {porcentaje(top10)}")
k4.metric("MRR conocido en riesgo", euros(riesgo), f"{len(contratos_proximos_vencer)} permanencias")

if evolucion_mrr < 0 and saldo < 0:
    st.warning(
        f"Se observa una señal de contracción: el MRR conocido cae un "
        f"{porcentaje(evolucion_mrr)} y el saldo contractual es {saldo}."
    )
elif evolucion_mrr > 0 and saldo > 0:
    st.success(
        f"Se observa una señal de crecimiento: el MRR conocido aumenta un "
        f"{porcentaje(evolucion_mrr)} y el saldo contractual es +{saldo}."
    )
else:
    st.info("La evolución de MRR y contratos presenta señales mixtas.")

st.subheader("📈 Evolución del negocio")
c1, c2 = st.columns(2)

with c1:
    st.markdown("**MRR últimos 12 meses**")
    if not mrr_mensual.empty:
        datos = mrr_mensual.copy()
        datos["mes"] = pd.to_datetime(datos["mes"])
        fig = px.line(datos, x="mes", y="mrr", markers=True,
                      labels={"mes": "Mes", "mrr": "MRR (€)"})
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de MRR.")

with c2:
    st.markdown("**Altas y bajas de contratos**")
    if not altas_bajas_contratos.empty:
        datos = altas_bajas_contratos.copy()
        datos["mes"] = pd.to_datetime(datos["mes"])
        fig = px.bar(
            datos, x="mes", y=["altas", "bajas"], barmode="group",
            labels={"mes": "Mes", "value": "Contratos", "variable": "Tipo"}
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Saldo acumulado del periodo: {saldo} contratos.")
    else:
        st.info("No hay datos de altas y bajas.")

st.subheader("💰 Ingresos y concentración")
c1, c2 = st.columns([1.2, 1])

with c1:
    st.markdown("**Top 10 clientes por MRR**")
    if not mrr_por_cliente.empty:
        datos = mrr_por_cliente.head(10).copy()

        if "nombre" not in datos.columns and hasattr(calculos, "clientes"):
            datos = datos.merge(
                calculos.clientes[["id_cliente", "nombre"]],
                on="id_cliente", how="left"
            )

        nombre = col_existente(datos, ["nombre", "nombre_cliente"])
        datos["cliente"] = datos[nombre].astype(str).str.strip() if nombre else datos["id_cliente"].astype(str)

        fig = px.bar(
            datos.sort_values("mrr"),
            x="mrr", y="cliente", orientation="h",
            labels={"mrr": "MRR (€)", "cliente": "Cliente"},
            text="mrr"
        )
        fig.update_traces(texttemplate="%{text:,.0f} €", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("**Concentración**")
    st.metric("Top 5 clientes", porcentaje(top5))
    st.metric("Top 10 clientes", porcentaje(top10))
    if not mrr_por_cliente.empty and "porcentaje_mrr" in mrr_por_cliente:
        st.info(
            f"El mayor cliente representa aproximadamente "
            f"{porcentaje(mrr_por_cliente.iloc[0]['porcentaje_mrr'])} "
            f"del MRR conocido."
        )
    st.caption("Concentración calculada sobre el MRR conocido de septiembre de 2026.")

st.subheader("⚙️ Rentabilidad técnica")
st.caption("Coste interno utilizado: 22 €/hora. El margen es técnico, no beneficio contable.")

if not clientes_margen.empty:
    c_margen = col_existente(clientes_margen, ["margen_tecnico", "margen", "margen_12m"])
    c_coste = col_existente(clientes_margen, ["coste_tecnico", "coste_12m", "coste"])
    c_ingresos = col_existente(clientes_margen, ["ingresos_12m", "ingresos", "mrr_12m", "revenue_12m"])

    if c_margen:
        margen = pd.to_numeric(clientes_margen[c_margen], errors="coerce")
        negativos = clientes_margen[margen < 0].copy()

        c1, c2, c3 = st.columns(3)
        c1.metric("Clientes con margen negativo", len(negativos))
        c2.metric(
            "Coste técnico 12M",
            euros(pd.to_numeric(clientes_margen[c_coste], errors="coerce").sum())
            if c_coste else "—"
        )
        c3.metric(
            "Ingresos analizados 12M",
            euros(pd.to_numeric(clientes_margen[c_ingresos], errors="coerce").sum())
            if c_ingresos else "—"
        )

        if negativos.empty:
            st.success("No se han identificado clientes con margen técnico negativo.")
        else:
            st.warning(f"Hay {len(negativos)} clientes cuyo coste técnico supera sus ingresos.")
            st.dataframe(negativos, use_container_width=True, hide_index=True)
    else:
        st.info("El cálculo de margen existe, pero no se ha identificado su columna automáticamente.")
else:
    st.success("No se han identificado clientes con margen técnico negativo en el análisis realizado.")

st.subheader("🎯 Riesgo comercial")
st.markdown("**Contratos cuya permanencia vence en los próximos 90 días**")

if not contratos_proximos_vencer.empty:
    datos = contratos_proximos_vencer.copy()
    columnas = [c for c in [
        "id_contrato", "id_cliente", "servicio",
        "fecha_fin_permanencia", "mrr", "cuota_mensual"
    ] if c in datos.columns]
    if columnas:
        datos = datos[columnas]
    st.dataframe(datos, use_container_width=True, hide_index=True)
    st.warning(
        f"{len(contratos_proximos_vencer)} contratos requieren seguimiento comercial."
    )
    st.info(
        f"MRR conocido asociado: {euros(riesgo)} al mes. "
        "El riesgo real puede ser superior por contratos sin tarifa válida."
    )
else:
    st.success("No hay permanencias venciendo en los próximos 90 días.")

st.subheader("🛒 Oportunidades de cross-selling")
st.markdown("**Clientes con un único servicio activo**")

if not clientes_un_servicio.empty:
    st.write(f"Se han identificado **{len(clientes_un_servicio)} clientes**.")
    datos = clientes_un_servicio.copy()
    columnas = [c for c in [
        "id_cliente", "nombre", "sector", "comercial",
        "servicio", "numero_servicios", "mrr"
    ] if c in datos.columns]
    if columnas:
        datos = datos[columnas]
    st.dataframe(datos, use_container_width=True, hide_index=True)
    st.caption(
        "Son candidatos a cross-selling. El dataset no permite recomendar "
        "un producto concreto sin inventar información."
    )
else:
    st.info("No se han identificado clientes con un único servicio.")

st.markdown("**Clientes sin actividad técnica reciente**")
if not clientes_sin_actividad.empty:
    st.write(f"Se han detectado **{len(clientes_sin_actividad)} clientes** que requieren revisión.")
    st.dataframe(clientes_sin_actividad, use_container_width=True, hide_index=True)
else:
    st.success("No se han detectado clientes sin actividad técnica reciente.")

st.subheader("👥 Evolución de clientes")
if hasattr(calculos, "altas_clientes"):
    altas_clientes = calculos.altas_clientes
    total_altas_clientes = int(altas_clientes["altas_clientes"].sum()) if "altas_clientes" in altas_clientes else 0
    st.metric("Altas de clientes en los últimos 12 meses", total_altas_clientes)

st.info(
    "El dataset no contiene una fecha de baja específica de cliente. "
    "Por tanto, no se inventa una métrica de bajas de clientes; "
    "las bajas analizadas son bajas de contratos."
)

st.subheader("🤖 Resumen ejecutivo")
st.write(
    "El botón siguiente genera una lectura ejecutiva basada en los indicadores "
    "calculados. También queda preparado el prompt exacto para una futura "
    "integración con un LLM."
)

with st.expander("Ver prompt exacto del LLM"):
    st.code(prompt_llm(), language="text")

st.button(
    "✨ Generar resumen ejecutivo (LLM)",
    type="primary",
    use_container_width=True,
    disabled=True,
)

st.info(
    "La integración con el modelo de lenguaje queda preparada pero desactivada "
    "porque no se utiliza una API de pago para esta prueba, tal como permite "
    "el enunciado."
)

st.markdown("**Ejemplo de respuesta esperada:**")
st.write(
    "El negocio presenta una evolución negativa en los últimos 12 meses: "
    "el MRR conocido ha pasado de 25.482,39 € a 23.805,85 €, mientras que "
    "se han producido 3 altas frente a 10 bajas de contratos. Los cinco "
    "mayores clientes concentran el 34,09 % del MRR conocido, por lo que "
    "existe una dependencia relevante de los principales clientes. Además, "
    "16 contratos tienen una permanencia que vence en los próximos 90 días, "
    "con al menos 1.341,19 € de MRR mensual conocido en riesgo. Desde el "
    "punto de vista comercial, hay 16 clientes con un único servicio activo "
    "que pueden ser candidatos a venta cruzada y 21 clientes sin actividad "
    "técnica reciente o registrada que conviene revisar. El análisis de "
    "rentabilidad técnica no identifica clientes con margen negativo usando "
    "un coste interno de 22 €/hora."
)

st.caption(
    "La respuesta anterior es únicamente el ejemplo solicitado en el enunciado; "
    "no se presenta como una respuesta generada realmente por un LLM."
)

st.subheader("🔎 Calidad de datos")
with st.expander("Incidencias detectadas y tratamiento"):
    st.markdown("""
- Contrato duplicado: se elimina el duplicado exacto para los cálculos.
- Fechas de contrato incoherentes: no se inventan correcciones.
- Contratos sin tarifa válida: se excluyen del MRR cuando no existe un importe válido.
- Tarifas con importe vacío: se conserva el último importe válido cuando existe.
- Horas negativas: no se convierten artificialmente en positivas.
- Partes de horas de clientes inexistentes: se excluyen del análisis de clientes.
- Contratos suspendidos: se consideran sin MRR mientras están suspendidos.
- No existe una fecha de baja de cliente: no se inventa una métrica.
""")
