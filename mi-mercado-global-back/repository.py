"""
Repositorio central — Mi Mercado Global

Claves Redis:
  perfil:{usuario_id}           TTL 300 s
  pedidos_usuario:{usuario_id}  TTL 120 s
  pedido:{id_pedido}            TTL 180 s
  pedidos_estado:{estado}       TTL  60 s
  productos:todos               TTL 120 s
  productos:categoria:{cat}     TTL 120 s
  usuarios:todos                TTL 300 s
  carrito:{usuario_id}          TTL 3600 s
"""

from dynamodb_adapter import DynamoDBAdapter
from redis_adapter import (
    RedisAdapter,
    TTL_PERFIL,
    TTL_PEDIDOS_USUARIO,
    TTL_PEDIDO,
    TTL_PEDIDOS_ESTADO,
    TTL_PRODUCTOS,
    TTL_USUARIOS,
    TTL_CARRITO,
)


class MercadoRepository:

    def __init__(self):
        self._db    = DynamoDBAdapter()
        self._cache = RedisAdapter()

    # ─── Usuarios ────────────────────────────────────────────────────────────
    # Estrategia: Cache-Aside

    def obtener_perfil(self, usuario_id: str) -> dict:
        clave = f"perfil:{usuario_id}"
        cached = self._cache.get(clave)
        if cached is not None:
            return {**cached, "fuente": "cache"}
        perfil = self._db.obtener_perfil(usuario_id)
        if perfil:
            self._cache.set(clave, perfil, TTL_PERFIL)
        return {**perfil, "fuente": "dynamodb"} if perfil else {}

    def listar_pedidos_usuario(self, usuario_id: str) -> dict:
        clave = f"pedidos_usuario:{usuario_id}"
        cached = self._cache.get(clave)
        if cached is not None:
            return {"pedidos": cached, "fuente": "cache"}
        pedidos = self._db.listar_pedidos_usuario(usuario_id)
        self._cache.set(clave, pedidos, TTL_PEDIDOS_USUARIO)
        return {"pedidos": pedidos, "fuente": "dynamodb"}

    def listar_todos_los_usuarios(self) -> dict:
        clave = "usuarios:todos"
        cached = self._cache.get(clave)
        if cached is not None:
            return {"usuarios": cached, "fuente": "cache"}
        usuarios = self._db.listar_todos_los_usuarios()
        self._cache.set(clave, usuarios, TTL_USUARIOS)
        return {"usuarios": usuarios, "fuente": "dynamodb"}

    # ─── Pedidos ─────────────────────────────────────────────────────────────

    def obtener_detalle_pedido(self, id_pedido: str) -> dict:
        clave = f"pedido:{id_pedido}"
        cached = self._cache.get(clave)
        if cached is not None:
            return {**cached, "fuente": "cache"}
        detalle = self._db.obtener_detalle_pedido(id_pedido)
        if detalle["info"]:
            self._cache.set(clave, detalle, TTL_PEDIDO)
        return {**detalle, "fuente": "dynamodb"}

    def buscar_pedidos_por_estado(self, estado: str) -> dict:
        clave = f"pedidos_estado:{estado}"
        cached = self._cache.get(clave)
        if cached is not None:
            return {"pedidos": cached, "fuente": "cache"}
        pedidos = self._db.buscar_pedidos_por_estado(estado)
        self._cache.set(clave, pedidos, TTL_PEDIDOS_ESTADO)
        return {"pedidos": pedidos, "fuente": "dynamodb"}

    def actualizar_estado_pedido(self, id_pedido: str, nuevo_estado: str) -> bool:
        """Write-Through: DynamoDB → Redis, invalida listas afectadas."""
        clave_pedido = f"pedido:{id_pedido}"
        detalle_actual = self.obtener_detalle_pedido(id_pedido)
        estado_anterior = (
            detalle_actual["info"].get("Estado") if detalle_actual.get("info") else None
        )
        self._db.actualizar_estado_pedido(id_pedido, nuevo_estado)
        if detalle_actual["info"]:
            detalle_actualizado = {
                "info": {**detalle_actual["info"], "Estado": nuevo_estado},
                "items": detalle_actual["items"],
            }
            self._cache.set(clave_pedido, detalle_actualizado, TTL_PEDIDO)
        if estado_anterior and estado_anterior != nuevo_estado:
            self._cache.delete(f"pedidos_estado:{estado_anterior}")
        self._cache.delete(f"pedidos_estado:{nuevo_estado}")
        return True

    # ─── Productos ───────────────────────────────────────────────────────────
    # Estrategia: Cache-Aside

    def listar_productos(self) -> dict:
        clave = "productos:todos"
        cached = self._cache.get(clave)
        if cached is not None:
            return {"productos": cached, "fuente": "cache"}
        productos = self._db.listar_productos()
        self._cache.set(clave, productos, TTL_PRODUCTOS)
        return {"productos": productos, "fuente": "dynamodb"}

    def listar_productos_por_categoria(self, categoria: str) -> dict:
        clave = f"productos:categoria:{categoria}"
        cached = self._cache.get(clave)
        if cached is not None:
            return {"productos": cached, "fuente": "cache"}
        productos = self._db.listar_productos_por_categoria(categoria)
        self._cache.set(clave, productos, TTL_PRODUCTOS)
        return {"productos": productos, "fuente": "dynamodb"}

    # ─── Carrito (solo Redis) ─────────────────────────────────────────────────
    # El carrito es efímero: vive en Redis, no se persiste en DynamoDB.

    def obtener_carrito(self, usuario_id: str) -> dict:
        items = self._cache.get(f"carrito:{usuario_id}") or []
        return {"items": items}

    def agregar_al_carrito(self, usuario_id: str, item: dict) -> dict:
        clave = f"carrito:{usuario_id}"
        items = self._cache.get(clave) or []
        for i, existente in enumerate(items):
            if existente["producto_id"] == item["producto_id"]:
                items[i]["cantidad"] += item.get("cantidad", 1)
                self._cache.set(clave, items, TTL_CARRITO)
                return {"items": items}
        items.append(item)
        self._cache.set(clave, items, TTL_CARRITO)
        return {"items": items}

    def eliminar_del_carrito(self, usuario_id: str, producto_id: str) -> dict:
        clave = f"carrito:{usuario_id}"
        items = self._cache.get(clave) or []
        items = [i for i in items if i["producto_id"] != producto_id]
        self._cache.set(clave, items, TTL_CARRITO)
        return {"items": items}

    def limpiar_carrito(self, usuario_id: str) -> dict:
        self._cache.delete(f"carrito:{usuario_id}")
        return {"items": []}

    def crear_pedido(self, usuario_id: str, items: list, dir_envio: str, total: float) -> dict:
        """
        Crea un pedido completo en DynamoDB:
          - ORD#<id> / INFO         → cabecera
          - ORD#<id> / ITEM#<ref>   → línea por producto
          - USER#<id> / ORD#<fecha>#<id> → referencia en el usuario
        Luego limpia el carrito de Redis e invalida caché de pedidos del usuario.
        """
        import random, datetime

        id_pedido = str(10000 + random.randint(0, 89999))
        fecha     = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")
        fecha_sk  = datetime.datetime.utcnow().strftime("%Y%m%dT%H%MZ")

        datos = [
            {
                "PK": f"ORD#{id_pedido}", "SK": "INFO",
                "Fecha_Creacion": fecha,
                "Estado": "Pago exitoso",
                "Dir_Envio": dir_envio,
                "Total": int(total),
                "Estado_Pago": "Exitoso",
            }
        ]
        for item in items:
            datos.append({
                "PK": f"ORD#{id_pedido}",
                "SK": f"ITEM#{item['producto_id'].replace('PROD#', '')}",
                "Producto": item["nombre"],
                "Cantidad": item["cantidad"],
                "Precio_Unitario_Compra": int(item["precio"]),
                "Subtotal": int(item["precio"] * item["cantidad"]),
            })
        datos.append({
            "PK": f"USER#{usuario_id}",
            "SK": f"ORD#{fecha_sk}#{id_pedido}",
            "Estado": "Pago exitoso",
            "Fecha_Creacion": fecha,
            "Dir_Envio": dir_envio,
            "Total": int(total),
        })

        self._db.insertar_lote(datos)
        self.limpiar_carrito(usuario_id)
        self._cache.delete(f"pedidos_usuario:{usuario_id}")

        return {"id_pedido": id_pedido, "estado": "Pago exitoso", "total": int(total)}
