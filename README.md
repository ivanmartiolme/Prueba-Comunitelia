# Cuadro de mando de dirección — Comunitelia

Prueba técnica para el puesto de desarrollo de herramientas y productos con IA.

## 1. Objetivo

La aplicación analiza cuatro CSV de una empresa de servicios tecnológicos recurrentes y presenta un cuadro de mando orientado a Dirección General y al departamento comercial.

La aplicación responde a:

1. Evolución del MRR durante los últimos 12 meses.
2. Altas y bajas de contratos y evolución de la base contractual.
3. Concentración de ingresos entre los principales clientes.
4. Clientes cuyo coste técnico estimado puede superar sus ingresos.
5. Contratos cuya permanencia vence en los próximos 90 días.
6. Clientes con un único servicio activo, como candidatos a venta cruzada.
7. Clientes sin actividad técnica reciente.

Fecha de referencia utilizada: **30/09/2026**.

## 2. Estructura

```text
prueba-comunitelia/
│
├── app.py
├── calculos.py
├── requirements.txt
├── README.md
├── DECISIONES.md
│
└── prueba-datos/
    ├── clientes.csv
    ├── contratos.csv
    ├── tarifas.csv
    └── partes_horas.csv
```

### Archivos principales

- `calculos.py`: carga, limpieza, tratamiento de anomalías y cálculos de negocio.
- `app.py`: interfaz del cuadro de mando desarrollada con Streamlit.
- `requirements.txt`: dependencias necesarias.
- `DECISIONES.md`: supuestos, anomalías, preguntas y elementos deliberadamente no incluidos.
- `prueba-datos/`: CSV proporcionados para la prueba.

## 3. Requisitos

- Python 3.10 o superior.
- Las dependencias indicadas en `requirements.txt`.

## 4. Instalación

Abrir una terminal dentro de la carpeta raíz del proyecto y ejecutar:

```bash
pip install -r requirements.txt
```

## 5. Ejecución

Desde la carpeta raíz:

```bash
streamlit run app.py
```

La aplicación se abrirá en el navegador.

## 6. Criterios principales de cálculo

### MRR

Se calcula para cada uno de los 12 cierres mensuales tomando la tarifa válida más reciente disponible para cada contrato en ese momento.

Una tarifa no se aplica antes de la fecha de inicio del contrato.

Si aparece una tarifa posterior con importe vacío, se conserva el último importe válido conocido. Si no existe ningún importe válido, ese contrato no se inventa ni se incluye en el MRR conocido.

Los contratos suspendidos se consideran sin MRR mientras están suspendidos.

### Coste técnico

Se utiliza el coste indicado en el enunciado:

```text
22 € / hora de técnico
```

El análisis compara los ingresos del periodo de 12 meses con el coste técnico de las horas válidas imputadas al cliente.

Este resultado se denomina **margen técnico** y no pretende representar el beneficio contable de la empresa.

### Actividad de clientes

Se considera que un cliente requiere revisión cuando:

- no tiene actividad técnica registrada, o
- su última actividad tiene una antigüedad superior a 90 días respecto a la fecha de referencia.

### Permanencias

Se calcula la fecha de finalización de la permanencia a partir de:

```text
fecha_alta + permanencia_meses
```

y se buscan los contratos activos cuya fecha de finalización se encuentra entre el 30/09/2026 y los 90 días posteriores.

## 7. IA

El enunciado permite no realizar una llamada de pago a una API.

Por ello, la aplicación deja preparada y desactivada la integración con un modelo de lenguaje. El botón aparece en el dashboard, pero no realiza una llamada externa.

### Prompt exacto

```text
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
```

### Ejemplo de respuesta esperada

> El negocio presenta una evolución negativa en los últimos 12 meses: el MRR conocido ha pasado de 25.482,39 € a 23.805,85 €, mientras que se han producido 3 altas frente a 10 bajas de contratos. Los cinco mayores clientes concentran el 34,09 % del MRR conocido, por lo que existe una dependencia relevante de los principales clientes. Además, 16 contratos tienen una permanencia que vence en los próximos 90 días, con al menos 1.341,19 € de MRR mensual conocido en riesgo. Desde el punto de vista comercial, hay 16 clientes con un único servicio activo que pueden ser candidatos a venta cruzada y 21 clientes sin actividad técnica reciente o registrada que conviene revisar. El análisis de rentabilidad técnica no identifica clientes con margen negativo usando un coste interno de 22 €/hora.

La respuesta anterior es un ejemplo de referencia, no una llamada real a un modelo de lenguaje.

## 8. Limitaciones conocidas

- No existe una fecha de baja de cliente en los datos, por lo que no se calcula una métrica de bajas de clientes.
- El MRR se denomina "conocido" porque existen contratos sin una tarifa válida disponible.
- El margen calculado es técnico y no incluye otros costes empresariales.
- Los candidatos a venta cruzada se identifican por tener un único servicio, pero los datos no contienen información suficiente para recomendar qué producto concreto ofrecer.
