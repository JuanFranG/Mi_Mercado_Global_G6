"""
Redis Adapter — Mi Mercado Global
-----------------------------------
Claves Redis utilizadas:
  perfil:{usuario_id}           → dict del perfil          TTL: 300 s
  pedidos_usuario:{usuario_id}  → list de referencias      TTL: 120 s
  pedido:{id_pedido}            → dict {info, items}       TTL: 180 s
  pedidos_estado:{estado}       → list de cabeceras        TTL:  60 s
  productos:todos               → list de productos        TTL: 120 s
  productos:categoria:{cat}     → list de productos        TTL: 120 s
  usuarios:todos                → list de perfiles         TTL: 300 s
  carrito:{usuario_id}          → list de items            TTL: 3600 s
"""

import json
import os

import redis

_HOST = os.environ.get("REDIS_HOST", "localhost")
_PORT = int(os.environ.get("REDIS_PORT", "6379"))
_DB   = 0

# TTLs por tipo de recurso (segundos)
TTL_PERFIL          = 300
TTL_PEDIDOS_USUARIO = 120
TTL_PEDIDO          = 180
TTL_PEDIDOS_ESTADO  = 60
TTL_PRODUCTOS       = 120
TTL_USUARIOS        = 300
TTL_CARRITO         = 3600


class RedisAdapter:
    """
    Wrapper de Redis con serialización JSON y TTL automático.
    Un fallo de Redis en ping() no corta la petición.
    """

    def __init__(self):
        self._cliente = redis.Redis(
            host=_HOST,
            port=_PORT,
            db=_DB,
            decode_responses=True,
        )

    def get(self, clave: str):
        valor = self._cliente.get(clave)
        if valor is None:
            return None
        return json.loads(valor)

    def set(self, clave: str, datos, ttl: int) -> None:
        self._cliente.setex(clave, ttl, json.dumps(datos, default=str))

    def delete(self, clave: str) -> None:
        self._cliente.delete(clave)

    def ttl_restante(self, clave: str) -> int:
        return self._cliente.ttl(clave)

    def ping(self) -> bool:
        try:
            return self._cliente.ping()
        except redis.ConnectionError:
            return False
