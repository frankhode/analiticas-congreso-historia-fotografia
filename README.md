# Congresos de Historia de la Fotografía

Sitio estático para consultar las ponencias catalogadas de los Congresos de Historia de la Fotografía.

## Fuente de datos

La fuente maestra de actualización es `fuente/secuencial.txt`, exportada desde Aleph. El script `scripts/procesar_secuencial.py` regenera automáticamente `data1.js` a `data5.js`, `subjects1.js` a `subjects5.js` y `datos/resumen.json`.

Se procesan los campos 600, 610, 611, 630, 650, 651 y 655. En encabezamientos de nombre, los subcampos ligados al nombre (`$d`, `$q`, etc.) se mantienen unidos; las subdivisiones `$x`, `$y`, `$z` y `$v` se presentan separadas por raya larga.

## Actualización

1. Abrir `/actualizar/` en GitHub Pages.
2. Seleccionar el nuevo secuencial de Aleph y revisar el control rápido.
3. Descargar la copia preparada como `secuencial.txt`.
4. Usar el botón para abrir la carpeta `fuente` en GitHub y subir ese archivo reemplazando el anterior.
5. Al confirmar el commit, GitHub Actions ejecuta `Actualizar datos desde Aleph`, regenera los archivos de datos y GitHub Pages publica el resultado.

La URL `/actualizar/` no es un mecanismo de seguridad: simplemente no está enlazada y lleva `noindex`. La modificación efectiva del repositorio queda protegida por la autenticación de GitHub.
