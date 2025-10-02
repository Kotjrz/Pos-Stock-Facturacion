"""SQLAlchemy ORM models mapping Supabase tables."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Categoria(Base):
    __tablename__ = "categorias"

    idcategoria: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    descripcion: Mapped[Optional[str]]
    estado: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    productos: Mapped[list["Producto"]] = relationship(
        "Producto", back_populates="categoria"
    )


class Proveedor(Base):
    __tablename__ = "proveedores"

    idproveedor: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String)
    telefono: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    direccion: Mapped[Optional[str]]
    cuit: Mapped[Optional[str]] = mapped_column(String, unique=True)
    estado: Mapped[bool] = mapped_column(Boolean, default=True)

    productos: Mapped[list["Producto"]] = relationship(
        "Producto", back_populates="proveedor"
    )


class Producto(Base):
    __tablename__ = "productos"

    idproducto: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String)
    preciocompra: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    precioventa: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    stockactual: Mapped[Optional[int]]
    stockminimo: Mapped[Optional[int]]
    fechaingreso: Mapped[date] = mapped_column(Date, default=date.today)
    descripcion: Mapped[Optional[str]]
    estado: Mapped[bool] = mapped_column(Boolean, default=True)

    idcategoria: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.idcategoria"))
    idproveedor: Mapped[Optional[int]] = mapped_column(ForeignKey("proveedores.idproveedor"))

    categoria: Mapped[Optional["Categoria"]] = relationship(
        "Categoria", back_populates="productos"
    )
    proveedor: Mapped[Optional["Proveedor"]] = relationship(
        "Proveedor", back_populates="productos"
    )
    variantes: Mapped[list["ProductoVariante"]] = relationship(
        "ProductoVariante", back_populates="producto", cascade="all, delete-orphan"
    )


class ProductoVariante(Base):
    __tablename__ = "producto_variantes"

    idvariante: Mapped[int] = mapped_column(primary_key=True)
    idproducto: Mapped[int] = mapped_column(ForeignKey("productos.idproducto"))
    sku: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    codigo_barras: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    precio_compra: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    precio_venta: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0)
    estado: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    producto: Mapped["Producto"] = relationship("Producto", back_populates="variantes")
    valores: Mapped[list["VarianteValor"]] = relationship(
        "VarianteValor", back_populates="variante", cascade="all, delete-orphan"
    )
    movimientos: Mapped[list["MovimientoStock"]] = relationship(
        "MovimientoStock", back_populates="variante", cascade="all, delete-orphan"
    )
    detalles_venta: Mapped[list["DetalleVenta"]] = relationship(
        "DetalleVenta", back_populates="variante"
    )


class Atributo(Base):
    __tablename__ = "atributos"

    idatributo: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    tipo_dato: Mapped[str] = mapped_column(String(30))
    es_obligatorio: Mapped[bool] = mapped_column(Boolean, default=False)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    opciones: Mapped[list["AtributoOpcion"]] = relationship(
        "AtributoOpcion", back_populates="atributo", cascade="all, delete-orphan"
    )


class CategoriaAtributo(Base):
    __tablename__ = "categoria_atributos"
    __table_args__ = (UniqueConstraint("idcategoria", "idatributo", name="categoria_atributo_key"),)

    idcategoria: Mapped[int] = mapped_column(ForeignKey("categorias.idcategoria"), primary_key=True)
    idatributo: Mapped[int] = mapped_column(ForeignKey("atributos.idatributo"), primary_key=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)


class AtributoOpcion(Base):
    __tablename__ = "atributo_opciones"

    idopcion: Mapped[int] = mapped_column(primary_key=True)
    idatributo: Mapped[int] = mapped_column(ForeignKey("atributos.idatributo"))
    valor: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    atributo: Mapped["Atributo"] = relationship("Atributo", back_populates="opciones")


class VarianteValor(Base):
    __tablename__ = "variante_valores"

    idvariante: Mapped[int] = mapped_column(
        ForeignKey("producto_variantes.idvariante", ondelete="CASCADE"), primary_key=True
    )
    idatributo: Mapped[int] = mapped_column(ForeignKey("atributos.idatributo"), primary_key=True)
    valor_texto: Mapped[Optional[str]]
    valor_numero: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    valor_booleano: Mapped[Optional[bool]]
    idopcion: Mapped[Optional[int]] = mapped_column(ForeignKey("atributo_opciones.idopcion"))

    variante: Mapped["ProductoVariante"] = relationship(
        "ProductoVariante", back_populates="valores"
    )
    atributo: Mapped["Atributo"] = relationship("Atributo")
    opcion: Mapped[Optional["AtributoOpcion"]] = relationship("AtributoOpcion")


class Empleado(Base):
    __tablename__ = "empleados"

    idempleado: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str]
    apellido: Mapped[Optional[str]]
    dni: Mapped[Optional[str]] = mapped_column(String, unique=True)
    rol: Mapped[Optional[str]]
    telefono: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    fechaingreso: Mapped[date] = mapped_column(Date, default=date.today)
    estado: Mapped[bool] = mapped_column(Boolean, default=True)

    ventas: Mapped[list["Venta"]] = relationship("Venta", back_populates="empleado")
    usuario: Mapped[Optional["Usuario"]] = relationship(
        "Usuario", back_populates="empleado", uselist=False
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    idusuario: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    dni_empleado: Mapped[str] = mapped_column(String, unique=True)
    rol: Mapped[Optional[str]] = mapped_column(String(50))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    empleado: Mapped[Optional["Empleado"]] = relationship(
        "Empleado", back_populates="usuario", primaryjoin="Usuario.dni_empleado==Empleado.dni"
    )


class Venta(Base):
    __tablename__ = "ventas"

    idventa: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    idempleado: Mapped[Optional[int]] = mapped_column(ForeignKey("empleados.idempleado"))
    total: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    metodopago: Mapped[Optional[str]]

    empleado: Mapped[Optional["Empleado"]] = relationship("Empleado", back_populates="ventas")
    detalles: Mapped[list["DetalleVenta"]] = relationship(
        "DetalleVenta", back_populates="venta"
    )


class DetalleVenta(Base):
    __tablename__ = "detalleventa"

    iddetalle: Mapped[int] = mapped_column(primary_key=True)
    idventa: Mapped[Optional[int]] = mapped_column(ForeignKey("ventas.idventa"))
    idproducto: Mapped[Optional[int]] = mapped_column(ForeignKey("productos.idproducto"))
    idvariante: Mapped[Optional[int]] = mapped_column(ForeignKey("producto_variantes.idvariante"))
    cantidad: Mapped[Optional[int]]
    preciounitario: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric)

    venta: Mapped[Optional["Venta"]] = relationship("Venta", back_populates="detalles")
    variante: Mapped[Optional["ProductoVariante"]] = relationship(
        "ProductoVariante", back_populates="detalles_venta"
    )


class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="movimientos_stock_cantidad_check"),
    )

    idmovimiento: Mapped[int] = mapped_column(primary_key=True)
    idvariante: Mapped[int] = mapped_column(ForeignKey("producto_variantes.idvariante"))
    tipo: Mapped[str] = mapped_column(String(20))
    cantidad: Mapped[int] = mapped_column(Integer)
    referencia_id: Mapped[Optional[int]] = mapped_column(Integer)
    referencia_tipo: Mapped[Optional[str]] = mapped_column(String(50))
    descripcion: Mapped[Optional[str]]
    idempleado: Mapped[Optional[int]] = mapped_column(ForeignKey("empleados.idempleado"))
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    variante: Mapped["ProductoVariante"] = relationship(
        "ProductoVariante", back_populates="movimientos"
    )
    empleado: Mapped[Optional["Empleado"]] = relationship("Empleado")
