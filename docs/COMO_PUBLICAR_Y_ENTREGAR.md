# Últimos pasos para presentar la Fase 4

1. La tutora estableció modalidad colaborativa. Envía y conserva la solicitud de excepción; **no presupongas que una entrega individual será aceptada**.
2. Entra a GitHub con tu cuenta y crea un repositorio público nuevo con nombre sugerido `software-fj-fase4-unad`. No marques «Initialize with README», pues el ZIP ya contiene uno.
3. Extrae el ZIP y sube los archivos del proyecto a dicho repositorio. Es posible hacerlo desde **Add file → Upload files** o usando Git desde la carpeta descomprimida:

```bash
git init
git add .
git commit -m "Implementar Software FJ Fase 4 con POO y manejo de excepciones"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/software-fj-fase4-unad.git
git push -u origin main
```

4. Verifica que en GitHub se vean `ejecutar_demo.py`, `src/`, `tests/`, `README.md`. **No subas registros personales de logs.**
5. Prueba `py ejecutar_demo.py` y `py -m unittest discover -s tests -v` en la copia local.
6. Abre `docs/Informe_Fase4_Individual.docx`, reemplaza `[[ENLACE_GITHUB]]` por la URL real, revisa tus datos y exporta a PDF.
7. Si la tutora autorizó la modalidad individual, adjunta el PDF al enlace de entrega del campus. De lo contrario, consulta y gestiona el aporte con el grupo; el repositorio independiente no garantiza la calificación.
8. Confirma en el campus que el archivo quedó **entregado**, no solamente cargado como borrador.

Fecha de cierre indicada en la guía: domingo 22/11/2026. Las reglas de la tutora y de la plataforma son las que determinan la validez de la entrega.
