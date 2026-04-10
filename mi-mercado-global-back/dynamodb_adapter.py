"""
DynamoDB Adapter — Mi Mercado Global
-------------------------------------
Centraliza toda interacción con DynamoDB Local (Docker).

Flujo de datos:
  Docker (DynamoDB Local :8000)
      ↓  boto3.resource (endpoint_url)
  DynamoDBAdapter  ←  genera KeyConditionExpression / PutItem / etc.
      ↓
  FastAPI (main.py)  →  responde JSON al frontend

Modelo de claves (Single-Table Design):
  PK                  SK                        Entidad
  USER#<uuid>         PERFIL                    Perfil de usuario
  USER#<uuid>         ORD#<fecha>#<num>         Referencia de pedido en usuario
  ORD#<num>           INFO                      Cabecera del pedido
  ORD#<num>           ITEM#<ref>                Línea de producto

GSI_1: Estado (PK) + Fecha_Creacion (SK)  →  buscar pedidos por estado
"""

import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional


# ─── Configuración de conexión ───────────────────────────────────────────────

_ENDPOINT   = "http://localhost:8000"
_REGION     = "us-east-1"
_ACCESS_KEY = "test"
_SECRET_KEY = "test"
_TABLE_NAME = "MiMercadoGlobal"


class DynamoDBAdapter:
    """
    Adaptador que encapsula todas las queries DynamoDB del e-commerce.
    Genera las expresiones de condición y devuelve dicts limpios.
    """

    def __init__(self):
        recurso = boto3.resource(
            "dynamodb",
            endpoint_url=_ENDPOINT,
            region_name=_REGION,
            aws_access_key_id=_ACCESS_KEY,
            aws_secret_access_key=_SECRET_KEY,
        )
        self._tabla = recurso.Table(_TABLE_NAME)

    # ─── Usuarios ────────────────────────────────────────────────────────────

    def obtener_perfil(self, usuario_id: str) -> dict:
        """
        Query: PK = USER#<id>  AND  SK = PERFIL
        Retorna el perfil del usuario o {} si no existe.
        """
        respuesta = self._tabla.query(
            KeyConditionExpression=(
                Key("PK").eq(f"USER#{usuario_id}") & Key("SK").eq("PERFIL")
            )
        )
        items = respuesta["Items"]
        return items[0] if items else {}

    def listar_pedidos_usuario(self, usuario_id: str) -> list:
        """
        Query: PK = USER#<id>  AND  SK begins_with 'ORD#'
        Retorna referencias de pedidos ordenadas por fecha desc (ScanIndexForward=False).
        """
        respuesta = self._tabla.query(
            KeyConditionExpression=(
                Key("PK").eq(f"USER#{usuario_id}") & Key("SK").begins_with("ORD#")
            ),
            ScanIndexForward=False,
        )
        return respuesta["Items"]

    # ─── Pedidos ─────────────────────────────────────────────────────────────

    def obtener_detalle_pedido(self, id_pedido: str) -> dict:
        """
        Query: PK = ORD#<id>  (todas las SK: INFO + ITEM#*)
        Retorna {"info": {...}, "items": [...]}
        """
        respuesta = self._tabla.query(
            KeyConditionExpression=Key("PK").eq(f"ORD#{id_pedido}")
        )
        info = {}
        items = []
        for item in respuesta["Items"]:
            if item["SK"] == "INFO":
                info = item
            elif item["SK"].startswith("ITEM#"):
                items.append(item)
        return {"info": info, "items": items}

    def buscar_pedidos_por_estado(self, estado: str) -> list:
        """
        Query sobre GSI_1: Estado (PK) + Fecha_Creacion (SK)
        Útil para administración: ver todos los pedidos 'Enviado', etc.
        """
        respuesta = self._tabla.query(
            IndexName="GSI_1",
            KeyConditionExpression=Key("Estado").eq(estado),
            ScanIndexForward=False,
        )
        return respuesta["Items"]

    # ─── Escritura ───────────────────────────────────────────────────────────

    def crear_o_actualizar_item(self, item: dict) -> bool:
        """
        PutItem genérico. Requiere que el dict traiga PK y SK.
        Retorna True si fue exitoso.
        """
        self._tabla.put_item(Item=item)
        return True

    def insertar_lote(self, items: list[dict]) -> int:
        """
        BatchWriter para insertar múltiples ítems de golpe.
        Retorna la cantidad de ítems procesados.
        """
        with self._tabla.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return len(items)

    def eliminar_item(self, pk: str, sk: str) -> bool:
        """
        DeleteItem por clave primaria (PK + SK).
        """
        self._tabla.delete_item(Key={"PK": pk, "SK": sk})
        return True

    def actualizar_estado_pedido(self, id_pedido: str, nuevo_estado: str) -> bool:
        """
        UpdateItem: cambia Estado en ORD#<id> / INFO sin reescribir todo el item.
        """
        self._tabla.update_item(
            Key={"PK": f"ORD#{id_pedido}", "SK": "INFO"},
            UpdateExpression="SET #est = :val",
            ExpressionAttributeNames={"#est": "Estado"},
            ExpressionAttributeValues={":val": nuevo_estado},
        )
        return True
