"""Testes dos exportadores técnicos (memorial descritivo, CSV e ZIP)."""

import os
import tempfile
import unittest
import zipfile
from fractions import Fraction

from pcf_nbr11742.calculator import dimensionar_projeto_portas
from pcf_nbr11742.exporters import (
    _fmt,
    _sanitizar_campo_csv,
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosPorta,
    DadosProjetoPortas,
    TipoFolhaPorta,
)


class TestExporters(unittest.TestCase):
    """Testes dos geradores de relatórios e exportação determinística."""

    def setUp(self) -> None:
        self.porta = DadosPorta(
            identificacao="PCF-EXP-01",
            ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_FUMACA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P90,
            largura_vao_livre_m=Fraction(100, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=80,
        )
        self.projeto = DadosProjetoPortas(
            nome_edificacao="Edifício Exemplo",
            responsavel_tecnico="Eng. Lofrano",
            portas=(self.porta,),
        )
        self.resultado = dimensionar_projeto_portas(self.projeto)

    def test_fmt_fracao(self) -> None:
        self.assertEqual(_fmt(Fraction(10, 1), 2), "10.0")
        self.assertEqual(_fmt(Fraction(1, 2), 2), "0.50")
        self.assertEqual(_fmt(Fraction(9, 10), 2), "0.90")
        self.assertEqual(_fmt(Fraction(22, 10), 2), "2.20")

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(_sanitizar_campo_csv("Normal"), "Normal")
        self.assertEqual(_sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(_sanitizar_campo_csv("+SUM(A1:A5)"), "'+SUM(A1:A5)")
        self.assertEqual(_sanitizar_campo_csv("-123"), "'-123")
        self.assertEqual(_sanitizar_campo_csv("@CMD"), "'@CMD")
        self.assertEqual(_sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(_sanitizar_campo_csv("\rcarriage"), "'\rcarriage")
        self.assertEqual(_sanitizar_campo_csv(""), "")

    def test_gerar_relatorio_texto(self) -> None:
        texto = gerar_relatorio_texto(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", texto)
        self.assertIn("PORTAS CORTA-FOGO E BARRAS ANTIPÂNICO", texto)
        self.assertIn("Edifício Exemplo", texto)
        self.assertIn("PCF-EXP-01", texto)
        self.assertIn("CONFORME", texto)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_txt = gerar_csv_sanitizado(self.resultado)
        linhas = csv_txt.strip().split("\n")
        self.assertGreaterEqual(len(linhas), 2)
        cabecalho = linhas[0]
        self.assertIn("identificacao", cabecalho)
        self.assertIn("classe_especificada", cabecalho)
        self.assertIn("conforme_geral", cabecalho)
        self.assertIn("PCF-EXP-01", linhas[1])

    def test_gerar_pacote_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = os.path.join(tmpdir, "pacote_teste.zip")
            svg_dummy = "<svg><text>Teste</text></svg>"
            gerar_pacote_zip(self.resultado, caminho_zip, svg_conteudo=svg_dummy)

            self.assertTrue(os.path.exists(caminho_zip))
            with zipfile.ZipFile(caminho_zip, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_descritivo.txt", nomes)
                self.assertIn("dados_portas.json", nomes)
                self.assertIn("resumo_portas.csv", nomes)
                self.assertIn("painel_esquematico.svg", nomes)

                # Verificar timestamp determinístico
                for info in zf.infolist():
                    self.assertEqual(info.date_time, (2026, 1, 1, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
