import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Fecha de referencia indicada en la prueba técnica
FECHA_REFERENCIA = pd.Timestamp("2026-09-30")


# ============================================================
# CARGA DE DATOS
# ============================================================

clientes = pd.read_csv(
    "prueba-datos/clientes.csv",
    sep=";"
)

contratos = pd.read_csv(
    "prueba-datos/contratos.csv",
    sep=";"
)

tarifas = pd.read_csv(
    "prueba-datos/tarifas.csv",
    sep=";"
)

partes_horas = pd.read_csv(
    "prueba-datos/partes_horas.csv",
    sep=";"
)


# ============================================================
# CONVERSIÓN DE FECHAS
# ============================================================

clientes["fecha_alta_cliente"] = pd.to_datetime(
    clientes["fecha_alta_cliente"],
    dayfirst=True,
    errors="coerce"
)

contratos["fecha_alta"] = pd.to_datetime(
    contratos["fecha_alta"],
    dayfirst=True,
    errors="coerce"
)

contratos["fecha_baja"] = pd.to_datetime(
    contratos["fecha_baja"],
    dayfirst=True,
    errors="coerce"
)

tarifas["vigente_desde"] = pd.to_datetime(
    tarifas["vigente_desde"],
    dayfirst=True,
    errors="coerce"
)

# Convertimos las cuotas mensuales a números
tarifas["cuota_mensual"] = (
    tarifas["cuota_mensual"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
)

tarifas["cuota_mensual"] = pd.to_numeric(
    tarifas["cuota_mensual"],
    errors="coerce"
)

partes_horas["fecha"] = pd.to_datetime(
    partes_horas["fecha"],
    dayfirst=True,
    errors="coerce"
)

# Convertimos las horas a valores numéricos
partes_horas["horas"] = pd.to_numeric(
    partes_horas["horas"],
    errors="coerce"
)


# ============================================================
# COMPROBACIÓN
# ============================================================

print("Clientes:", len(clientes))
print("Contratos:", len(contratos))
print("Tarifas:", len(tarifas))
print("Partes de horas:", len(partes_horas))

print("\nFecha de referencia:", FECHA_REFERENCIA)

print("\nDatos cargados correctamente.")

# ============================================================
# CONTROL DE DUPLICADOS
# ============================================================

# Detectamos contratos duplicados exactamente iguales
duplicados_contratos = contratos[
    contratos.duplicated(keep=False)
]

print("\nContratos duplicados detectados:")
print(duplicados_contratos)

# Eliminamos duplicados exactos para los cálculos
contratos_calculo = contratos.drop_duplicates().copy()

print("\nContratos originales:", len(contratos))
print("Contratos para cálculo:", len(contratos_calculo))

# ============================================================
# CONTROL DE FECHAS DE CONTRATOS
# ============================================================

# Detectamos contratos cuya fecha de baja es anterior
# a su fecha de alta
contratos_fecha_invalida = contratos_calculo[
    contratos_calculo["fecha_baja"].notna()
    & (contratos_calculo["fecha_baja"] < contratos_calculo["fecha_alta"])
]

print("\nContratos con fecha de baja anterior al alta:")
print(
    contratos_fecha_invalida[
        [
            "id_contrato",
            "id_cliente",
            "fecha_alta",
            "fecha_baja",
            "estado"
        ]
    ]
)

# ============================================================
# CONTRATOS VÁLIDOS PARA CÁLCULOS TEMPORALES
# ============================================================

# Excluimos contratos cuya fecha de baja sea anterior
# a su fecha de alta.
contratos_validos = contratos_calculo[
    ~(
        contratos_calculo["fecha_baja"].notna()
        & (contratos_calculo["fecha_baja"] < contratos_calculo["fecha_alta"])
    )
].copy()

print("\nContratos válidos para cálculos temporales:", len(contratos_validos))

# ============================================================
# CONTRATOS ANTERIORES AL ALTA DEL CLIENTE
# ============================================================

# Unimos la fecha de alta del cliente a cada contrato
contratos_con_cliente = contratos_validos.merge(
    clientes[["id_cliente", "fecha_alta_cliente"]],
    on="id_cliente",
    how="left"
)

# Detectamos contratos que empiezan antes de que conste
# el alta del cliente
contratos_antes_cliente = contratos_con_cliente[
    contratos_con_cliente["fecha_alta"]
    < contratos_con_cliente["fecha_alta_cliente"]
]

print("\nContratos anteriores al alta del cliente:")
print(
    contratos_antes_cliente[
        [
            "id_contrato",
            "id_cliente",
            "fecha_alta",
            "fecha_alta_cliente"
        ]
    ]
)

print(
    "\nNúmero de contratos anteriores al alta del cliente:",
    len(contratos_antes_cliente)
)

# ============================================================
# CONTRATOS SIN TARIFA
# ============================================================

# Obtenemos los contratos que tienen al menos una tarifa
contratos_con_tarifa = tarifas["id_contrato"].unique()

# Buscamos contratos válidos que no aparecen en tarifas.csv
contratos_sin_tarifa = contratos_validos[
    ~contratos_validos["id_contrato"].isin(contratos_con_tarifa)
].copy()

print("\nContratos sin tarifa:")
print(
    contratos_sin_tarifa[
        [
            "id_contrato",
            "id_cliente",
            "servicio",
            "fecha_alta",
            "estado"
        ]
    ]
)

print(
    "\nNúmero de contratos sin tarifa:",
    len(contratos_sin_tarifa)
)

# ============================================================
# TARIFAS ANTERIORES AL INICIO DEL CONTRATO
# ============================================================

tarifas_con_contrato = tarifas.merge(
    contratos_validos[["id_contrato", "fecha_alta"]],
    on="id_contrato",
    how="inner"
)

tarifas_antes_contrato = tarifas_con_contrato[
    tarifas_con_contrato["vigente_desde"]
    < tarifas_con_contrato["fecha_alta"]
]

print("\nTarifas anteriores al inicio del contrato:")
print(
    tarifas_antes_contrato[
        [
            "id_contrato",
            "cuota_mensual",
            "vigente_desde",
            "fecha_alta"
        ]
    ]
)

print(
    "\nNúmero de tarifas anteriores al contrato:",
    len(tarifas_antes_contrato)
)

# ============================================================
# CONTROL DE HORAS NEGATIVAS
# ============================================================

partes_horas_negativas = partes_horas[
    partes_horas["horas"] < 0
].copy()

print("\nPartes de horas con horas negativas:")
print(
    partes_horas_negativas[
        [
            "id_parte",
            "id_cliente",
            "fecha",
            "tecnico",
            "horas",
            "tipo"
        ]
    ]
)

print(
    "\nNúmero de partes con horas negativas:",
    len(partes_horas_negativas)
)

# ============================================================
# PARTES DE HORAS DE CLIENTES INEXISTENTES
# ============================================================

clientes_validos = clientes["id_cliente"].unique()

partes_cliente_inexistente = partes_horas[
    ~partes_horas["id_cliente"].isin(clientes_validos)
].copy()

print("\nPartes de horas de clientes inexistentes:")
print(
    partes_cliente_inexistente[
        [
            "id_parte",
            "id_cliente",
            "fecha",
            "horas",
            "tipo"
        ]
    ]
)

print(
    "\nNúmero de partes de clientes inexistentes:",
    len(partes_cliente_inexistente)
)

# ============================================================
# CONTRATOS SUSPENDIDOS
# ============================================================

contratos_suspendidos = contratos_validos[
    contratos_validos["estado"].str.lower() == "suspendido"
].copy()

print("\nContratos suspendidos:")
print(
    contratos_suspendidos[
        [
            "id_contrato",
            "id_cliente",
            "servicio",
            "fecha_alta",
            "fecha_baja",
            "estado"
        ]
    ]
)

print(
    "\nNúmero de contratos suspendidos:",
    len(contratos_suspendidos)
)

# ============================================================
# MRR MENSUAL - ÚLTIMOS 12 MESES
# ============================================================

def calcular_mrr_mensual():

    # Creamos los últimos 12 meses incluyendo septiembre de 2026
    meses = pd.date_range(
        end=FECHA_REFERENCIA,
        periods=12,
        freq="ME"
    )

    resultados = []

    for fecha_mes in meses:

        mrr_mes = 0

        for _, contrato in contratos_validos.iterrows():

            # ------------------------------------------------
            # Comprobamos si el contrato estaba activo
            # al final de ese mes
            # ------------------------------------------------

            contrato_activo = (
                contrato["fecha_alta"] <= fecha_mes
                and (
                    pd.isna(contrato["fecha_baja"])
                    or contrato["fecha_baja"] >= fecha_mes
                )
            )

            # Los contratos suspendidos no generan MRR
            if contrato["estado"].lower() == "suspendido":
                contrato_activo = False

            if not contrato_activo:
                continue

            # ------------------------------------------------
            # Buscamos las tarifas aplicables a ese contrato
            # ------------------------------------------------

            tarifas_contrato = tarifas[
                (tarifas["id_contrato"] == contrato["id_contrato"])
                & (tarifas["vigente_desde"] <= fecha_mes)
                & (tarifas["vigente_desde"] >= contrato["fecha_alta"])
            ].copy()

            # Si no tiene ninguna tarifa aplicable,
            # no podemos calcular su MRR
            if tarifas_contrato.empty:
                continue

            # ------------------------------------------------
            # Nos quedamos solo con tarifas que tengan
            # un importe conocido
            # ------------------------------------------------

            tarifas_con_importe = tarifas_contrato[
                tarifas_contrato["cuota_mensual"].notna()
            ].copy()

            # Si no existe ninguna tarifa con importe conocido,
            # no podemos calcular el MRR del contrato
            if tarifas_con_importe.empty:
                continue

            # ------------------------------------------------
            # Cogemos la última tarifa conocida
            # ------------------------------------------------

            tarifa_actual = tarifas_con_importe.sort_values(
                "vigente_desde"
            ).iloc[-1]

            mrr_mes += tarifa_actual["cuota_mensual"]

        resultados.append(
            {
                "mes": fecha_mes,
                "mrr": mrr_mes
            }
        )

    return pd.DataFrame(resultados)


# Calculamos el MRR
mrr_mensual = calcular_mrr_mensual()

print("\nMRR mensual:")
print(mrr_mensual)

# ============================================================
# ALTAS Y BAJAS MENSUALES DE CONTRATOS
# ============================================================

def calcular_altas_bajas_contratos():

    meses = pd.date_range(
        end=FECHA_REFERENCIA,
        periods=12,
        freq="ME"
    )

    resultados = []

    for fecha_mes in meses:

        inicio_mes = fecha_mes.replace(day=1)

        altas = (
            (contratos_validos["fecha_alta"] >= inicio_mes)
            & (contratos_validos["fecha_alta"] <= fecha_mes)
        ).sum()

        bajas = (
            contratos_validos["fecha_baja"].notna()
            & (contratos_validos["fecha_baja"] >= inicio_mes)
            & (contratos_validos["fecha_baja"] <= fecha_mes)
        ).sum()

        resultados.append(
            {
                "mes": fecha_mes,
                "altas": altas,
                "bajas": bajas,
                "saldo": altas - bajas
            }
        )

    return pd.DataFrame(resultados)


altas_bajas_contratos = calcular_altas_bajas_contratos()

print("\nAltas y bajas mensuales de contratos:")
print(altas_bajas_contratos)

# ============================================================
# ALTAS MENSUALES DE CLIENTES
# ============================================================

def calcular_altas_clientes():

    meses = pd.date_range(
        end=FECHA_REFERENCIA,
        periods=12,
        freq="ME"
    )

    resultados = []

    for fecha_mes in meses:

        inicio_mes = fecha_mes.replace(day=1)

        altas = (
            (clientes["fecha_alta_cliente"] >= inicio_mes)
            & (clientes["fecha_alta_cliente"] <= fecha_mes)
        ).sum()

        resultados.append(
            {
                "mes": fecha_mes,
                "altas_clientes": altas
            }
        )

    return pd.DataFrame(resultados)


altas_clientes = calcular_altas_clientes()

print("\nAltas mensuales de clientes:")
print(altas_clientes)

# ============================================================
# CONCENTRACIÓN DE INGRESOS POR CLIENTE
# ============================================================

def calcular_mrr_por_cliente(fecha_mes):

    resultados = []

    for _, contrato in contratos_validos.iterrows():

        contrato_activo = (
            contrato["fecha_alta"] <= fecha_mes
            and (
                pd.isna(contrato["fecha_baja"])
                or contrato["fecha_baja"] >= fecha_mes
            )
        )

        if contrato["estado"].lower() == "suspendido":
            contrato_activo = False

        if not contrato_activo:
            continue

        tarifas_contrato = tarifas[
            (tarifas["id_contrato"] == contrato["id_contrato"])
            & (tarifas["vigente_desde"] <= fecha_mes)
            & (tarifas["vigente_desde"] >= contrato["fecha_alta"])
            & (tarifas["cuota_mensual"].notna())
        ].copy()

        if tarifas_contrato.empty:
            continue

        tarifa_actual = tarifas_contrato.sort_values(
            "vigente_desde"
        ).iloc[-1]

        resultados.append(
            {
                "id_cliente": contrato["id_cliente"],
                "mrr": tarifa_actual["cuota_mensual"]
            }
        )

    resultado = pd.DataFrame(resultados)

    if resultado.empty:
        return resultado

    return (
        resultado
        .groupby("id_cliente", as_index=False)["mrr"]
        .sum()
        .sort_values("mrr", ascending=False)
    )


mrr_por_cliente = calcular_mrr_por_cliente(FECHA_REFERENCIA)

mrr_total = mrr_por_cliente["mrr"].sum()

mrr_por_cliente["porcentaje_mrr"] = (
    mrr_por_cliente["mrr"] / mrr_total * 100
)

print("\nMRR por cliente - septiembre 2026:")
print(mrr_por_cliente.head(10))

print("\nMRR total:", round(mrr_total, 2))

print("\nTop 5 clientes:")
print(
    mrr_por_cliente.head(5)
)

print("\nConcentración Top 5:")
print(
    round(
        mrr_por_cliente.head(5)["mrr"].sum()
        / mrr_total
        * 100,
        2
    ),
    "%"
)

print("\nConcentración Top 10:")
print(
    round(
        mrr_por_cliente.head(10)["mrr"].sum()
        / mrr_total
        * 100,
        2
    ),
    "%"
)

# ============================================================
# CLIENTES QUE CUESTAN MÁS DE LO QUE GENERAN
# ============================================================

COSTE_HORA_TECNICO = 22

fecha_inicio_12_meses = (
    FECHA_REFERENCIA - pd.DateOffset(months=12) + pd.Timedelta(days=1)
)

# ------------------------------------------------------------
# INGRESOS DE LOS ÚLTIMOS 12 MESES POR CLIENTE
# ------------------------------------------------------------

def calcular_ingresos_12_meses():

    meses = pd.date_range(
        end=FECHA_REFERENCIA,
        periods=12,
        freq="ME"
    )

    resultados = []

    for fecha_mes in meses:

        mrr_mes_clientes = calcular_mrr_por_cliente(fecha_mes)

        if not mrr_mes_clientes.empty:

            mrr_mes_clientes["mes"] = fecha_mes

            resultados.append(
                mrr_mes_clientes[
                    [
                        "id_cliente",
                        "mrr",
                        "mes"
                    ]
                ]
            )

    if not resultados:
        return pd.DataFrame(
            columns=["id_cliente", "ingresos_12_meses"]
        )

    ingresos = pd.concat(resultados)

    ingresos = (
        ingresos
        .groupby("id_cliente", as_index=False)["mrr"]
        .sum()
        .rename(
            columns={
                "mrr": "ingresos_12_meses"
            }
        )
    )

    return ingresos


ingresos_12_meses = calcular_ingresos_12_meses()


# ------------------------------------------------------------
# COSTE TÉCNICO DE LOS ÚLTIMOS 12 MESES
# ------------------------------------------------------------

partes_horas_validos = partes_horas[
    (partes_horas["fecha"] >= fecha_inicio_12_meses)
    & (partes_horas["fecha"] <= FECHA_REFERENCIA)
    & (partes_horas["horas"].notna())
    & (partes_horas["horas"] >= 0)
    & (partes_horas["id_cliente"].isin(clientes_validos))
].copy()

coste_tecnico = (
    partes_horas_validos
    .groupby("id_cliente", as_index=False)["horas"]
    .sum()
)

coste_tecnico["coste_tecnico_12_meses"] = (
    coste_tecnico["horas"] * COSTE_HORA_TECNICO
)

coste_tecnico = coste_tecnico[
    [
        "id_cliente",
        "horas",
        "coste_tecnico_12_meses"
    ]
]


# ------------------------------------------------------------
# COMPARACIÓN INGRESOS VS COSTE
# ------------------------------------------------------------

rentabilidad_clientes = ingresos_12_meses.merge(
    coste_tecnico,
    on="id_cliente",
    how="left"
)

rentabilidad_clientes["horas"] = (
    rentabilidad_clientes["horas"].fillna(0)
)

rentabilidad_clientes["coste_tecnico_12_meses"] = (
    rentabilidad_clientes["coste_tecnico_12_meses"].fillna(0)
)

rentabilidad_clientes["margen_tecnico"] = (
    rentabilidad_clientes["ingresos_12_meses"]
    - rentabilidad_clientes["coste_tecnico_12_meses"]
)

rentabilidad_clientes = rentabilidad_clientes.sort_values(
    "margen_tecnico"
)

print("\nClientes que cuestan más de lo que generan:")
print(
    rentabilidad_clientes[
        rentabilidad_clientes["margen_tecnico"] < 0
    ]
)

print(
    "\nNúmero de clientes con margen técnico negativo:",
    (
        rentabilidad_clientes["margen_tecnico"] < 0
    ).sum()
)

# ============================================================
# PERMANENCIAS QUE VENCEN EN LOS PRÓXIMOS 90 DÍAS
# ============================================================

FECHA_FIN_90_DIAS = FECHA_REFERENCIA + pd.Timedelta(days=90)


contratos_permanencia = contratos_validos.copy()

# Calculamos la fecha de fin de permanencia
contratos_permanencia["fecha_fin_permanencia"] = (
    contratos_permanencia["fecha_alta"]
    + contratos_permanencia["permanencia_meses"].apply(
        lambda meses: pd.DateOffset(months=int(meses))
    )
)


# Solo contratos activos en la fecha de referencia
contratos_permanencia = contratos_permanencia[
    (contratos_permanencia["fecha_alta"] <= FECHA_REFERENCIA)
    & (
        contratos_permanencia["fecha_baja"].isna()
        | (
            contratos_permanencia["fecha_baja"]
            >= FECHA_REFERENCIA
        )
    )
    & (
        contratos_permanencia["estado"].str.lower()
        == "activo"
    )
]


# Permanencias que vencen dentro de los próximos 90 días
contratos_proximos_vencer = contratos_permanencia[
    (contratos_permanencia["fecha_fin_permanencia"] >= FECHA_REFERENCIA)
    & (
        contratos_permanencia["fecha_fin_permanencia"]
        <= FECHA_FIN_90_DIAS
    )
].copy()


# ------------------------------------------------------------
# OBTENER CUOTA ACTUAL DE CADA CONTRATO
# ------------------------------------------------------------

cuotas_actuales = []

for _, contrato in contratos_proximos_vencer.iterrows():

    tarifas_contrato = tarifas[
        (tarifas["id_contrato"] == contrato["id_contrato"])
        & (tarifas["vigente_desde"] <= FECHA_REFERENCIA)
        & (tarifas["vigente_desde"] >= contrato["fecha_alta"])
        & (tarifas["cuota_mensual"].notna())
    ].copy()

    if tarifas_contrato.empty:
        cuota = None
    else:
        tarifa_actual = tarifas_contrato.sort_values(
            "vigente_desde"
        ).iloc[-1]

        cuota = tarifa_actual["cuota_mensual"]

    cuotas_actuales.append(cuota)


contratos_proximos_vencer["cuota_mensual"] = cuotas_actuales


# ------------------------------------------------------------
# MOSTRAR RESULTADO
# ------------------------------------------------------------

print("\nContratos cuya permanencia vence en los próximos 90 días:")

print(
    contratos_proximos_vencer[
        [
            "id_contrato",
            "id_cliente",
            "servicio",
            "fecha_alta",
            "permanencia_meses",
            "fecha_fin_permanencia",
            "cuota_mensual"
        ]
    ].sort_values("fecha_fin_permanencia")
)


dinero_en_riesgo = (
    contratos_proximos_vencer["cuota_mensual"]
    .fillna(0)
    .sum()
)


print(
    "\nNúmero de contratos con permanencia próxima a vencer:",
    len(contratos_proximos_vencer)
)

print(
    "\nMRR mensual potencialmente en riesgo:",
    round(dinero_en_riesgo, 2),
    "€"
)

print(
    "\nContratos sin cuota válida:",
    contratos_proximos_vencer["cuota_mensual"].isna().sum()
)

# ============================================================
# CLIENTES CON UN ÚNICO SERVICIO
# ============================================================

# Contratos activos en la fecha de referencia
contratos_activos = contratos_validos[
    (contratos_validos["fecha_alta"] <= FECHA_REFERENCIA)
    & (
        contratos_validos["fecha_baja"].isna()
        | (
            contratos_validos["fecha_baja"] >= FECHA_REFERENCIA
        )
    )
    & (
        contratos_validos["estado"].str.lower() == "activo"
    )
].copy()


# Contamos servicios distintos por cliente
servicios_por_cliente = (
    contratos_activos
    .groupby("id_cliente")["servicio"]
    .nunique()
    .reset_index(name="numero_servicios")
)


# Nos quedamos únicamente con clientes que tienen un servicio
clientes_un_servicio = servicios_por_cliente[
    servicios_por_cliente["numero_servicios"] == 1
].copy()


# Añadimos el nombre del cliente
clientes_un_servicio = clientes_un_servicio.merge(
    clientes[
        [
            "id_cliente",
            "nombre",
            "sector",
            "comercial"
        ]
    ],
    on="id_cliente",
    how="left"
)


# Añadimos el servicio que tiene
servicio_unico = contratos_activos[
    contratos_activos["id_cliente"].isin(
        clientes_un_servicio["id_cliente"]
    )
][
    [
        "id_cliente",
        "servicio"
    ]
].drop_duplicates()


clientes_un_servicio = clientes_un_servicio.merge(
    servicio_unico,
    on="id_cliente",
    how="left"
)


# Añadimos el MRR actual del cliente
clientes_un_servicio = clientes_un_servicio.merge(
    mrr_por_cliente[
        [
            "id_cliente",
            "mrr"
        ]
    ],
    on="id_cliente",
    how="left"
)


clientes_un_servicio = clientes_un_servicio.sort_values(
    "mrr",
    ascending=False
)


print("\nClientes con un único servicio:")
print(
    clientes_un_servicio[
        [
            "id_cliente",
            "nombre",
            "sector",
            "comercial",
            "servicio",
            "mrr"
        ]
    ]
)

print(
    "\nNúmero de clientes con un único servicio:",
    len(clientes_un_servicio)
)

# ============================================================
# CLIENTES SIN ACTIVIDAD TÉCNICA RECIENTE
# ============================================================

DIAS_SIN_ACTIVIDAD = 90

fecha_limite_actividad = (
    FECHA_REFERENCIA
    - pd.Timedelta(days=DIAS_SIN_ACTIVIDAD)
)


# Partes válidos para calcular actividad
partes_horas_validos_actividad = partes_horas[
    (partes_horas["fecha"].notna())
    & (partes_horas["fecha"] <= FECHA_REFERENCIA)
    & (partes_horas["id_cliente"].isin(clientes_validos))
].copy()


# Última actividad registrada por cliente
ultima_actividad = (
    partes_horas_validos_actividad
    .groupby("id_cliente")["fecha"]
    .max()
    .reset_index()
    .rename(
        columns={
            "fecha": "ultima_actividad"
        }
    )
)


# Partimos de todos los clientes
clientes_actividad = clientes[
    [
        "id_cliente",
        "nombre",
        "sector",
        "comercial"
    ]
].copy()


clientes_actividad = clientes_actividad.merge(
    ultima_actividad,
    on="id_cliente",
    how="left"
)


# Calculamos días desde la última actividad
clientes_actividad["dias_sin_actividad"] = (
    FECHA_REFERENCIA
    - clientes_actividad["ultima_actividad"]
).dt.days


# Clasificamos la situación
def clasificar_actividad(row):

    if pd.isna(row["ultima_actividad"]):
        return "Sin actividad registrada"

    if row["dias_sin_actividad"] > DIAS_SIN_ACTIVIDAD:
        return "Sin actividad >90 días"

    return "Actividad reciente"


clientes_actividad["situacion_actividad"] = (
    clientes_actividad.apply(
        clasificar_actividad,
        axis=1
    )
)


# Solo mostramos los clientes que requieren atención
clientes_sin_actividad = clientes_actividad[
    clientes_actividad["situacion_actividad"] != "Actividad reciente"
].copy()


clientes_sin_actividad = clientes_sin_actividad.sort_values(
    "dias_sin_actividad",
    ascending=False,
    na_position="first"
)


print("\nClientes sin actividad técnica reciente:")
print(
    clientes_sin_actividad[
        [
            "id_cliente",
            "nombre",
            "sector",
            "comercial",
            "ultima_actividad",
            "dias_sin_actividad",
            "situacion_actividad"
        ]
    ]
)


print(
    "\nNúmero de clientes sin actividad >90 días:",
    (
        clientes_sin_actividad["situacion_actividad"]
        == "Sin actividad >90 días"
    ).sum()
)


print(
    "Número de clientes sin actividad registrada:",
    (
        clientes_sin_actividad["situacion_actividad"]
        == "Sin actividad registrada"
    ).sum()
)


# ============================================================
# CONTROL DE TARIFAS SIN IMPORTE
# ============================================================

tarifas_sin_importe = tarifas[
    tarifas["cuota_mensual"].isna()
].copy()

print("\nTarifas sin importe:")
print(tarifas_sin_importe)

print(
    "\nNúmero de tarifas sin importe:",
    len(tarifas_sin_importe)
)

# ============================================================
# CONTRATOS CON TARIFAS SIN IMPORTE
# ============================================================

contratos_tarifa_sin_importe = contratos_validos[
    contratos_validos["id_contrato"].isin(
        tarifas_sin_importe["id_contrato"]
    )
].copy()

print("\nContratos que tienen alguna tarifa sin importe:")
print(
    contratos_tarifa_sin_importe[
        [
            "id_contrato",
            "id_cliente",
            "servicio",
            "fecha_alta",
            "fecha_baja",
            "estado"
        ]
    ]
)

print(
    "\nNúmero de contratos afectados:",
    len(contratos_tarifa_sin_importe)
)

# ============================================================
# COMPROBACIÓN DE TARIFAS ANTERIORES CON IMPORTE
# ============================================================

for _, tarifa in tarifas_sin_importe.iterrows():

    id_contrato = tarifa["id_contrato"]
    fecha_tarifa = tarifa["vigente_desde"]

    tarifas_anteriores = tarifas[
        (tarifas["id_contrato"] == id_contrato)
        & (tarifas["vigente_desde"] < fecha_tarifa)
        & (tarifas["cuota_mensual"].notna())
    ].sort_values("vigente_desde")

    print(
        f"\nContrato {id_contrato} - "
        f"tarifa sin importe del {fecha_tarifa.date() if pd.notna(fecha_tarifa) else 'sin fecha'}"
    )

    if tarifas_anteriores.empty:
        print("  No tiene ninguna tarifa anterior con importe.")
    else:
        print("  Última tarifa anterior válida:")
        print(
            tarifas_anteriores[
                [
                    "id_contrato",
                    "cuota_mensual",
                    "vigente_desde"
                ]
            ].tail(1)
        )