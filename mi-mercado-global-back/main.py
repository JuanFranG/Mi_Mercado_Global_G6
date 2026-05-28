from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from repository import MercadoRepository
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = MercadoRepository()


class ItemCarrito(BaseModel):
    producto_id: str
    nombre: str
    precio: float
    cantidad: int = 1


class PedidoCreate(BaseModel):
    usuario_id: str
    items: list[dict]
    dir_envio: str
    total: float


# ─── Usuarios ────────────────────────────────────────────────────────────────

@app.get("/api/usuarios")
def listar_usuarios():
    return repo.listar_todos_los_usuarios()


@app.get("/api/usuarios/{usuario_id}/perfil")
def obtener_perfil(usuario_id: str):
    perfil = repo.obtener_perfil(usuario_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return perfil


@app.get("/api/usuarios/{usuario_id}/pedidos")
def listar_pedidos(usuario_id: str):
    return repo.listar_pedidos_usuario(usuario_id)


# ─── Pedidos ─────────────────────────────────────────────────────────────────

@app.get("/api/pedidos/{id_pedido}")
def detalle_pedido(id_pedido: str):
    resultado = repo.obtener_detalle_pedido(id_pedido)
    if not resultado["info"]:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return resultado


@app.get("/api/pedidos")
def pedidos_por_estado(estado: str):
    return repo.buscar_pedidos_por_estado(estado)


@app.post("/api/pedidos")
def crear_pedido(pedido: PedidoCreate):
    return repo.crear_pedido(
        pedido.usuario_id, pedido.items, pedido.dir_envio, pedido.total
    )


@app.patch("/api/pedidos/{id_pedido}/estado")
def actualizar_estado(id_pedido: str, estado: str):
    repo.actualizar_estado_pedido(id_pedido, estado)
    return {"mensaje": f"Pedido {id_pedido} actualizado a '{estado}'"}


# ─── Productos ───────────────────────────────────────────────────────────────

@app.get("/api/productos")
def listar_productos(categoria: str = None):
    if categoria:
        return repo.listar_productos_por_categoria(categoria)
    return repo.listar_productos()


# ─── Carrito (Redis) ─────────────────────────────────────────────────────────

@app.get("/api/carrito/{usuario_id}")
def obtener_carrito(usuario_id: str):
    return repo.obtener_carrito(usuario_id)


@app.post("/api/carrito/{usuario_id}/items")
def agregar_al_carrito(usuario_id: str, item: ItemCarrito):
    return repo.agregar_al_carrito(usuario_id, item.model_dump())


@app.delete("/api/carrito/{usuario_id}/items/{producto_id}")
def eliminar_del_carrito(usuario_id: str, producto_id: str):
    return repo.eliminar_del_carrito(usuario_id, producto_id)


@app.delete("/api/carrito/{usuario_id}")
def limpiar_carrito(usuario_id: str):
    return repo.limpiar_carrito(usuario_id)


# ─── Diagnóstico Redis ────────────────────────────────────────────────────────

@app.get("/api/cache/ping")
def cache_ping():
    return {"redis_activo": repo._cache.ping()}


@app.get("/api/cache/ttl/{clave}")
def cache_ttl(clave: str):
    return {"clave": clave, "ttl_segundos": repo._cache.ttl_restante(clave)}


@app.delete("/api/cache/{clave}")
def cache_delete(clave: str):
    repo._cache.delete(clave)
    return {"mensaje": f"Clave '{clave}' eliminada del caché"}
