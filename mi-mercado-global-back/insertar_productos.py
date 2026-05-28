"""
Script de seed para productos del catálogo.
Inserta 13 productos en 4 categorías usando GSI_2 (Categoria + Nombre).

Correr con:
  DYNAMODB_ENDPOINT=http://localhost:4566 python insertar_productos.py
"""

import os
from decimal import Decimal

import boto3

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000"),
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

tabla = dynamodb.Table("MiMercadoGlobal")

productos = [
    # ── Electrónica ──────────────────────────────────────────────────────────
    {
        "PK": "PROD#001", "SK": "INFO",
        "Nombre": "Teléfono Inteligente X100",
        "Precio": Decimal("850000"),
        "Stock": Decimal("15"),
        "Categoria": "Electronica",
        "Descripcion": "Smartphone 6.7'' AMOLED, 256 GB, cámara 108 MP",
    },
    {
        "PK": "PROD#002", "SK": "INFO",
        "Nombre": "Portátil WorkPro 15",
        "Precio": Decimal("2200000"),
        "Stock": Decimal("8"),
        "Categoria": "Electronica",
        "Descripcion": "Intel Core i7, 16 GB RAM, SSD 512 GB, pantalla FHD",
    },
    {
        "PK": "PROD#003", "SK": "INFO",
        "Nombre": "Auriculares Bluetooth Z5",
        "Precio": Decimal("120000"),
        "Stock": Decimal("25"),
        "Categoria": "Electronica",
        "Descripcion": "Cancelación de ruido activa, 30 h de batería",
    },
    {
        "PK": "PROD#004", "SK": "INFO",
        "Nombre": "Reloj Inteligente FitTrack",
        "Precio": Decimal("350000"),
        "Stock": Decimal("3"),
        "Categoria": "Electronica",
        "Descripcion": "GPS integrado, monitor cardíaco, resistente al agua",
    },
    # ── Ropa ─────────────────────────────────────────────────────────────────
    {
        "PK": "PROD#005", "SK": "INFO",
        "Nombre": "Camiseta Algodón Hombre",
        "Precio": Decimal("45000"),
        "Stock": Decimal("100"),
        "Categoria": "Ropa",
        "Descripcion": "100% algodón peinado, corte regular, tallas S-XXL",
    },
    {
        "PK": "PROD#006", "SK": "INFO",
        "Nombre": "Jeans Slim Fit",
        "Precio": Decimal("89000"),
        "Stock": Decimal("40"),
        "Categoria": "Ropa",
        "Descripcion": "Denim elastizado, corte moderno, disponible en azul y negro",
    },
    {
        "PK": "PROD#007", "SK": "INFO",
        "Nombre": "Chaqueta Deportiva",
        "Precio": Decimal("135000"),
        "Stock": Decimal("20"),
        "Categoria": "Ropa",
        "Descripcion": "Impermeable liviana, capucha ajustable, bolsillos con cierre",
    },
    {
        "PK": "PROD#008", "SK": "INFO",
        "Nombre": "Vestido Floral Verano",
        "Precio": Decimal("75000"),
        "Stock": Decimal("35"),
        "Categoria": "Ropa",
        "Descripcion": "Tela suave tipo viscosa, estampado floral, largo midi",
    },
    # ── Hogar ────────────────────────────────────────────────────────────────
    {
        "PK": "PROD#009", "SK": "INFO",
        "Nombre": "Licuadora MultiPro",
        "Precio": Decimal("180000"),
        "Stock": Decimal("12"),
        "Categoria": "Hogar",
        "Descripcion": "700 W, 5 velocidades, vaso de vidrio 1.5 L, fácil limpieza",
    },
    {
        "PK": "PROD#010", "SK": "INFO",
        "Nombre": "Juego de Sábanas Queen",
        "Precio": Decimal("95000"),
        "Stock": Decimal("30"),
        "Categoria": "Hogar",
        "Descripcion": "Microfibra suave 1800 hilos, incluye sábana plana, ajustable y 2 fundas",
    },
    # ── Deportes ─────────────────────────────────────────────────────────────
    {
        "PK": "PROD#011", "SK": "INFO",
        "Nombre": "Mochila de Viaje 40L",
        "Precio": Decimal("90000"),
        "Stock": Decimal("50"),
        "Categoria": "Deportes",
        "Descripcion": "Nylon resistente, compartimentos organizados, porta laptop 15''",
    },
    {
        "PK": "PROD#012", "SK": "INFO",
        "Nombre": "Balón de Fútbol Pro",
        "Precio": Decimal("75000"),
        "Stock": Decimal("35"),
        "Categoria": "Deportes",
        "Descripcion": "Talla 5, cuero sintético termosellado, válvula butílica",
    },
    {
        "PK": "PROD#013", "SK": "INFO",
        "Nombre": "Pesas Hexagonales 5 kg",
        "Precio": Decimal("55000"),
        "Stock": Decimal("20"),
        "Categoria": "Deportes",
        "Descripcion": "Hierro fundido recubierto de goma, agarre antideslizante",
    },
]

try:
    with tabla.batch_writer() as batch:
        for producto in productos:
            batch.put_item(Item=producto)
    print(f"✓ {len(productos)} productos insertados correctamente.")
except Exception as e:
    print(f"✗ Error: {e}")
