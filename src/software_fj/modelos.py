"""Modelos del dominio. Mantiene datos en memoria; sin uso de bases de datos.

Demuestra abstracción, herencia, polimorfismo, encapsulación y métodos
con parámetros opcionales que permiten varias formas de cálculo.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, overload

from .errores import DatosInvalidos, ServicioNoDisponible, ReservaNoValida, EstadoReservaInvalido

_DOS_DECIMALES = Decimal('0.01')


def dinero(valor: Any, *, permitir_cero: bool = False) -> Decimal:
    """Convierte números a Decimal y descarta NaN, infinito y negativos."""
    if isinstance(valor, bool):
        raise DatosInvalidos('No se admiten booleanos como importes.')
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise DatosInvalidos(f'Importe no numérico: {valor!r}') from exc
    if not numero.is_finite() or numero < 0 or (not permitir_cero and numero == 0):
        raise DatosInvalidos('El importe debe ser finito y positivo.')
    return numero


def duracion_valida(valor: Any) -> Decimal:
    """La duración positiva se mide en horas y puede incluir fracciones."""
    return dinero(valor)


def porcentaje(valor: Any, nombre: str) -> Decimal:
    p = dinero(valor, permitir_cero=True)
    if p > 1:
        raise DatosInvalidos(f'{nombre} debe estar entre 0 y 1 (0.19 = 19 %).')
    return p


def identificador_valido(valor: Any, etiqueta: str) -> str:
    if not isinstance(valor, str) or not re.fullmatch(r'[A-Za-z0-9_-]{2,24}', valor.strip()):
        raise DatosInvalidos(f'{etiqueta}: use de 2 a 24 letras/números, _ o -.')
    return valor.strip()


def texto_valido(valor: Any, etiqueta: str, minimo: int = 3) -> str:
    if not isinstance(valor, str) or len(valor.strip()) < minimo:
        raise DatosInvalidos(f'{etiqueta} debe contener al menos {minimo} caracteres.')
    return valor.strip()


class Entidad(ABC):
    """Abstracción general del modelo con identificador de solo lectura."""
    def __init__(self, identificador: str) -> None:
        self._id = identificador_valido(identificador, 'Identificador')

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve descripción pública de la entidad."""


class Cliente(Entidad):
    """Cliente con nombre y datos privados validados mediante propiedades."""
    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = texto_valido(valor, 'Nombre')

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', valor.strip()):
            raise DatosInvalidos('El correo electrónico no es válido.')
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r'\+?[0-9]{7,15}', valor.strip()):
            raise DatosInvalidos('Teléfono: se requieren de 7 a 15 dígitos (opcional +).')
        self._telefono = valor.strip()

    def describir(self) -> str:
        return f'Cliente {self.id}: {self.nombre}'  # Evita mostrar datos de contacto en la consola.


class Servicio(Entidad, ABC):
    """Servicio abstracto con capacidad de cálculo y validación polimórfica."""
    def __init__(self, identificador: str, nombre: str, tarifa_hora: Any,
                 disponible: bool = True) -> None:
        super().__init__(identificador)
        self._nombre = texto_valido(nombre, 'Nombre de servicio')
        self._tarifa_hora = dinero(tarifa_hora)
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> Decimal:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise DatosInvalidos('La disponibilidad debe ser verdadera o falsa.')
        self._disponible = valor

    @abstractmethod
    def validar_parametros(self, duracion_horas: Any, **parametros: Any) -> None:
        """Valida las características específicas de cada servicio."""

    @overload
    def calcular_costo(self, duracion_horas: Any, **parametros: Any) -> Decimal: ...

    @overload
    def calcular_costo(self, duracion_horas: Any, *, impuesto: Any,
                      descuento: Any = 0, **parametros: Any) -> Decimal: ...

    @abstractmethod
    def calcular_costo(self, duracion_horas: Any, *, impuesto: Any = 0,
                      descuento: Any = 0, **parametros: Any) -> Decimal:
        """Calcula el costo usando la variante simple o con impuestos/descuento."""

    def _calculo(self, cantidad: Any, duracion_horas: Any,
                 impuesto: Any, descuento: Any) -> Decimal:
        # Se aplica descuento antes de impuestos; todas las tasas son fracciones.
        base = self.tarifa_hora * duracion_valida(duracion_horas) * dinero(cantidad)
        total = base * (1 - porcentaje(descuento, 'Descuento')) * (1 + porcentaje(impuesto, 'Impuesto'))
        return total.quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)


class ReservaSala(Servicio):
    """Alquiler de sala con capacidad máxima de asistentes."""
    def __init__(self, identificador: str, nombre: str, tarifa_hora: Any,
                 capacidad: int, disponible: bool = True) -> None:
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise DatosInvalidos('Capacidad de sala debe ser entero positivo.')
        self.capacidad = capacidad

    def validar_parametros(self, duracion_horas: Any, **parametros: Any) -> None:
        duracion_valida(duracion_horas)
        if not self.disponible:
            raise ServicioNoDisponible(f'Sala {self.id} no disponible.')
        asistentes = parametros.get('asistentes')
        if isinstance(asistentes, bool) or not isinstance(asistentes, int) or asistentes < 1:
            raise ReservaNoValida('Debe indicar asistentes como entero positivo.')
        if asistentes > self.capacidad:
            raise ServicioNoDisponible(f'Aforo {asistentes} supera capacidad {self.capacidad}.')

    def calcular_costo(self, duracion_horas: Any, *, impuesto: Any = 0,
                      descuento: Any = 0, **parametros: Any) -> Decimal:
        self.validar_parametros(duracion_horas, **parametros)
        return self._calculo(1, duracion_horas, impuesto, descuento)

    def describir(self) -> str:
        return f'Sala {self.nombre}, capacidad {self.capacidad}, tarifa/hora {self.tarifa_hora}'


class AlquilerEquipo(Servicio):
    """Alquiler de uno o varios equipos, restringido por existencias."""
    def __init__(self, identificador: str, nombre: str, tarifa_hora: Any,
                 existencias: int, disponible: bool = True) -> None:
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if isinstance(existencias, bool) or not isinstance(existencias, int) or existencias < 1:
            raise DatosInvalidos('Existencias deben ser entero positivo.')
        self.existencias = existencias

    def validar_parametros(self, duracion_horas: Any, **parametros: Any) -> None:
        duracion_valida(duracion_horas)
        if not self.disponible:
            raise ServicioNoDisponible(f'Equipo {self.id} no disponible.')
        cantidad = parametros.get('cantidad')
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 1:
            raise ReservaNoValida('Debe indicar cantidad como entero positivo.')
        if cantidad > self.existencias:
            raise ServicioNoDisponible(f'Se solicitan {cantidad}, disponibles {self.existencias}.')

    def calcular_costo(self, duracion_horas: Any, *, impuesto: Any = 0,
                      descuento: Any = 0, **parametros: Any) -> Decimal:
        self.validar_parametros(duracion_horas, **parametros)
        return self._calculo(parametros['cantidad'], duracion_horas, impuesto, descuento)

    def describir(self) -> str:
        return f'Equipo {self.nombre}, stock {self.existencias}, tarifa/hora {self.tarifa_hora}'


class AsesoriaEspecializada(Servicio):
    """Asesoría que exige asunto y nombre del especialista."""
    def __init__(self, identificador: str, nombre: str, tarifa_hora: Any,
                 especialista: str, disponible: bool = True) -> None:
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self.especialista = texto_valido(especialista, 'Especialista')

    def validar_parametros(self, duracion_horas: Any, **parametros: Any) -> None:
        duracion_valida(duracion_horas)
        if not self.disponible:
            raise ServicioNoDisponible(f'Asesoría {self.id} no disponible.')
        texto_valido(parametros.get('tema'), 'Tema de asesoría', minimo=5)

    def calcular_costo(self, duracion_horas: Any, *, impuesto: Any = 0,
                      descuento: Any = 0, **parametros: Any) -> Decimal:
        self.validar_parametros(duracion_horas, **parametros)
        return self._calculo(1, duracion_horas, impuesto, descuento)

    def describir(self) -> str:
        return f'Asesoría {self.nombre} con {self.especialista}, tarifa/hora {self.tarifa_hora}'


class Reserva(Entidad):
    """Estado de una reserva y transiciones válidas; no persiste en archivos."""
    CREADA = 'CREADA'
    CONFIRMADA = 'CONFIRMADA'
    PROCESADA = 'PROCESADA'
    CANCELADA = 'CANCELADA'

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio,
                 duracion_horas: Any, *, impuesto: Any = 0, descuento: Any = 0,
                 **parametros: Any) -> None:
        super().__init__(identificador)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaNoValida('Cliente y servicio deben ser objetos válidos.')
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = duracion_valida(duracion_horas)
        self.parametros = dict(parametros)
        self.impuesto = porcentaje(impuesto, 'Impuesto')
        self.descuento = porcentaje(descuento, 'Descuento')
        self._estado = self.CREADA
        self._costo: Decimal | None = None
        # Una reserva inválida se rechaza de inmediato, sin modificar otras listas.
        self.servicio.validar_parametros(self.duracion_horas, **self.parametros)

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo(self) -> Decimal | None:
        return self._costo

    def confirmar(self) -> Decimal:
        if self.estado != self.CREADA:
            raise EstadoReservaInvalido('Solo es posible confirmar reservas creadas.')
        # Revalida disponibilidad para evitar confirmar servicios ahora deshabilitados.
        self._costo = self.servicio.calcular_costo(
            self.duracion_horas, impuesto=self.impuesto,
            descuento=self.descuento, **self.parametros)
        self._estado = self.CONFIRMADA
        return self._costo

    def procesar(self) -> None:
        if self.estado != self.CONFIRMADA:
            raise EstadoReservaInvalido('Solo se procesan reservas confirmadas.')
        self._estado = self.PROCESADA

    def cancelar(self) -> None:
        if self.estado not in (self.CREADA, self.CONFIRMADA):
            raise EstadoReservaInvalido('Solo se cancelan reservas creadas o confirmadas.')
        self._estado = self.CANCELADA

    def describir(self) -> str:
        return f'Reserva {self.id}: cliente={self.cliente.id}, servicio={self.servicio.id}, estado={self.estado}'
