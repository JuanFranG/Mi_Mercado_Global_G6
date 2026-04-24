from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from repository import MercadoRepository

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = MercadoRepository()


@app.get("/api/usuarios/{usuario_id}/perfil")
def obtener_perfil(usuario_id: str):
    perfil = repo.obtener_perfil(usuario_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return perfil


@app.get("/api/usuarios/{usuario_id}/pedidos")
def listar_pedidos(usuario_id: str):
    return repo.listar_pedidos_usuario(usuario_id)


@app.get("/api/pedidos/{id_pedido}")
def detalle_pedido(id_pedido: str):
    resultado = repo.obtener_detalle_pedido(id_pedido)
    if not resultado["info"]:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return resultado


@app.get("/api/pedidos")
def pedidos_por_estado(estado: str):
    return repo.buscar_pedidos_por_estado(estado)


@app.patch("/api/pedidos/{id_pedido}/estado")
def actualizar_estado(id_pedido: str, estado: str):
    repo.actualizar_estado_pedido(id_pedido, estado)
    return {"mensaje": f"Pedido {id_pedido} actualizado a '{estado}'"}


# ─── Diagnóstico Redis ────────────────────────────────────────────────────────

@app.get("/api/cache/ping")
def cache_ping():
    """Verifica si Redis está activo."""
    activo = repo._cache.ping()
    return {"redis_activo": activo}


@app.get("/api/cache/ttl/{clave}")
def cache_ttl(clave: str):
    """
    Retorna los segundos de vida restantes de una clave en Redis.
    -1 = clave existe pero sin TTL
    -2 = clave no existe (nunca se cargó o ya expiró)
    """
    segundos = repo._cache.ttl_restante(clave)
    return {"clave": clave, "ttl_segundos": segundos}


@app.delete("/api/cache/{clave}")
def cache_delete(clave: str):
    """Elimina manualmente una clave del caché. Fuerza recarga desde DynamoDB."""
    repo._cache.delete(clave)
    return {"mensaje": f"Clave '{clave}' eliminada del caché"}
