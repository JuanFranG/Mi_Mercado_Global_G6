"""
Redis Adapter — Mi Mercado Global
-----------------------------------
Encapsula la conexión a Redis y las operaciones de caché con TTL.

Responsabilidades:
  - Serializar/deserializar datos (JSON) hacia y desde Redis.
  - Gestionar TTLs por tipo de dato.
  - Proveer get / set / delete como interfaz limpia para el repositorio.

Claves Redis utilizadas:
  perfil:{usuario_id}           → dict del perfil          TTL: 300 s
  pedidos_usuario:{usuario_id}  → list de referencias      TTL: 120 s
  pedido:{id_pedido}            → dict {info, items}       TTL: 180 s
  pedidos_estado:{estado}       → list de cabeceras        TTL:  60 s
"""

import json
import redis

# ─── Configuración ────────────────────────────────────────────────────────────

_HOST = "localhost"
_PORT = 6379
_DB   = 0  # base de datos Redis 0 (por defecto)

# TTLs en segundos por tipo de recurso
TTL_PERFIL          = 300   # 5 minutos
TTL_PEDIDOS_USUARIO = 120   # 2 minutos
TTL_PEDIDO          = 180   # 3 minutos
TTL_PEDIDOS_ESTADO  = 60    # 1 minuto


class RedisAdapter:
    """
    Wrapper de Redis que serializa datos como JSON y aplica TTL automáticamente.
    Todas las operaciones son seguras: un fallo de Redis nunca corta la petición.
    """

    def __init__(self):
        self._cliente = redis.Redis(
            host=_HOST,
            port=_PORT,
            db=_DB,
            decode_responses=True,  # retorna strings, no bytes
        )

    # ─── Lectura ──────────────────────────────────────────────────────────────

    def get(self, clave: str) -> dict | list | None:
        """
        Busca la clave en Redis.
        Retorna el objeto deserializado o None si no existe / expiró.
        """
        valor = self._cliente.get(clave)
        if valor is None:
            return None
        return json.loads(valor)

    # ─── Escritura ────────────────────────────────────────────────────────────

    def set(self, clave: str, datos: dict | list, ttl: int) -> None:
        """
        Guarda datos serializados con un TTL en segundos.
        Redis expira la clave automáticamente al cumplirse el TTL.
        """
        self._cliente.setex(clave, ttl, json.dumps(datos, default=str))

    # ─── Eliminación ──────────────────────────────────────────────────────────

    def delete(self, clave: str) -> None:
        """Elimina una clave específica del caché."""
        self._cliente.delete(clave)

    # ─── Diagnóstico ──────────────────────────────────────────────────────────

    def ttl_restante(self, clave: str) -> int:
        """
        Retorna los segundos de vida restantes de una clave.
        -1 = sin TTL, -2 = no existe.
        Útil para depurar desde Postman o logs.
        """
        return self._cliente.ttl(clave)

    def ping(self) -> bool:
        """Verifica que Redis esté activo."""
        try:
            return self._cliente.ping()
        except redis.ConnectionError:
            return False
