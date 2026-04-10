# Modelado de Datos - Mi Mercado Global
## Single Table Design para DynamoDB

---

## Paso 1: Identificar Patrones de Acceso (Access Patterns)

El diseno de la tabla parte de las preguntas que el sistema debe responder, no de la estructura de los datos. Cada patron de acceso define como se van a leer o escribir los datos.

| # | Patron de Acceso | Descripcion |
|---|-----------------|-------------|
| AP-01 | Ver perfil de un usuario | Obtener nombre, correo, direcciones y metodos de pago de Luisa |
| AP-02 | Listar pedidos recientes de un usuario | Mostrar estado, fecha de creacion y direccion de envio, ordenados por fecha descendente |
| AP-03 | Ver informacion general de un pedido especifico | Obtener cabecera del pedido: estado, fecha, total, direccion de envio |
| AP-04 | Ver items que componen un pedido | Listar productos, cantidad, precio unitario y subtotal de un pedido dado su ID |
| AP-05 | Ver todos los pedidos por estado | Listar todos los pedidos en estado "Enviado" o "Pago exitoso", ordenados por fecha |
| AP-06 | Ver estado del pago de un pedido | Consultar si el pago fue exitoso, pendiente o fallido |

---

## Paso 2: Modelar PK y SK para Responder los Patrones de Acceso

### Logica de las claves

Se usa Key Overloading: la misma tabla almacena diferentes tipos de entidades (usuarios, pedidos, items) distinguiendolas por el valor del SK.

| PK | SK | Entidad | Patron que responde |
|----|----|---------|-------------------|
| USER#<EMAIL> | PERFIL | Perfil del usuario | AP-01 |
| USER#<EMAIL> | ORD#<FECHA>#<ID> | Resumen de pedido del usuario | AP-02 |
| ORD#<ID_PEDIDO> | INFO | Informacion general del pedido | AP-03, AP-06 |
| ORD#<ID_PEDIDO> | ITEM#<PRODUCTO> | Item dentro del pedido | AP-04 |

### Tabla unica resultante

| PK | SK | ATRIBUTOS |
|----|----|-----------|
| USER#luisa@x.com | PERFIL | Nombre, Email, Direcciones, Metodos_Pago |
| USER#luisa@x.com | ORD#20231115T1430Z#556 | Estado, Fecha_Creacion, Dir_Envio, Total |
| USER#luisa@x.com | ORD#20231027T0800Z#555 | Estado, Fecha_Creacion, Dir_Envio, Total |
| USER#luisa@x.com | ORD#20231010T1145Z#554 | Estado, Fecha_Creacion, Dir_Envio, Total |
| ORD#555 | INFO | Fecha, Estado, Dir_Envio, Total, Estado_Pago, expira_en |
| ORD#555 | ITEM#LAPTOP_XPS | Producto, Cantidad, Precio_Unitario_Compra, Subtotal |
| ORD#555 | ITEM#LIBRO_EL_CAPITAL | Producto, Cantidad, Precio_Unitario_Compra, Subtotal |

### Por que el pedido aparece dos veces

El item `USER#luisa@x.com + ORD#<FECHA>#555` existe para listar los pedidos de Luisa ordenados por fecha (AP-02), aprovechando que DynamoDB ordena el SK lexicograficamente.

El item `ORD#555 + INFO` existe para acceder directamente al detalle del pedido con solo su ID (AP-03), sin necesidad de saber a que usuario pertenece.

Esta duplicidad intencional es una practica estandar en Single Table Design.

### TTL: campo expira_en

El campo `expira_en` se agrega unicamente a los items de tipo `ORD#<ID> + METADATA` cuyo `Estado` sea `Cancelado`.

- Tipo: Number (timestamp Unix en segundos)
- Valor: fecha de cancelacion + 90 dias
- Ejemplo: si el pedido se cancelo el 2023-11-15, expira_en = 1702684800 + 7776000

DynamoDB elimina automaticamente estos items cuando el timestamp vence, sin costo de escritura adicional.

No se aplica TTL a:
- Perfiles de usuario (no deben expirar)
- Pedidos con estado Enviado o Pago exitoso (pueden requerirse para auditoria)
- Items ITEM# dentro de un pedido (se eliminan en cascada al borrar la cabecera si se maneja desde la aplicacion)

---

## Paso 3: Definir Indices Secundarios (GSI)

Los GSI permiten responder patrones de acceso que no siguen la PK principal de la tabla.

### GSI_1 - Buscar pedidos por estado

Responde al patron AP-05: "Ver todos los pedidos en un estado determinado, ordenados por fecha".

| Configuracion | Valor |
|--------------|-------|
| Nombre | GSI_1 |
| GSI PK | Estado (String) |
| GSI SK | Fecha_Creacion (String, formato ISO 8601) |
| Proyeccion | ALL |
| Aplica a | Items con SK = INFO dentro de ORD# |

Visualizacion del GSI_1:

| GSI PK (Estado) | GSI SK (Fecha_Creacion) | Atributos Proyectados |
|-----------------|------------------------|----------------------|
| Pago exitoso | 2023-11-15T14:30Z | PK: USER#luisa@x.com, SK: ORD#..#556, Total: 1250 |
| Pago exitoso | 2023-10-27T08:00Z | PK: ORD#555, SK: INFO, Total: 1250 |
| Enviado | 2023-11-01T09:15Z | PK: USER#luisa@x.com, SK: ORD#..#557, Total: 50 |
| Enviado | 2023-10-10T11:45Z | PK: USER#luisa@x.com, SK: ORD#..#554, Total: 100 |
| Cancelado | 2023-09-01T10:00Z | PK: ORD#540, SK: METADATA, Total: 75, expira_en: 1700000000 |

Con este GSI la consulta es:

```
GSI_1 donde Estado = "Enviado" → devuelve todos los pedidos enviados ordenados por fecha
```

### Resumen de indices

| Indice | PK | SK | Patron que resuelve |
|--------|----|----|-------------------|
| Tabla base | USER# / ORD# | METADATA / ORD# / ITEM# | AP-01, AP-02, AP-03, AP-04, AP-06 |
| GSI_1 | Estado | Fecha_Creacion | AP-05 |

---

## Consideraciones adicionales

**Sobre TTL y pedidos cancelados**

Los pedidos cancelados consumen espacio de almacenamiento sin aportar valor operativo pasado cierto tiempo. Al activar TTL sobre el campo `expira_en`, DynamoDB los elimina automaticamente. Esto reduce costos y mantiene la tabla limpia sin operaciones de borrado manuales desde la aplicacion.

**Sobre la proyeccion del GSI**

Se uso `ProjectionType: ALL` para simplicidad academica. En produccion se recomienda proyectar solo los atributos necesarios para reducir el costo por lectura del indice.

**Sobre patrones no cubiertos actualmente**

Si en el futuro se necesita buscar en que pedidos aparecio un producto especifico (ej: "todos los pedidos que contienen Laptop XPS"), se requerira un GSI adicional con `Producto` como PK. Este patron no esta en los requisitos actuales pero es comun en e-commerce.
