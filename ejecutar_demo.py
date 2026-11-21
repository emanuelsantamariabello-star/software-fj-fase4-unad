"""Lanzador multiplataforma que no necesita instalar paquetes externos."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from software_fj.demo import ejecutar_demostracion

if __name__ == '__main__':
    resumen = ejecutar_demostracion()
    print('\nRESUMEN FINAL')
    for clave in ('operaciones', 'exitos', 'errores_controlados', 'clientes', 'servicios', 'reservas'):
        print(f'  {clave}: {resumen[clave]}')
