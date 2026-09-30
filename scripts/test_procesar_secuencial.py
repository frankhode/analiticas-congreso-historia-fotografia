import tempfile
import unittest
from pathlib import Path

from procesar_secuencial import merge_records, parse, read_records


def record(rid, title, ordinal='4º', subjects=('Fotografía',)):
    lines = [
        f'{rid} FMT   L BK',
        f'{rid} 24510 L $$a{title}',
        f'{rid} 1001  L $$aApellido, Nombre',
        f'{rid} 7731  L $$aCongreso de Historia de la Fotografía ({ordinal} : 1995 octubre : Buenos Aires)$$gp. 1-2',
    ]
    lines += [f'{rid} 650 4 L $$a{subject}' for subject in subjects]
    return '\n'.join(lines) + '\n'


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'secuencial.txt'
        self.master = Path(self.temp.name) / 'acumulado.txt'

    def test_partial_batch_updates_whole_record_and_preserves_others(self):
        old = record('000000001', 'Sin cambios', '3o')
        self.master.write_text(old + record('000000002', 'Título anterior', subjects=('Tema anterior',)), encoding='utf-8')
        updated = record('000000002', 'Título corregido', subjects=('Pintura', 'Arte'))
        self.source.write_text(updated + record('000000003', 'Ponencia nueva'), encoding='utf-8')
        merge_records(self.source, self.master)
        rows, summary = parse(self.master)
        self.assertEqual(summary['analytics'], 3)
        by_id = {r['id']: r for r in rows}
        self.assertEqual(by_id['000000002']['title'], 'Título corregido')
        self.assertEqual(by_id['000000002']['subjects'], ['Pintura', 'Arte'])
        self.assertEqual(read_records(self.master)['000000001'], old.splitlines())
        self.assertEqual(read_records(self.master)['000000002'], updated.splitlines())
        before = self.master.read_bytes()
        merge_records(self.source, self.master)
        self.assertEqual(self.master.read_bytes(), before)

    def test_ordinal_variants(self):
        for ordinal in ('4o', '4º', '4.º', '4°', '4O'):
            with self.subTest(ordinal=ordinal):
                self.source.write_text(record('000000001', 'Título', ordinal), encoding='utf-8')
                rows, summary = parse(self.source)
                self.assertEqual((rows[0]['congressNo'], rows[0]['year']), (4, 1995))
                self.assertEqual(summary['warnings']['sin_congreso_identificado'], [])

    def test_invalid_batch_does_not_change_master(self):
        self.master.write_text(record('000000001', 'Conservar'), encoding='utf-8')
        before = self.master.read_bytes()
        for bad in ('', 'archivo incorrecto', '000000001 FMT   L BK\n'):
            with self.subTest(bad=bad):
                self.source.write_text(bad, encoding='utf-8')
                with self.assertRaises(ValueError):
                    merge_records(self.source, self.master)
                self.assertEqual(self.master.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
