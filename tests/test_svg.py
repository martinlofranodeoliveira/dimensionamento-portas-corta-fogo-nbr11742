"""Testes do gerador de painel técnico SVG."""

import unittest
from fractions import Fraction

from pcf_nbr11742.calculator import dimensionar_projeto_portas
from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosBarraAntipanico,
    DadosPorta,
    DadosProjetoPortas,
    TipoFolhaPorta,
)
from pcf_nbr11742.svg_generator import gerar_painel_svg


class TestSVG(unittest.TestCase):
    """Testes de conformidade e integridade do gerador vetorial SVG."""

    def test_gerar_painel_svg_estrutura(self) -> None:
        porta = DadosPorta(
            identificacao="PCF-AUD-01",
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            tipo_folha=TipoFolhaPorta.DUPLA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(220, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=300,
            possui_seletor_fechamento=True,
            possui_eletroima_retencao=True,
            dados_barra=DadosBarraAntipanico(
                instalada=True,
                altura_instalacao_m=Fraction(100, 100),
                comprimento_barra_m=Fraction(70, 100),
                forca_operacao_n=120,
            ),
        )
        proj = DadosProjetoPortas(
            nome_edificacao="Teatro Metropolitano",
            responsavel_tecnico="Eng. Lofrano",
            portas=(porta,),
        )
        res = dimensionar_projeto_portas(proj)
        svg = gerar_painel_svg(res)

        self.assertIsInstance(svg, str)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn("Teatro Metropolitano", svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("DETALHE EXECUTIVO DA PORTA CORTA-FOGO", svg)
        self.assertIn("BARRA ANTIPÂNICO (ABNT NBR 11785)", svg)
        self.assertIn("PCF-AUD-01", svg)


if __name__ == "__main__":
    unittest.main()
