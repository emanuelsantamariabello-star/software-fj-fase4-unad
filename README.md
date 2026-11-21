# Software FJ · Fase 4 - Prácticas simuladas

**UNAD | Ingeniería de Sistemas | Programación 213023**  
**Autor de esta implementación independiente:** Emanuel Steban Santamaria Bello  
**Presentación individual:** sujeta a autorización de la tutora. La guía original establece modalidad colaborativa.

## Objetivo del proyecto

Aplicación de Python 3.10+ para gestionar clientes, servicios (salas, alquiler de equipos y asesorías) y reservas con programación orientada a objetos, validaciones y manejo avanzado de excepciones. **No usa bases de datos ni persistencia de registros operativos**: clientes, servicios y reservas existen exclusivamente en listas de memoria. Los archivos únicamente se emplean para eventos y errores en un log.

## Cómo ejecutarlo

En Windows, abre la carpeta del proyecto y ejecuta en PowerShell o CMD:

```powershell
py ejecutar_demo.py
py -m unittest discover -s tests -v
```

Si tu sistema utiliza `python` en lugar de `py`, reemplázalo en ambos comandos. No se necesitan dependencias de terceros ni instalación con `pip`.

La primera ejecución simula **22 operaciones**: 13 correctas y 9 fallidas de forma controlada, sin detener el programa. La segunda ejecuta **25 pruebas automatizadas**; al final debe aparecer `OK`.

Cada ejecución crea o actualiza `logs/software_fj.log`, que registra operaciones, errores esperados e inesperados. El log no contiene información persistente de clientes ni reservas.

## Estructura

```text
SoftwareFJ_Fase4_Entrega/
├── ejecutar_demo.py
├── README.md
├── .gitignore
├── src/
│   └── software_fj/
│       ├── __init__.py
│       ├── modelos.py          # Entidad, Cliente, Servicio, subclases y Reserva
│       ├── errores.py          # Excepciones personalizadas
│       ├── gestor.py           # Listas, reglas de operaciones y logging
│       └── demo.py             # 22 operaciones de ejemplo
├── tests/
│   └── test_software_fj.py     # 25 pruebas unittest
├── logs/                        # Se genera al ejecutar; no subir logs personales
└── docs/
    ├── Informe_Fase4_Individual.docx
    ├── Informe_Fase4_Individual_BORRADOR.pdf
    ├── evidencia_simulacion.txt
    ├── evidencia_pruebas.txt
    └── COMO_PUBLICAR_Y_ENTREGAR.md
```

## Correspondencia con Anexo 3

| Requisito | Implementación |
|---|---|
| Entidad abstracta | `Entidad`, en `modelos.py` |
| Clase Cliente y encapsulación | `Cliente`, propiedades con validación |
| Servicio abstracto, 3 servicios derivados | `Servicio`, `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| Sobrescritura y polimorfismo | `calcular_costo`, `describir`, `validar_parametros` |
| Métodos con variantes | `calcular_costo` con `impuesto` y `descuento`; sobrecarga de tipos documentada con `typing.overload` |
| Reserva y estados | `Reserva`: CREADA, CONFIRMADA, PROCESADA, CANCELADA |
| Excepciones personalizadas | `errores.py` y comprobaciones en servicios y reservas |
| try/except/else/finally | `GestorReservas.ejecutar_seguro` |
| Encadenamiento de excepciones | `raise ... from exc` en `dinero` |
| Logs | `RotatingFileHandler` en `gestor.py` |
| Al menos 10 operaciones | `demo.py`: 22 escenarios, correctos e incorrectos |
| Pruebas | `unittest` con 25 casos y resultados documentados |

### Reglas de cálculo

Las tasas se expresan como fracciones: `0.19` corresponde a 19 %. El sistema calcula el subtotal, aplica el descuento y después el impuesto. Los importes se procesan con `decimal.Decimal`, redondeando a 2 decimales al final.

Las validaciones rechazan por ejemplo: correos mal formados, registros duplicados, tarifas negativas, duración cero, capacidad superada, stock insuficiente, falta de cliente, servicio no disponible y estados de reserva incompatibles.

**Alcance:** simulación académica; no contiene una agenda de disponibilidad por fechas ni reservas simultáneas de recursos físicos. La guía exige robustez y simulación sin base de datos, no una plataforma comercial de reservas en tiempo real.

## Publicación y entrega

El trabajo requiere repositorio GitHub y un PDF con portada, introducción, enlace, conclusiones y referencias APA. Este paquete se ha preparado **sin publicar** ni afirmar una excepción individual que la tutora no haya concedido.

Antes de entregarlo, publica este código en un repositorio de tu titularidad o integra un aporte identificable al repositorio oficial del grupo si corresponde, verifica que corre allí y **sustituye el marcador del enlace en el informe Word**. Exporta el informe a PDF y revísalo. El PDF incluido en este paquete es un borrador académico con marcador; no debe enviarse sin la URL real.
