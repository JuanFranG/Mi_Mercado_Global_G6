"""
DynamoDB Adapter — Mi Mercado Global
-------------------------------------
Flujo de datos:
  Docker/LocalStack (DynamoDB :4566)
      ↓  boto3.resource
  DynamoDBAdapter
      ↓
  Repository → FastAPI

Modelo de claves (Single-Table Design):
  PK                  SK                        Entidad
  USER#<uuid>         PERFIL                    Perfil de usuario
  USER#<uuid>         ORD#<fecha>#<num>         Referencia de pedido
  ORD#<num>           INFO                      Cabecera del pedido
  ORD#<num>           ITEM#<ref>                Línea de producto
  PROD#<id>           INFO                      Producto del catálogo

GSI_1: Estado (PK) + Fecha_Creacion (SK)  → pedidos por estado
GSI_2: Categoria (PK) + Nombre (SK)       → productos por categoría
"""

import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr, Key

_ENDPOINT   = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
_REGION     = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "MiMercadoGlobal")


def _limpiar_decimals(obj):
    """Convierte Decimal de DynamoDB a int/float para serialización JSON."""
    if isinstance(obj, list):
        return [_limpiar_decimals(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _limpiar_decimals(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


class DynamoDBAdapter:

    def __init__(self):
        recurso = boto3.resource(
            "dynamodb",
            endpoint_url=_ENDPOINT,
            region_name=_REGION,
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )
        self._tabla = recurso.Table(_TABLE_NAME)

    # ─── Usuarios ────────────────────────────────────────────────────────────

    def obtener_perfil(self, usuario_id: str) -> dict:
        respuesta = self._tabla.query(
            KeyConditionExpression=(
                Key("PK").eq(f"USER#{usuario_id}") & Key("SK").eq("PERFIL")
            )
        )
        items = respuesta["Items"]
        return _limpiar_decimals(items[0]) if items else {}

    def listar_pedidos_usuario(self, usuario_id: str) -> list:
        respuesta = self._tabla.query(
            KeyConditionExpression=(
                Key("PK").eq(f"USER#{usuario_id}") & Key("SK").begins_with("ORD#")
            ),
            ScanIndexForward=False,
        )
        return _limpiar_decimals(respuesta["Items"])

    def listar_todos_los_usuarios(self) -> list:
        """Scan para obtener todos los perfiles de usuario."""
        respuesta = self._tabla.scan(
            FilterExpression=Attr("SK").eq("PERFIL")
        )
        return _limpiar_decimals(respuesta.get("Items", []))

    # ─── Pedidos ─────────────────────────────────────────────────────────────

    def obtener_detalle_pedido(self, id_pedido: str) -> dict:
        respuesta = self._tabla.query(
            KeyConditionExpression=Key("PK").eq(f"ORD#{id_pedido}")
        )
        info, items = {}, []
        for item in respuesta["Items"]:
            if item["SK"] == "INFO":
                info = item
            elif item["SK"].startswith("ITEM#"):
                items.append(item)
        return _limpiar_decimals({"info": info, "items": items})

    def buscar_pedidos_por_estado(self, estado: str) -> list:
        respuesta = self._tabla.query(
            IndexName="GSI_1",
            KeyConditionExpression=Key("Estado").eq(estado),
            ScanIndexForward=False,
        )
        return _limpiar_decimals(respuesta["Items"])

    def actualizar_estado_pedido(self, id_pedido: str, nuevo_estado: str) -> bool:
        self._tabla.update_item(
            Key={"PK": f"ORD#{id_pedido}", "SK": "INFO"},
            UpdateExpression="SET #est = :val",
            ExpressionAttributeNames={"#est": "Estado"},
            ExpressionAttributeValues={":val": nuevo_estado},
        )
        return True

    # ─── Productos ───────────────────────────────────────────────────────────

    def listar_productos(self) -> list:
        """Scan de todos los productos (PK comienza con PROD# y SK = INFO)."""
        respuesta = self._tabla.scan(
            FilterExpression=Attr("SK").eq("INFO") & Attr("PK").begins_with("PROD#")
        )
        return _limpiar_decimals(respuesta.get("Items", []))

    def listar_productos_por_categoria(self, categoria: str) -> list:
        """Query en GSI_2: Categoria (PK) + Nombre (SK)."""
        respuesta = self._tabla.query(
            IndexName="GSI_2",
            KeyConditionExpression=Key("Categoria").eq(categoria),
        )
        return _limpiar_decimals(respuesta.get("Items", []))

    # ─── Escritura genérica ───────────────────────────────────────────────────

    def crear_o_actualizar_item(self, item: dict) -> bool:
        self._tabla.put_item(Item=item)
        return True

    def insertar_lote(self, items: list) -> int:
        with self._tabla.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return len(items)

    def eliminar_item(self, pk: str, sk: str) -> bool:
        self._tabla.delete_item(Key={"PK": pk, "SK": sk})
        return True
