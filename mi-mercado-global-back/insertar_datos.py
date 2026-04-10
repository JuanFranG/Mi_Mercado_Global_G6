import boto3

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1',
    aws_access_key_id='fake',
    aws_secret_access_key='fake'
)

tabla = dynamodb.Table('MiMercadoGlobal')

UUID_LUISA = "550e8400-e29b-41d4-a716-446655440000"

datos_a_insertar = [
    {
        'PK': f'USER#{UUID_LUISA}', 
        'SK': 'PERFIL', 
        'Nombre': 'Luisa', 
        'Email': 'l@x.com', 
        'Direcciones': ['Calle 10, Bogotá', 'Ave. 5, Medellín'], 
        'Metodos_Pago': ['Visa ...1234', 'PayPal']
    },
    {
        'PK': f'USER#{UUID_LUISA}', 
        'SK': 'ORD#20231115T1430Z#556', 
        'Estado': 'Pago exitoso', 
        'Fecha_Creacion': '2023-11-15T14:30Z', 
        'Dir_Envio': 'Calle 10', 
        'Total': 1250
    },
    {
        'PK': f'USER#{UUID_LUISA}', 
        'SK': 'ORD#20231027T0800Z#555', 
        'Estado': 'Pago exitoso', 
        'Fecha_Creacion': '2023-10-27T08:00Z', 
        'Dir_Envio': 'Calle 10', 
        'Total': 1250
    },
    {
        'PK': f'USER#{UUID_LUISA}', 
        'SK': 'ORD#20231010T1145Z#554', 
        'Estado': 'Enviado', 
        'Fecha_Creacion': '2023-10-10T11:45Z', 
        'Dir_Envio': 'Ave. 5', 
        'Total': 100
    },
    
    {
        'PK': 'ORD#555', 
        'SK': 'INFO', 
        'Fecha_Creacion': '2023-10-27T08:00Z', 
        'Estado': 'Pago exitoso', 
        'Dir_Envio': 'Calle 10, Bogotá', 
        'Total': 1250, 
        'Estado_Pago': 'Exitoso'
    },
    {
        'PK': 'ORD#555', 
        'SK': 'ITEM#LAPTOP_XPS', 
        'Producto': 'Laptop XPS', 
        'Cantidad': 1, 
        'Precio_Unitario_Compra': 1200, 
        'Subtotal': 1200
    },
    {
        'PK': 'ORD#555', 
        'SK': 'ITEM#LIBRO_EL_CAPITAL', 
        'Producto': 'Libro "El Capital"', 
        'Cantidad': 2, 
        'Precio_Unitario_Compra': 25, 
        'Subtotal': 50
    }
]

try:
    with tabla.batch_writer() as batch:
        for item in datos_a_insertar:
            batch.put_item(Item=item)
    print(f"Datos insertados. El UUID es: {UUID_LUISA}")
except Exception as e:
    print(e)