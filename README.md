# Congresos de Historia de la Fotografía

Sitio estático para consultar las ponencias catalogadas de los Congresos de Historia de la Fotografía.

## Fuente de datos

La última tanda exportada desde Aleph se sube como `fuente/secuencial.txt`. El catálogo completo se conserva en `fuente/acumulado.txt`: cada tanda agrega registros nuevos y reemplaza los registros que tienen el mismo número de sistema, conservando los que no aparecen en la tanda. Repetir una carga no duplica registros.

El script `scripts/procesar_secuencial.py` regenera automáticamente `data1.js` a `data5.js`, `subjects1.js` a `subjects5.js` y `datos/resumen.json` a partir del acumulado. Reconoce números de congreso escritos como `4o`, `4º`, `4.º` o `4°`.

Se procesan los campos 600, 610, 611, 630, 650, 651 y 655. En encabezamientos de nombre, los subcampos ligados al nombre (`$d`, `$q`, etc.) se mantienen unidos; las subdivisiones `$x`, `$y`, `$z` y `$v` se presentan separadas por raya larga.

## Actualización

1. Abrir `/actualizar/` en GitHub Pages.
2. Seleccionar el nuevo secuencial de Aleph y revisar el control rápido.
3. Descargar la copia preparada como `secuencial.txt`.
4. Usar el botón para abrir la carpeta `fuente` en GitHub y subir ese archivo reemplazando el anterior.
5. Al confirmar el commit, GitHub Actions ejecuta `Actualizar datos desde Aleph`, regenera los archivos de datos y GitHub Pages publica el resultado.

Se puede subir una tanda parcial o una exportación completa. No reemplazar ni borrar `fuente/acumulado.txt`: lo mantiene el proceso automático. La ausencia de un registro en una tanda no lo elimina del catálogo.

Para procesar localmente: `python scripts/procesar_secuencial.py fuente/secuencial.txt . --master fuente/acumulado.txt`.

Pruebas del importador: `python -m unittest discover -s scripts -p 'test_*.py'`.

La URL `/actualizar/` no es un mecanismo de seguridad: simplemente no está enlazada y lleva `noindex`. La modificación efectiva del repositorio queda protegida por la autenticación de GitHub.
