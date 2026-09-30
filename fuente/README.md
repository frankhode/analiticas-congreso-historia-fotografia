# Fuente Aleph

Subir aquí el export secuencial con el nombre exacto `secuencial.txt`.

Cada reemplazo de ese archivo dispara automáticamente el procesamiento y la actualización de los datos publicados.

La carga es acumulativa: agrega registros nuevos y actualiza por número de sistema. Los registros ausentes de la tanda se conservan y repetir una carga no genera duplicados.

`acumulado.txt` contiene el catálogo completo y lo mantiene el proceso automático. No reemplazar ese archivo al subir una tanda.
