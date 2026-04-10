import boto3

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1',
    aws_access_key_id='fake',
    aws_secret_access_key='fake'
)

tabla = dynamodb.Table('MiMercadoGlobal')

UUID_CARLOS = "a1b2c3d4-e5f6-7890-1234-56789abcdef0"

datos_nuevos = [
    {
        
        'PK': f'USER#{UUID_CARLOS}', 
        'SK': 'PERFIL', 
        'Nombre': 'Carlos Alberto', 
        'Email': 'carlos@x.com', 
        'Direcciones': ['Cra 45 # 12-34, Cali', 'Oficina 402, Edificio Central, Bogotá'], 
        'Metodos_Pago': ['Mastercard ...5678']
    },
    {
        
        'PK': f'USER#{UUID_CARLOS}', 
        'SK': 'ORD#20240320T1000Z#901', 
        'Estado': 'Enviado', 
        'Fecha_Creacion': '2024-03-20T10:00Z', 
        'Dir_Envio': 'Cra 45 # 12-34, Cali', 
        'Total': 450
    },
    {
        
        'PK': f'USER#{UUID_CARLOS}', 
        'SK': 'ORD#20240325T1530Z#902', 
        'Estado': 'Pago exitoso', 
        'Fecha_Creacion': '2024-03-25T15:30Z', 
        'Dir_Envio': 'Oficina 402, Edificio Central, Bogotá', 
        'Total': 85
    },
    
    {
        'PK': 'ORD#901', 
        'SK': 'INFO', 
        'Fecha_Creacion': '2024-03-20T10:00Z', 
        'Estado': 'Enviado', 
        'Dir_Envio': 'Cra 45 # 12-34, Cali', 
        'Total': 450, 
        'Estado_Pago': 'Exitoso'
    },
    {
        'PK': 'ORD#901', 
        'SK': 'ITEM#MONITOR_LG', 
        'Producto': 'Monitor LG 24"', 
        'Cantidad': 1, 
        'Precio_Unitario_Compra': 350, 
        'Subtotal': 350
    },
    {
        'PK': 'ORD#901', 
        'SK': 'ITEM#TECLADO_MEC', 
        'Producto': 'Teclado Mecánico', 
        'Cantidad': 1, 
        'Precio_Unitario_Compra': 100, 
        'Subtotal': 100
    },
    {
        'PK': 'ORD#902', 
        'SK': 'INFO', 
        'Fecha_Creacion': '2024-03-25T15:30Z', 
        'Estado': 'Pago exitoso', 
        'Dir_Envio': 'Oficina 402, Edificio Central, Bogotá', 
        'Total': 85, 
        'Estado_Pago': 'Exitoso'
    },
    {
        'PK': 'ORD#902', 
        'SK': 'ITEM#MOUSE_LOGI', 
        'Producto': 'Mouse Inalámbrico', 
        'Cantidad': 1, 
        'Precio_Unitario_Compra': 85, 
        'Subtotal': 85
    }
]

try:
    with tabla.batch_writer() as batch:
        for item in datos_nuevos:
            batch.put_item(Item=item)
    print(f"Datos de Carlos insertados correctamente la UUID es: {UUID_CARLOS}")
except Exception as e:
    print(e)