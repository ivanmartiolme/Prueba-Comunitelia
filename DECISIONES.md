# DECISIONES

## Supuestos

- Fecha de referencia: **30/09/2026**.
- El MRR se calcula como una foto al cierre de cada mes, usando la última tarifa válida disponible hasta ese momento y nunca antes del inicio del contrato.
- Un contrato suspendido no aporta MRR mientras está suspendido.
- Para actividad técnica se utiliza un umbral de **90 días**.
- El análisis de coste/margen utiliza los últimos 12 meses y un coste interno de **22 €/hora**, tal como indica el enunciado.
- Una baja de contrato se cuenta en el mes de su `fecha_baja`, incluso si coincide con el último día del mes.
- La concentración se calcula sobre el MRR conocido de septiembre de 2026.

## Anomalías y tratamiento

- **S2018 duplicado:** se elimina el duplicado exacto para evitar contar dos veces el mismo contrato.
- **S2004:** figura como activo aunque tiene una fecha de baja anterior a la referencia. Se conserva el dato y las fechas prevalecen en los cálculos temporales.
- **S2019:** `fecha_baja` es anterior a `fecha_alta`. Se excluye de los cálculos temporales; no se inventa una fecha corregida.
- **Contratos anteriores al alta del cliente:** se detectan y documentan, pero no se modifican.
- **Tarifas anteriores al inicio del contrato:** no se utilizan antes de que exista el contrato.
- **S2061 sin tarifa:** no se inventa cuota y no se incluye en el MRR conocido.
- **Tarifas con importe vacío:** si existe un importe válido anterior, se conserva el último conocido; si no existe, el contrato queda fuera del MRR conocido.
- **Horas negativas:** no se convierten en positivas; se excluyen del coste técnico.
- **C9999 en partes de horas:** el cliente no existe en `clientes.csv`; su actividad se excluye del análisis por cliente.
- **CIF duplicado G93567312:** se mantiene porque no se puede determinar cuál registro es correcto.
- **Nombre de C1006 con espacios:** se eliminan espacios sobrantes al mostrar/tratar el nombre.
- **Clientes sin fecha de baja:** no se calcula baja de cliente porque el dato no existe.
- **Clientes sin actividad:** se separan entre sin actividad registrada y sin actividad durante más de 90 días.

## Preguntas para Comunitelia

1. ¿Qué debe considerarse exactamente como cliente activo cuando existen contratos suspendidos?
2. ¿Una baja con `fecha_baja` anterior a la fecha de referencia debe prevalecer sobre el campo `estado`?
3. ¿Cómo debe tratarse una tarifa vacía cuando no existe una tarifa histórica válida?
4. ¿El coste de 22 €/hora incluye únicamente coste técnico o representa un coste completo para calcular rentabilidad?
5. ¿Existe en el sistema real una fecha de baja de cliente que no esté incluida en este CSV?

## Fuera a propósito

- No se ha construido una recomendación automática del siguiente producto a vender: los datos permiten detectar clientes con un único servicio, pero no justifican qué producto concreto recomendar.
- No se ha incorporado una API de pago para el resumen LLM: el enunciado permite dejar la integración preparada y desactivada.
- No se ha añadido una capa de tecnología adicional innecesaria (base de datos, autenticación, despliegue, etc.) porque no aporta valor a las preguntas de negocio planteadas.
