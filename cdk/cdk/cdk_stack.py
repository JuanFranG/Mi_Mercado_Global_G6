from aws_cdk import (
    Stack,
    BundlingOptions,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Duration,
    RemovalPolicy
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Crear la tabla de DynamoDB
        table = dynamodb.Table(
            self, "MiMercadoGlobalTable",
            table_name="MiMercadoGlobal",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY, # Para que se elimine al destruir el stack
            time_to_live_attribute="expira_en"
        )

        # GSI_1: buscar pedidos por estado
        table.add_global_secondary_index(
            index_name="GSI_1",
            partition_key=dynamodb.Attribute(name="Estado", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Fecha_Creacion", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # GSI_2: buscar productos por categoría
        table.add_global_secondary_index(
            index_name="GSI_2",
            partition_key=dynamodb.Attribute(name="Categoria", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Nombre", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Integrar la API, la Lambda y el Código
        backend_lambda = _lambda.Function(
            self, "MiMercadoGlobalBackendLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset(
                "../mi-mercado-global-back",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    platform="linux/amd64",
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"
                    ]
                )
            ),
            timeout=Duration.seconds(30),
            environment={
                "DYNAMODB_TABLE_NAME": table.table_name,
                "DYNAMODB_ENDPOINT": "http://host.docker.internal:4566",
                "REDIS_HOST": "host.docker.internal"
            }
        )

        # Dar permisos a la Lambda sobre la tabla
        table.grant_read_write_data(backend_lambda)

        # Crear la API que reciba las peticiones entrantes
        api = apigw.LambdaRestApi(
            self, "MiMercadoGlobalApi",
            handler=backend_lambda,
            proxy=True
        )
