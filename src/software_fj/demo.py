"""Práctica simulada: 22 operaciones, incluyendo éxitos y errores controlados.

Ejecute: python -m software_fj.demo  (con PYTHONPATH=src o instalación editable)
"""
from __future__ import annotations

from pathlib import Path
from .gestor import GestorReservas
from .modelos import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada


def ejecutar_demostracion(ruta_log: str | Path = 'logs/software_fj.log') -> dict:
    app = GestorReservas(ruta_log)
    operaciones = [
        ('01 Cliente válido', app.registrar_cliente, Cliente('CL001', 'Laura Gomez', 'laura@ejemplo.com', '3001234567')),
        ('02 Cliente válido', app.registrar_cliente, Cliente('CL002', 'Carlos Ruiz', 'carlos@ejemplo.com', '3007654321')),
        ('03 Cliente duplicado', app.registrar_cliente, Cliente('CL001', 'Laura Gomez', 'laura@ejemplo.com', '3001234567')),
        ('04 Sala válida', app.registrar_servicio, ReservaSala('SA001', 'Sala empresarial', 80000, capacidad=12)),
        ('05 Equipo válido', app.registrar_servicio, AlquilerEquipo('EQ001', 'Proyector', 25000, existencias=2)),
        ('06 Asesoría válida', app.registrar_servicio, AsesoriaEspecializada('AS001', 'Analisis de datos', 95000, especialista='Lina Perez')),
        ('07 Servicio duplicado', app.registrar_servicio, ReservaSala('SA001', 'Otra sala', 40000, capacidad=6)),
        ('08 Reserva sala correcta', app.crear_reserva, 'RE001', 'CL001', 'SA001', 2),
        ('09 Reserva equipo incorrecta por stock', app.crear_reserva, 'RE002', 'CL002', 'EQ001', 1),
        ('10 Reserva asesoría correcta', app.crear_reserva, 'RE003', 'CL002', 'AS001', 1.5),
        ('11 Reserva cliente inexistente', app.crear_reserva, 'RE004', 'CL999', 'SA001', 2),
        ('12 Reserva con duración inválida', app.crear_reserva, 'RE005', 'CL001', 'SA001', -2),
        ('13 Confirmación de sala', app.confirmar_reserva, 'RE001'),
        ('14 Procesamiento de sala', app.procesar_reserva, 'RE001'),
        ('15 Cancelación imposible de procesada', app.cancelar_reserva, 'RE001'),
        ('16 Confirmación asesoría', app.confirmar_reserva, 'RE003'),
        ('17 Cancelación asesoría', app.cancelar_reserva, 'RE003'),
        ('18 Reserva equipo válida', app.crear_reserva, 'RE006', 'CL001', 'EQ001', 2),
        ('19 Confirmación equipo con impuesto y descuento', app.confirmar_reserva, 'RE006'),
        ('20 Reserva sin servicio', app.crear_reserva, 'RE007', 'CL001', 'ZZ999', 2),
    ]

    # Las operaciones 08, 09, 10 y 12 requieren parámetros particulares.
    # Se crean sus invocaciones aquí, sin persistir datos fuera de memoria.
    condiciones = {
        '08': {'asistentes': 5},
        '09': {'cantidad': 9},
        '10': {'tema': 'Analisis de ventas'},
        '12': {'asistentes': 2},
        '18': {'cantidad': 2, 'impuesto': 0.19, 'descuento': 0.10},
    }
    exitos, errores = 0, 0
    detalles = []
    for nombre, funcion, *args in operaciones:
        extra = condiciones.get(nombre[:2], {})
        ok, resultado = app.ejecutar_seguro(nombre, funcion, *args, **extra)
        exitos += int(ok)
        errores += int(not ok)
        etiqueta = 'OK' if ok else 'CONTROLADO'
        resultado_presentable = (resultado.describir() if hasattr(resultado, 'describir')
                                else ('Acción completada' if resultado is None else resultado))
        mensaje = f'[{etiqueta}] {nombre}: {resultado_presentable}'
        detalles.append(mensaje)
        print(mensaje)
    # Validación de un ejemplo inválido en fase de construcción (antes de registrar).
    def cliente_invalido():
        return app.registrar_cliente(Cliente('CL003', 'Eva Lopez', 'sin-arroba', '3001234567'))
    for etiqueta, operacion in (
        ('21 Cliente con correo inválido', cliente_invalido),
        ('22 Servicio con tarifa negativa', lambda: app.registrar_servicio(
            ReservaSala('SA002', 'Sala defectuosa', -10, capacidad=5))),
    ):
        ok, resultado = app.ejecutar_seguro(etiqueta, operacion)
        errores += int(not ok)
        exitos += int(ok)
        detalles.append(f'[{"OK" if ok else "CONTROLADO"}] {etiqueta}: {resultado}')
        print(detalles[-1])
    return {'operaciones': len(detalles), 'exitos': exitos, 'errores_controlados': errores,
            'clientes': len(app.clientes), 'servicios': len(app.servicios),
            'reservas': len(app.reservas), 'detalles': detalles}


if __name__ == '__main__':
    datos = ejecutar_demostracion()
    print('\nRESUMEN:', {k: v for k, v in datos.items() if k != 'detalles'})
