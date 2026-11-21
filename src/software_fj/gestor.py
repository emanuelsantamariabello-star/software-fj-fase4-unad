"""Gestor principal: registra entidades y supervisa transacciones en memoria."""
from __future__ import annotations

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any

from .errores import DatosInvalidos, EntidadNoEncontrada, RegistroDuplicado, ErrorSoftwareFJ
from .modelos import Cliente, Servicio, Reserva


def construir_logger(ruta_log: str | Path) -> logging.Logger:
    """Los archivos se usan SOLO para eventos y errores, no como base de datos."""
    ruta = Path(ruta_log)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger(f'software_fj.{ruta.resolve()}')
    log.setLevel(logging.INFO)
    log.propagate = False
    if not log.handlers:
        handler = RotatingFileHandler(ruta, maxBytes=512_000, backupCount=2, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        log.addHandler(handler)
    return log


class GestorReservas:
    """Listas internas; las excepciones se informan a la capa llamante."""
    def __init__(self, ruta_log: str | Path = 'logs/software_fj.log') -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []
        self.logger = construir_logger(ruta_log)

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes)  # Encapsulación: no se expone la lista modificable.

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self._servicios)

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos('Se requiere una instancia de Cliente.')
        if any(c.id == cliente.id for c in self._clientes):
            raise RegistroDuplicado(f'Cliente {cliente.id} ya registrado.')
        self._clientes.append(cliente)
        self.logger.info('CLIENTE_REGISTRADO id=%s', cliente.id)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos('Se requiere una instancia de Servicio.')
        if any(s.id == servicio.id for s in self._servicios):
            raise RegistroDuplicado(f'Servicio {servicio.id} ya registrado.')
        self._servicios.append(servicio)
        self.logger.info('SERVICIO_REGISTRADO id=%s tipo=%s', servicio.id, type(servicio).__name__)
        return servicio

    def obtener_cliente(self, identificador: str) -> Cliente:
        for cliente in self._clientes:
            if cliente.id == identificador:
                return cliente
        raise EntidadNoEncontrada(f'Cliente {identificador} inexistente.')

    def obtener_servicio(self, identificador: str) -> Servicio:
        for servicio in self._servicios:
            if servicio.id == identificador:
                return servicio
        raise EntidadNoEncontrada(f'Servicio {identificador} inexistente.')

    def obtener_reserva(self, identificador: str) -> Reserva:
        for reserva in self._reservas:
            if reserva.id == identificador:
                return reserva
        raise EntidadNoEncontrada(f'Reserva {identificador} inexistente.')

    def crear_reserva(self, identificador: str, cliente_id: str, servicio_id: str,
                      duracion_horas: Any, **parametros: Any) -> Reserva:
        if any(r.id == identificador for r in self._reservas):
            raise RegistroDuplicado(f'Reserva {identificador} ya registrada.')
        cliente = self.obtener_cliente(cliente_id)
        servicio = self.obtener_servicio(servicio_id)
        reserva = Reserva(identificador, cliente, servicio, duracion_horas, **parametros)
        self._reservas.append(reserva)
        self.logger.info('RESERVA_CREADA id=%s cliente=%s servicio=%s', identificador, cliente_id, servicio_id)
        return reserva

    def confirmar_reserva(self, reserva_id: str):
        reserva = self.obtener_reserva(reserva_id)
        total = reserva.confirmar()
        self.logger.info('RESERVA_CONFIRMADA id=%s total=%s', reserva.id, total)
        return total

    def procesar_reserva(self, reserva_id: str) -> None:
        reserva = self.obtener_reserva(reserva_id)
        reserva.procesar()
        self.logger.info('RESERVA_PROCESADA id=%s', reserva.id)

    def cancelar_reserva(self, reserva_id: str) -> None:
        reserva = self.obtener_reserva(reserva_id)
        reserva.cancelar()
        self.logger.info('RESERVA_CANCELADA id=%s', reserva.id)

    def ejecutar_seguro(self, nombre: str, operacion, *args, **kwargs):
        """Demuestra try/except/else/finally y mantiene viva la ejecución."""
        self.logger.info('OPERACION_INICIADA %s', nombre)
        try:
            resultado = operacion(*args, **kwargs)
        except ErrorSoftwareFJ as exc:
            self.logger.warning('OPERACION_RECHAZADA %s | %s: %s', nombre, type(exc).__name__, exc)
            return False, str(exc)
        except Exception:  # Última barrera solo para proteger la aplicación de demostración.
            self.logger.exception('ERROR_INESPERADO %s', nombre)
            return False, 'Ocurrió un error interno; revisar el archivo de log.'
        else:
            self.logger.info('OPERACION_EXITOSA %s', nombre)
            return True, resultado
        finally:
            self.logger.info('OPERACION_FINALIZADA %s', nombre)
