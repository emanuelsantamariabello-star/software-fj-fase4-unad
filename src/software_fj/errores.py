"""Excepciones de dominio: errores esperables y controlados de la aplicación."""

class ErrorSoftwareFJ(Exception):
    """Clase base para excepciones recuperables del negocio."""


class DatosInvalidos(ErrorSoftwareFJ):
    """Un dato no respeta las restricciones del modelo."""


class RegistroDuplicado(ErrorSoftwareFJ):
    """Se intenta registrar nuevamente un identificador."""


class EntidadNoEncontrada(ErrorSoftwareFJ):
    """Un cliente, servicio o reserva no existe."""


class ServicioNoDisponible(ErrorSoftwareFJ):
    """El servicio no está habilitado o no tiene capacidad suficiente."""


class ReservaNoValida(ErrorSoftwareFJ):
    """Las características de la reserva no son aceptables."""


class EstadoReservaInvalido(ErrorSoftwareFJ):
    """La transición solicitada no es válida para el estado de la reserva."""
