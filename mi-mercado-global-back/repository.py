"""

Claves Redis:
  perfil:{usuario_id}           TTL 300 s
  pedidos_usuario:{usuario_id}  TTL 120 s
  pedido:{id_pedido}            TTL 180 s
  pedidos_estado:{estado}       TTL  60 s
"""

from dynamodb_adapter import DynamoDBAdapter
from redis_adapter import (
    RedisAdapter,
    TTL_PERFIL,
    TTL_PEDIDOS_USUARIO,
    TTL_PEDIDO,
    TTL_PEDIDOS_ESTADO,
)


class MercadoRepository:
    """
    Repositorio central que implementa Write-Through sobre Redis + DynamoDB.
    FastAPI solo conoce esta clase; nunca habla directamente con ningún adaptador.
    """

    def __init__(self):
        self._db    = DynamoDBAdapter()
        self._cache = RedisAdapter()

    # ─────────────────────────────────────────────────────────────────────────
    # LECTURAS  (estrategia: Cache-Aside = leer Redis primero, llenar en miss)
    # ─────────────────────────────────────────────────────────────────────────

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

    # ─────────────────────────────────────────────────────────────────────────
    # ESCRITURAS  (estrategia: Write-Through = escribir Redis Y DynamoDB)
    # ─────────────────────────────────────────────────────────────────────────

    def actualizar_estado_pedido(self, id_pedido: str, nuevo_estado: str) -> bool:
        """
        Implementación completa de Write-Through:

        Paso 1 — Obtener estado actual del pedido (puede venir de Redis o DynamoDB).
        Paso 2 — Persistir en DynamoDB (fuente de verdad permanente).
        Paso 3 — WRITE-THROUGH: actualizar la clave pedido:{id} en Redis
        Paso 4 — Invalidar las listas de estado afectadas:
  
        """
        clave_pedido = f"pedido:{id_pedido}"

        # ── Paso 1: leer estado anterior ─────────────────────────────────────
        detalle_actual = self.obtener_detalle_pedido(id_pedido)
        estado_anterior = (
            detalle_actual["info"].get("Estado") if detalle_actual.get("info") else None
        )

        # ── Paso 2: escribir en DynamoDB ─────────────────────────────────────
        self._db.actualizar_estado_pedido(id_pedido, nuevo_estado)

        # ── Paso 3: WRITE-THROUGH → actualizar Redis con el nuevo estado ─────
        if detalle_actual["info"]:
            detalle_actualizado = {
                "info": {**detalle_actual["info"], "Estado": nuevo_estado},
                "items": detalle_actual["items"],
            }
            self._cache.set(clave_pedido, detalle_actualizado, TTL_PEDIDO)

        # ── Paso 4: invalidar listas de estado (ya no reflejan la realidad) ──
        if estado_anterior and estado_anterior != nuevo_estado:
            self._cache.delete(f"pedidos_estado:{estado_anterior}")
        self._cache.delete(f"pedidos_estado:{nuevo_estado}")

        return True
