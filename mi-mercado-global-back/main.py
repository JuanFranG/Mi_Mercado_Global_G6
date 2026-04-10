from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dynamodb_adapter import DynamoDBAdapter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DynamoDBAdapter()


@app.get("/api/usuarios/{usuario_id}/perfil")
def obtener_perfil(usuario_id: str):
    perfil = db.obtener_perfil(usuario_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return perfil


@app.get("/api/usuarios/{usuario_id}/pedidos")
def listar_pedidos(usuario_id: str):
    return db.listar_pedidos_usuario(usuario_id)


@app.get("/api/pedidos/{id_pedido}")
def detalle_pedido(id_pedido: str):
    resultado = db.obtener_detalle_pedido(id_pedido)
    if not resultado["info"]:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return resultado


@app.get("/api/pedidos")
def pedidos_por_estado(estado: str):
    """Usa GSI_1 para filtrar pedidos por estado. Ej: ?estado=Enviado"""
    return db.buscar_pedidos_por_estado(estado)


@app.patch("/api/pedidos/{id_pedido}/estado")
def actualizar_estado(id_pedido: str, estado: str):
    """Actualiza solo el campo Estado de un pedido. Ej: ?estado=Entregado"""
    db.actualizar_estado_pedido(id_pedido, estado)
    return {"mensaje": f"Pedido {id_pedido} actualizado a '{estado}'"}
