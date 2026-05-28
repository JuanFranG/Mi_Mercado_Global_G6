import boto3

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

try:
    respuesta = dynamodb.create_table(
        TableName='MiMercadoGlobal',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'},
            {'AttributeName': 'Estado', 'AttributeType': 'S'},
            {'AttributeName': 'Fecha_Creacion', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'GSI_1',
                'KeySchema': [
                    {'AttributeName': 'Estado', 'KeyType': 'HASH'},
                    {'AttributeName': 'Fecha_Creacion', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName='MiMercadoGlobal')

    dynamodb.update_time_to_live(
        TableName='MiMercadoGlobal',
        TimeToLiveSpecification={
            'Enabled': True,
            'AttributeName': 'expira_en'
        }
    )
    print("Tabla local creada.")

except Exception as e:
    print(e)