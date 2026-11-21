"""Pruebas de la práctica simulada con unittest (biblioteca estándar)."""
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from software_fj import (Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
                         GestorReservas, DatosInvalidos, RegistroDuplicado,
                         EntidadNoEncontrada, ServicioNoDisponible,
                         ReservaNoValida, EstadoReservaInvalido)
from software_fj.demo import ejecutar_demostracion


class PruebasModelo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log = Path(self.tmp.name) / 'eventos.log'
        self.g = GestorReservas(self.log)
        self.cliente = Cliente('CL001', 'Ana Maria', 'ANA@EJEMPLO.COM', '3001234567')
        self.sala = ReservaSala('SA001', 'Sala principal', 100, capacidad=4)
        self.equipo = AlquilerEquipo('EQ001', 'Portatil', 50, existencias=2)
        self.asesoria = AsesoriaEspecializada('AS001', 'Consultoria Python', 125, especialista='Pedro Gomez')
        self.g.registrar_cliente(self.cliente)
        for s in (self.sala, self.equipo, self.asesoria):
            self.g.registrar_servicio(s)

    def test_cliente_encapsulacion_correo_normalizado(self):
        self.assertEqual(self.cliente.correo, 'ana@ejemplo.com')
        self.assertTrue(self.cliente.describir().startswith('Cliente CL001'))
        self.assertNotIn('ana@ejemplo.com', self.cliente.describir())

    def test_correo_invalido_excepcion(self):
        with self.assertRaises(DatosInvalidos):
            Cliente('CL003', 'Maria Perez', 'correo-sin-arroba', '3001234567')

    def test_telefono_invalido_excepcion(self):
        with self.assertRaises(DatosInvalidos):
            Cliente('CL003', 'Maria Perez', 'maria@ejemplo.com', 'abc')

    def test_cliente_duplicado(self):
        with self.assertRaises(RegistroDuplicado):
            self.g.registrar_cliente(self.cliente)

    def test_servicio_tarifa_negativa(self):
        with self.assertRaises(DatosInvalidos):
            ReservaSala('SA002', 'Sala nueva', -1, capacidad=3)

    def test_capacidad_superada(self):
        with self.assertRaises(ServicioNoDisponible):
            self.g.crear_reserva('RE001', 'CL001', 'SA001', 3, asistentes=7)
        self.assertEqual(len(self.g.reservas), 0)

    def test_servicio_sin_disponibilidad(self):
        self.sala.disponible = False
        with self.assertRaises(ServicioNoDisponible):
            self.g.crear_reserva('RE001', 'CL001', 'SA001', 1, asistentes=2)

    def test_duracion_cero(self):
        with self.assertRaises(DatosInvalidos):
            self.g.crear_reserva('RE001', 'CL001', 'SA001', 0, asistentes=2)

    def test_tipo_invalido_asistentes(self):
        with self.assertRaises(ReservaNoValida):
            self.g.crear_reserva('RE001', 'CL001', 'SA001', 1, asistentes='dos')

    def test_servicio_faltante_y_encadenamiento_excepcion(self):
        with self.assertRaises(EntidadNoEncontrada):
            self.g.crear_reserva('RE001', 'CL001', 'NO000', 1, asistentes=2)
        with self.assertRaises(DatosInvalidos) as ctx:
            self.sala.calcular_costo('NoNumero', asistentes=2)
        self.assertIsNotNone(ctx.exception.__cause__)

    def test_variante_costo_con_impuesto_descuento(self):
        self.assertEqual(self.equipo.calcular_costo(2, cantidad=2), Decimal('200.00'))
        self.assertEqual(self.equipo.calcular_costo(2, cantidad=2, impuesto=.19, descuento=.10), Decimal('214.20'))

    def test_costo_parametros_invalidos(self):
        with self.assertRaises(DatosInvalidos):
            self.sala.calcular_costo(2, asistentes=2, descuento=1.5)

    def test_flujo_completo_reserva(self):
        self.g.crear_reserva('RE001', 'CL001', 'SA001', 2, asistentes=2)
        self.assertEqual(self.g.confirmar_reserva('RE001'), Decimal('200.00'))
        self.g.procesar_reserva('RE001')
        self.assertEqual(self.g.obtener_reserva('RE001').estado, 'PROCESADA')
        with self.assertRaises(EstadoReservaInvalido):
            self.g.cancelar_reserva('RE001')

    def test_reserva_cancelada_no_confirma(self):
        self.g.crear_reserva('RE001', 'CL001', 'AS001', 1, tema='Asesoria Python')
        self.g.cancelar_reserva('RE001')
        with self.assertRaises(EstadoReservaInvalido):
            self.g.confirmar_reserva('RE001')

    def test_servicios_son_polimorficos(self):
        precios = [
            self.sala.calcular_costo(2, asistentes=2),
            self.equipo.calcular_costo(2, cantidad=2),
            self.asesoria.calcular_costo(2, tema='Aprender Python')
        ]
        self.assertEqual(precios, [Decimal('200.00'), Decimal('200.00'), Decimal('250.00')])

    def test_ejecutar_seguro_controla_error_y_genera_log(self):
        ok, mensaje = self.g.ejecutar_seguro('Duplicado', self.g.registrar_cliente, self.cliente)
        self.assertFalse(ok)
        self.assertIn('ya registrado', mensaje)
        self.assertIn('OPERACION_RECHAZADA', self.log.read_text(encoding='utf-8'))

    def test_demo_mas_diez_operaciones_y_continua(self):
        resumen = ejecutar_demostracion(Path(self.tmp.name) / 'demo.log')
        self.assertGreaterEqual(resumen['operaciones'], 10)
        self.assertGreaterEqual(resumen['exitos'], 8)
        self.assertGreaterEqual(resumen['errores_controlados'], 5)
        self.assertTrue((Path(self.tmp.name) / 'demo.log').exists())


    def test_no_puede_instanciar_clases_abstractas(self):
        from software_fj.modelos import Entidad, Servicio
        with self.assertRaises(TypeError):
            Entidad('AB001')
        with self.assertRaises(TypeError):
            Servicio('SV001', 'Servicio base', 100)

    def test_colecciones_de_solo_lectura(self):
        snapshot = self.g.clientes
        self.assertIsInstance(snapshot, tuple)
        self.assertEqual(len(snapshot), 1)
        with self.assertRaises(AttributeError):
            snapshot.append(self.cliente)
        self.assertEqual(len(self.g.clientes), 1)

    def test_validacion_del_cliente_al_modificar_propiedad(self):
        with self.assertRaises(DatosInvalidos):
            self.cliente.correo = 'correo-invalido'
        self.assertEqual(self.cliente.correo, 'ana@ejemplo.com')

    def test_no_admite_importes_no_finitos(self):
        for importe in ('NaN', 'Infinity', '-Infinity', -1, True):
            with self.subTest(importe=importe):
                with self.assertRaises(DatosInvalidos):
                    ReservaSala('SA002', 'Sala incorrecta', importe, capacidad=4)

    def test_reserva_duplicada(self):
        self.g.crear_reserva('RE001', 'CL001', 'SA001', 2, asistentes=2)
        with self.assertRaises(RegistroDuplicado):
            self.g.crear_reserva('RE001', 'CL001', 'SA001', 3, asistentes=3)
        self.assertEqual(len(self.g.reservas), 1)

    def test_error_de_servicio_desactivado_al_confirmar(self):
        self.g.crear_reserva('RE001', 'CL001', 'SA001', 2, asistentes=2)
        self.sala.disponible = False
        with self.assertRaises(ServicioNoDisponible):
            self.g.confirmar_reserva('RE001')
        self.assertEqual(self.g.obtener_reserva('RE001').estado, 'CREADA')

    def test_registro_error_inesperado_y_continuidad(self):
        def funcion_falla():
            raise RuntimeError('Error simulado para verificar recuperación')
        ok, mensaje = self.g.ejecutar_seguro('Inesperado', funcion_falla)
        self.assertFalse(ok)
        self.assertIn('error interno', mensaje)
        ok2, cliente = self.g.ejecutar_seguro('Cliente válido posterior',
            self.g.registrar_cliente,
            Cliente('CL004', 'Mariana Lopez', 'mariana@ejemplo.com', '3005556677'))
        self.assertTrue(ok2)
        self.assertEqual(cliente.id, 'CL004')
        contenido = self.log.read_text(encoding='utf-8')
        self.assertIn('ERROR_INESPERADO', contenido)
        self.assertIn('OPERACION_FINALIZADA', contenido)

    def test_variante_porcentajes_cero_y_maximo(self):
        precio = self.sala.calcular_costo(2, asistentes=2, descuento=1)
        self.assertEqual(precio, Decimal('0.00'))
        precio_con_impuesto = self.sala.calcular_costo(2, asistentes=2, impuesto=1)
        self.assertEqual(precio_con_impuesto, Decimal('400.00'))


if __name__ == '__main__':
    unittest.main()
