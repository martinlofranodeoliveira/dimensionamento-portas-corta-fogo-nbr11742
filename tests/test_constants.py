"""Testes das constantes e parâmetros normativos da NBR 11742 e NBR 11785."""

import unittest
from fractions import Fraction

from pcf_nbr11742.constants import (
    ALTURA_MAXIMA_BARRA_M,
    ALTURA_MINIMA_BARRA_M,
    ALTURA_NOMINAL_BARRA_M,
    ALTURA_PADRAO_VAO_LIVRE_M,
    CAPACIDADE_ESCOAMENTO_PORTA_UP,
    FOLGA_MAX_BATENTE_LATERAIS_MM,
    FOLGA_MAX_BATENTE_SUPERIOR_MM,
    FOLGA_MAX_ENTRE_FOLHAS_MM,
    FOLGA_MAX_PISO_ACABADO_MM,
    FORCA_MAXIMA_ABERTURA_BARRA_N,
    FRACAO_MINIMA_COMPRIMENTO_BARRA,
    LARGURA_UNIDADE_PASSAGEM_M,
    POPULACAO_GATILHO_BARRA_GERAL,
    POPULACAO_GATILHO_BARRA_REUNIAO,
    TEMPO_RESISTENCIA_P120_MIN,
    TEMPO_RESISTENCIA_P30_MIN,
    TEMPO_RESISTENCIA_P60_MIN,
    TEMPO_RESISTENCIA_P90_MIN,
    VAO_LIVRE_MINIMO_FOLHA_UNICA_M,
    VAO_LIVRE_MINIMO_HOSPITAIS_M,
)


class TestConstants(unittest.TestCase):
    """Testes de conformidade e integridade das constantes regulamentares."""

    def test_unidade_passagem_e_capacidade(self) -> None:
        self.assertEqual(LARGURA_UNIDADE_PASSAGEM_M, Fraction(55, 100))
        self.assertEqual(CAPACIDADE_ESCOAMENTO_PORTA_UP, 100)

    def test_tempos_resistencia_ao_fogo(self) -> None:
        self.assertEqual(TEMPO_RESISTENCIA_P30_MIN, 30)
        self.assertEqual(TEMPO_RESISTENCIA_P60_MIN, 60)
        self.assertEqual(TEMPO_RESISTENCIA_P90_MIN, 90)
        self.assertEqual(TEMPO_RESISTENCIA_P120_MIN, 120)

    def test_folgas_dimensionais_maximas(self) -> None:
        self.assertEqual(FOLGA_MAX_BATENTE_SUPERIOR_MM, Fraction(3, 1))
        self.assertEqual(FOLGA_MAX_BATENTE_LATERAIS_MM, Fraction(3, 1))
        self.assertEqual(FOLGA_MAX_ENTRE_FOLHAS_MM, Fraction(3, 1))
        self.assertEqual(FOLGA_MAX_PISO_ACABADO_MM, Fraction(10, 1))

    def test_parametros_barra_antipanico(self) -> None:
        self.assertEqual(ALTURA_MINIMA_BARRA_M, Fraction(90, 100))
        self.assertEqual(ALTURA_MAXIMA_BARRA_M, Fraction(110, 100))
        self.assertEqual(ALTURA_NOMINAL_BARRA_M, Fraction(1, 1))
        self.assertEqual(FRACAO_MINIMA_COMPRIMENTO_BARRA, Fraction(6, 10))
        self.assertEqual(FORCA_MAXIMA_ABERTURA_BARRA_N, 150)
        self.assertEqual(POPULACAO_GATILHO_BARRA_REUNIAO, 100)
        self.assertEqual(POPULACAO_GATILHO_BARRA_GERAL, 200)

    def test_vaos_livres_regulamentares(self) -> None:
        self.assertEqual(VAO_LIVRE_MINIMO_FOLHA_UNICA_M, Fraction(80, 100))
        self.assertEqual(VAO_LIVRE_MINIMO_HOSPITAIS_M, Fraction(220, 100))
        self.assertEqual(ALTURA_PADRAO_VAO_LIVRE_M, Fraction(210, 100))


if __name__ == "__main__":
    unittest.main()
