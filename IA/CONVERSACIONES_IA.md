# CONVERSACIONES_IA

## Prueba técnica — Cuadro de mando de dirección

Este documento recoge una recopilación resumida y estructurada de las interacciones relevantes mantenidas con ChatGPT durante el desarrollo de la prueba técnica de Comunitelia.

El objetivo es dejar constancia de cómo se utilizó la IA como herramienta de apoyo para analizar el enunciado, revisar los datos, detectar anomalías, diseñar los cálculos, desarrollar la aplicación y revisar las decisiones tomadas.

> **Nota:** este documento es una recopilación estructurada de las interacciones relevantes y no una transcripción literal completa de toda la conversación original.

---

## 1. Análisis inicial del enunciado

### Usuario

Se facilitó el enunciado de la prueba técnica y se pidió ayuda para entender los requisitos y plantear el proyecto.

### IA

Se identificaron como requisitos principales:

* Construir un cuadro de mando para dirección general y departamento comercial.
* Responder a las siete preguntas de negocio del enunciado.
* Trabajar con los cuatro CSV proporcionados:

  * `clientes.csv`
  * `contratos.csv`
  * `tarifas.csv`
  * `partes_horas.csv`
* Utilizar como fecha de referencia el 30/09/2026.
* Calcular el MRR y su evolución durante los últimos doce meses.
* Analizar altas y bajas.
* Analizar la concentración de ingresos.
* Comparar ingresos con coste técnico utilizando 22 €/hora.
* Detectar permanencias próximas a vencer.
* Detectar clientes con un único servicio.
* Detectar clientes sin actividad reciente.
* Incorporar un resumen ejecutivo mediante un modelo de lenguaje.
* Si no se dispone de una API, dejar la integración escrita y desactivada, incluyendo el prompt exacto y un ejemplo de respuesta.

También se decidió priorizar una solución pequeña, terminada y defendible frente a una solución excesivamente compleja.

---

## 2. Revisión inicial de los datos

### Usuario

Se proporcionaron los CSV y se comenzó a trabajar con Python y pandas.

Durante el desarrollo apareció inicialmente un error relacionado con una columna que no existía:

`KeyError: 'fecha_alta'`

### IA

Se recomendó comprobar las columnas reales de cada CSV antes de continuar.

Las columnas identificadas fueron:

**clientes.csv**

* `id_cliente`
* `nombre`
* `cif`
* `poblacion`
* `provincia`
* `sector`
* `comercial`
* `fecha_alta_cliente`

**contratos.csv**

* `id_contrato`
* `id_cliente`
* `servicio`
* `fecha_alta`
* `fecha_baja`
* `estado`
* `permanencia_meses`
* `comercial`

**tarifas.csv**

* `id_contrato`
* `cuota_mensual`
* `vigente_desde`

**partes_horas.csv**

* `id_parte`
* `id_cliente`
* `fecha`
* `tecnico`
* `horas`
* `tipo`

Se corrigió el código para utilizar `fecha_alta_cliente` en el fichero de clientes.

---

## 3. Análisis de calidad de datos y anomalías

Una parte importante del trabajo con IA consistió en revisar los datos antes de construir los indicadores.

### 3.1. Clientes

Se detectaron:

* Espacios innecesarios en el nombre de `C1006`.
* CIF duplicado `G93567312`, asociado a `C1001` y `C1055`.

### Decisión

El nombre se normalizó eliminando los espacios innecesarios.

El CIF duplicado no se eliminó porque los datos disponibles no permiten determinar cuál de los dos registros es incorrecto. Se dejó documentado como anomalía.

---

### 3.2. Contratos

Se detectaron:

* Duplicado exacto del contrato `S2018`.
* `S2004` aparece como activo aunque tiene una fecha de baja anterior a la fecha de referencia.
* `S2019` tiene una fecha de baja anterior a su fecha de alta.
* Existen contratos cuya fecha de alta es anterior a la fecha de alta del cliente.
* Existen contratos suspendidos.

### Decisión

El duplicado exacto `S2018` se cuenta una sola vez.

`S2004` se mantiene como anomalía, utilizando las fechas para los cálculos temporales en lugar de inventar una corrección.

`S2019` se excluye de los cálculos temporales porque la secuencia de fechas es incoherente y no existe información suficiente para saber qué fecha debería corregirse.

Los contratos que comienzan antes del alta del cliente se detectan y documentan, pero no se modifican.

Los contratos suspendidos se consideran sin MRR como supuesto de negocio documentado.

---

### 3.3. Tarifas

Se detectaron:

* Tarifas cuya fecha `vigente_desde` es anterior al inicio del contrato.
* Contrato `S2061` sin registro de tarifa.
* Registros de tarifa con `cuota_mensual` vacía.

### Decisión

No se utilizan tarifas anteriores al inicio del contrato.

`S2061` no se incluye en el MRR porque no existe una cuota que permita calcularlo sin inventar información.

Cuando una tarifa está vacía pero existe una tarifa válida anterior, se utiliza la última tarifa válida conocida.

Cuando no existe ninguna tarifa válida anterior, el importe se considera desconocido y el contrato no aporta MRR al cálculo.

---

### 3.4. Partes de horas

Se detectaron:

* Registros con horas negativas.
* Un registro asociado al cliente `C9999`, que no existe en `clientes.csv`.
* Un registro con horas vacías.

### Decisión

Las horas negativas no se transforman mediante valor absoluto porque no se conoce su significado. Se excluyen del cálculo de coste técnico.

Los registros de `C9999` se excluyen del análisis por no existir ese cliente en el maestro.

Los valores desconocidos no se convierten artificialmente en cero.

---

## 4. Diseño del cálculo de MRR

### Usuario

Se planteó cómo calcular correctamente el MRR histórico cuando una tarifa puede cambiar durante la vida de un contrato.

### IA

Se estableció que cada mes debe calcularse utilizando la tarifa que estuviera vigente en ese momento.

Para cada cierre mensual se realiza conceptualmente lo siguiente:

1. Identificar los contratos activos en esa fecha.
2. Excluir contratos suspendidos.
3. Buscar las tarifas vigentes hasta ese mes.
4. No utilizar tarifas anteriores al inicio del contrato.
5. Si existen varias tarifas válidas, utilizar la última vigente.
6. Si una tarifa posterior está vacía pero existe una tarifa válida anterior, mantener la última conocida.
7. Si no existe ninguna tarifa válida, no inventar el importe.

Esto permite conservar correctamente el histórico.

Por ejemplo, si un cliente aumenta su cuota en marzo, el MRR de enero no cambia.

---

## 5. Resultados del MRR

El cálculo de los últimos doce meses produjo:

| Mes             |         MRR |
| --------------- | ----------: |
| Octubre 2025    | 25.482,39 € |
| Noviembre 2025  | 25.150,75 € |
| Diciembre 2025  | 25.291,31 € |
| Enero 2026      | 25.147,77 € |
| Febrero 2026    | 25.188,97 € |
| Marzo 2026      | 25.241,39 € |
| Abril 2026      | 25.165,20 € |
| Mayo 2026       | 24.581,50 € |
| Junio 2026      | 24.581,50 € |
| Julio 2026      | 23.766,86 € |
| Agosto 2026     | 23.805,85 € |
| Septiembre 2026 | 23.805,85 € |

Resultados principales:

* MRR inicial del periodo: **25.482,39 €**
* MRR a 30/09/2026: **23.805,85 €**
* Evolución: **-6,58 % aproximadamente**

---

## 6. Altas y bajas

Se calculó el número de altas y bajas de contratos por mes.

Resultado de los últimos doce meses:

* Altas: **3**
* Bajas: **10**
* Saldo neto: **-7 contratos**

La interpretación es que la base de contratos presenta una señal de contracción durante el periodo.

También se revisó la diferencia entre bajas de contratos y bajas de clientes.

Como el CSV de clientes no contiene una fecha de baja de cliente, no se inventó una métrica de bajas de clientes.

---

## 7. Concentración de ingresos

Se calculó la concentración del MRR a septiembre de 2026.

Resultados:

* MRR total: **23.805,85 €**
* Top 5 clientes: **34,09 %**
* Top 10 clientes: **50,40 %**
* Mayor cliente: `C1003`
* MRR de `C1003`: **3.508,89 €**
* Peso aproximado del mayor cliente: **14,74 %**

Se decidió mostrar tanto el porcentaje acumulado del Top 5 y Top 10 como el ranking de clientes para que dirección pueda identificar rápidamente la concentración.

---

## 8. Coste técnico y margen

### Usuario

Se planteó cómo responder a la pregunta:

> ¿Qué clientes nos están costando más de lo que nos dan?

### IA

Se utilizó el coste interno indicado por el enunciado:

**22 €/hora de técnico.**

Para cada cliente se compara:

`ingresos recurrentes de los últimos 12 meses - horas técnicas válidas × 22 €`

El resultado se denomina **margen técnico**.

Se decidió no llamarlo beneficio porque no se dispone de todos los costes de la empresa.

Resultado obtenido:

* **No hay clientes con margen técnico negativo** bajo este criterio.

La conclusión se presenta con esta limitación explícita.

---

## 9. Permanencias próximas a vencer

Se calculó la fecha de finalización de la permanencia a partir de:

`fecha_alta + permanencia_meses`

Se analizaron los contratos cuyo vencimiento de permanencia se encuentra dentro de los 90 días posteriores al 30/09/2026.

Resultado:

* **16 contratos** con permanencia próxima a vencer.
* Fechas de vencimiento entre **09/10/2026 y 27/12/2026**.
* **1.341,19 € mensuales** de MRR conocido asociado a estos contratos.
* **9 contratos** sin cuota válida conocida.

Por este motivo, el dashboard presenta 1.341,19 € como **MRR conocido en juego**, no como el riesgo total definitivo.

---

## 10. Clientes con un único servicio

Se identificaron:

* **16 clientes** con un único servicio activo.
* **13** tienen MRR conocido.
* **3** no tienen una tarifa válida conocida.
* MRR conocido conjunto: aproximadamente **3.103,27 €/mes**.

La aplicación muestra:

* Cliente.
* Servicio.
* Sector.
* Comercial.
* MRR conocido.

Se decidió no recomendar automáticamente un producto concreto de venta cruzada porque los datos proporcionados no contienen información suficiente para determinar qué producto adicional sería adecuado para cada cliente.

---

## 11. Clientes sin actividad

Se estableció un umbral de **90 días** para identificar clientes sin actividad reciente.

Resultado:

* **21 clientes** requieren atención.
* **13** llevan más de 90 días sin actividad.
* **8** no tienen actividad registrada.

La aplicación diferencia entre:

* `Sin actividad >90 días`
* `Sin actividad registrada`

Se decidió no afirmar que un cliente sin registros no haya recibido ningún contacto comercial, ya que los datos proporcionados solo permiten analizar la actividad registrada en `partes_horas.csv`.

---

## 12. Desarrollo de la aplicación

Se utilizó Streamlit para construir el cuadro de mando.

La aplicación incluye:

* KPI de MRR actual.
* Evolución mensual del MRR.
* Evolución porcentual de 12 meses.
* Altas y bajas de contratos.
* Saldo de contratos.
* Concentración Top 5 y Top 10.
* Ranking de principales clientes.
* Análisis de margen técnico.
* Contratos con permanencia próxima a vencer.
* Clientes con un único servicio.
* Clientes sin actividad reciente.
* Altas de clientes.
* Limitación sobre las bajas de clientes.
* Apartado de calidad de datos.
* Apartado de IA y resumen ejecutivo.

Durante el desarrollo se utilizó la IA para revisar errores de código, plantear correcciones y comprobar que los resultados obtenidos respondían al enunciado.

---

## 13. Integración del resumen ejecutivo mediante IA

### Usuario

Se revisó cómo cumplir el requisito del resumen ejecutivo sin realizar un gasto en una API.

### IA

Se decidió dejar la integración preparada pero desactivada, siguiendo la posibilidad indicada expresamente en el enunciado.

La aplicación contiene:

* El prompt exacto que se enviaría al modelo.
* La información que debería recibir el modelo.
* Un botón de resumen ejecutivo desactivado al no existir una API configurada.
* Un ejemplo de respuesta esperada.

El objetivo del prompt es que el modelo:

1. Resuma la situación del negocio.
2. Explique la evolución del MRR.
3. Señale si la base de contratos crece o se contrae.
4. Destaque la concentración de ingresos.
5. Señale riesgos por permanencias próximas a vencer.
6. Destaque clientes sin actividad.
7. Señale oportunidades comerciales.
8. Distinga datos conocidos de datos incompletos.
9. No invente información.
10. Priorice las acciones que debería considerar dirección.

---

## 14. Revisión del cumplimiento del enunciado

Una vez terminada la aplicación, se utilizó la IA para comprobar si el dashboard respondía a las siete preguntas planteadas.

La revisión confirmó la cobertura de:

1. MRR y evolución durante los últimos doce meses.
2. Altas y bajas y evolución de la base de contratos.
3. Concentración de ingresos.
4. Clientes cuyo coste técnico supera sus ingresos bajo el criterio de 22 €/hora.
5. Permanencias próximas a vencer y dinero mensual conocido en juego.
6. Clientes con un único servicio.
7. Clientes sin actividad reciente.

También se comprobó la presencia de:

* Aplicación.
* README.
* `DECISIONES.md`.
* Prompt exacto del LLM.
* Ejemplo de respuesta.
* Integración de IA preparada y desactivada.

---

## 15. Principios utilizados durante el trabajo con IA

Las interacciones con IA se utilizaron principalmente como apoyo al desarrollo y a la revisión, siguiendo estos principios:

* No inventar datos que no estén respaldados por los CSV.
* Diferenciar entre cero y dato desconocido.
* Mantener el histórico coherente.
* Documentar las anomalías en lugar de ocultarlas.
* Utilizar reglas sencillas y defendibles.
* Evitar sobreingeniería.
* Priorizar las preguntas de negocio del enunciado.
* Explicar las limitaciones cuando los datos no permiten responder completamente.
* Utilizar la IA para analizar, programar, revisar y detectar posibles problemas.
* Mantener explícitas las decisiones de negocio y sus supuestos.

El objetivo no fue delegar completamente el proyecto en la IA, sino utilizarla como herramienta de apoyo para acelerar el análisis, detectar problemas y revisar la solución final.
