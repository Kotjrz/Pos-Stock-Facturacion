"""Inventory and product related routes."""
from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, jsonify, request
from sqlalchemy import case, func, select

from ..db import get_session
from ..models import (
    Atributo,
    Categoria,
    MovimientoStock,
    Producto,
    ProductoVariante,
    VarianteValor,
)

bp = Blueprint("inventory", __name__)

MOV_TIPO_NEGATIVO = {"SALIDA"}
ALLOWED_MOV_TYPES = {"ENTRADA", "SALIDA", "AJUSTE"}


@bp.get("/categorias")
def list_categorias():
    with get_session() as session:
        categorias = session.scalars(select(Categoria).order_by(Categoria.nombre)).all()

    return jsonify(
        [
            {
                "id": cat.idcategoria,
                "nombre": cat.nombre,
                "slug": cat.slug,
                "estado": cat.estado,
            }
            for cat in categorias
        ]
    )


@bp.get("/productos")
def list_productos():
    with get_session() as session:
        stock_subquery = (
            select(
                MovimientoStock.idvariante.label("mv_idvariante"),
                func.coalesce(
                    func.sum(
                        case(
                            (MovimientoStock.tipo.in_(MOV_TIPO_NEGATIVO), -MovimientoStock.cantidad),
                            else_=MovimientoStock.cantidad,
                        )
                    ),
                    0,
                ).label("stock_actual"),
            )
            .group_by(MovimientoStock.idvariante)
            .subquery()
        )

        rows = session.execute(
            select(
                Producto,
                ProductoVariante,
                stock_subquery.c.stock_actual,
            )
            .join(ProductoVariante, Producto.variantes, isouter=True)
            .join(stock_subquery, stock_subquery.c.mv_idvariante == ProductoVariante.idvariante, isouter=True)
            .order_by(Producto.nombre, ProductoVariante.idvariante)
        ).all()

        variantes_ids = [row[1].idvariante for row in rows if row[1] is not None]

        valores_map: dict[int, list[dict]] = defaultdict(list)
        if variantes_ids:
            valores_rows = session.execute(
                select(VarianteValor, Atributo)
                .join(Atributo, VarianteValor.idatributo == Atributo.idatributo)
                .where(VarianteValor.idvariante.in_(variantes_ids))
            ).all()
            for valor, atributo in valores_rows:
                valores_map[valor.idvariante].append(
                    {
                        "atributo": atributo.nombre,
                        "slug": atributo.slug,
                        "valor": _serialize_valor(valor),
                    }
                )

    productos: dict[int, dict] = {}
    for producto, variante, stock in rows:
        prod_entry = productos.setdefault(
            producto.idproducto,
            {
                "id": producto.idproducto,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "precio_venta": float(producto.precioventa or 0),
                "categoria_id": producto.idcategoria,
                "proveedor_id": producto.idproveedor,
                "variantes": [],
            },
        )
        if variante:
            prod_entry["variantes"].append(
                {
                    "id": variante.idvariante,
                    "sku": variante.sku,
                    "codigo_barras": variante.codigo_barras,
                    "precio_venta": float(variante.precio_venta or 0),
                    "stock_actual": int(stock or 0),
                    "stock_minimo": variante.stock_minimo,
                    "atributos": valores_map.get(variante.idvariante, []),
                }
            )

    return jsonify(list(productos.values()))


def _serialize_valor(valor: VarianteValor) -> str | float | bool | None:
    if valor.valor_texto is not None:
        return valor.valor_texto
    if valor.valor_numero is not None:
        return float(valor.valor_numero)
    if valor.valor_booleano is not None:
        return bool(valor.valor_booleano)
    return None


@bp.post("/stock/movimientos")
def registrar_movimiento():
    payload = request.get_json(silent=True) or {}
    idvariante = payload.get("idvariante")
    tipo = payload.get("tipo")
    cantidad = payload.get("cantidad")
    descripcion = payload.get("descripcion")

    if not idvariante or not isinstance(idvariante, int):
        return jsonify({"error": "idvariante es obligatorio"}), 400
    if tipo not in ALLOWED_MOV_TYPES:
        return jsonify({"error": "tipo de movimiento inválido"}), 400
    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"error": "cantidad debe ser un entero positivo"}), 400

    with get_session() as session:
        variante = session.get(ProductoVariante, idvariante)
        if not variante:
            return jsonify({"error": "Variante no encontrada"}), 404

        movimiento = MovimientoStock(
            idvariante=idvariante,
            tipo=tipo,
            cantidad=cantidad,
            descripcion=descripcion,
        )
        session.add(movimiento)

    return jsonify({"status": "ok", "idmovimiento": movimiento.idmovimiento}), 201
