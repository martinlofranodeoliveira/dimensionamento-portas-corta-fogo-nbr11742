"""Testes das funções centrais de cálculo e dimensionamento."""

import unittest
from fractions import Fraction

from pcf_nbr11742.calculator import (
    _obter_minutos_classe,
    _teto_fracao,
    avaliar_barra_antipanico,
    avaliar_folgas_instalacao,
    comparar_classes_resistencia,
    determinar_classe_minima,
    determinar_classe_mola_en,
    dimensionar_porta,
    dimensionar_projeto_portas,
)
from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosBarraAntipanico,
    DadosFolgasInstalacao,
    DadosPorta,
    DadosProjetoPortas,
    TipoFolhaPorta,
)


class TestCalculator(unittest.TestCase):
    """Bateria de testes das regras normativas e lógicas de engenharia."""

    def test_teto_fracao(self) -> None:
        self.assertEqual(_teto_fracao(Fraction(10, 1)), 10)
        self.assertEqual(_teto_fracao(Fraction(101, 100)), 2)
        self.assertEqual(_teto_fracao(Fraction(200, 100)), 2)
        self.assertEqual(_teto_fracao(Fraction(201, 100)), 3)

    def test_determinar_classe_minima(self) -> None:
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.SUBESTACAO_SALA_ELETRICA),
            ClasseResistenciaFogo.P120,
        )
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.CENTRAL_GLP_INFLAMAVEIS),
            ClasseResistenciaFogo.P120,
        )
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.ESCADA_ENCLAUSURADA_FUMACA),
            ClasseResistenciaFogo.P90,
        )
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.ANTECAMARA_DUTO),
            ClasseResistenciaFogo.P90,
        )
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA),
            ClasseResistenciaFogo.P60,
        )
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO),
            ClasseResistenciaFogo.P60,
        )
        self.assertEqual(
            determinar_classe_minima(AmbienteInstalacao.CORREDOR_COMPARTIMENTACAO),
            ClasseResistenciaFogo.P30,
        )

    def test_comparar_classes_resistencia(self) -> None:
        self.assertTrue(comparar_classes_resistencia(ClasseResistenciaFogo.P120, ClasseResistenciaFogo.P60))
        self.assertTrue(comparar_classes_resistencia(ClasseResistenciaFogo.P90, ClasseResistenciaFogo.P90))
        self.assertFalse(comparar_classes_resistencia(ClasseResistenciaFogo.P60, ClasseResistenciaFogo.P90))
        self.assertFalse(comparar_classes_resistencia(ClasseResistenciaFogo.P30, ClasseResistenciaFogo.P60))

    def test_determinar_classe_mola_en(self) -> None:
        self.assertIn("EN 2", determinar_classe_mola_en(Fraction(80, 100)))
        self.assertIn("EN 3", determinar_classe_mola_en(Fraction(90, 100)))
        self.assertIn("EN 4", determinar_classe_mola_en(Fraction(100, 100)))
        self.assertIn("EN 5", determinar_classe_mola_en(Fraction(120, 100)))
        self.assertIn("EN 6", determinar_classe_mola_en(Fraction(130, 100)))

    def test_avaliar_folgas_conformes(self) -> None:
        folgas = DadosFolgasInstalacao(
            folga_superior_mm=Fraction(25, 10),
            folga_lateral_esquerda_mm=Fraction(25, 10),
            folga_lateral_direita_mm=Fraction(25, 10),
            folga_inferior_piso_mm=Fraction(80, 10),
        )
        res = avaliar_folgas_instalacao(folgas, TipoFolhaPorta.UNICA)
        self.assertTrue(res.conforme_geral)
        self.assertEqual(len(res.detalhes), 0)

    def test_avaliar_folgas_inconformes(self) -> None:
        folgas_ruins = DadosFolgasInstalacao(
            folga_superior_mm=Fraction(35, 10),  # > 3.0 mm
            folga_lateral_esquerda_mm=Fraction(25, 10),
            folga_lateral_direita_mm=Fraction(35, 10),  # > 3.0 mm
            folga_inferior_piso_mm=Fraction(120, 10),  # > 10.0 mm
        )
        res = avaliar_folgas_instalacao(folgas_ruins, TipoFolhaPorta.UNICA)
        self.assertFalse(res.conforme_geral)
        self.assertFalse(res.conforme_superior)
        self.assertFalse(res.conforme_laterais)
        self.assertFalse(res.conforme_piso)

    def test_avaliar_barra_antipanico_obrigatoria_e_presente(self) -> None:
        barra = DadosBarraAntipanico(
            instalada=True,
            altura_instalacao_m=Fraction(100, 100),
            comprimento_barra_m=Fraction(65, 100),  # 65% de 1.00m
            forca_operacao_n=120,  # <= 150N
        )
        res = avaliar_barra_antipanico(
            barra,
            populacao=150,
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            largura_folha_m=Fraction(1, 1),
        )
        self.assertTrue(res.obrigatoria)
        self.assertTrue(res.instalada)
        self.assertTrue(res.conforme_geral)

    def test_avaliar_barra_antipanico_obrigatoria_mas_ausente(self) -> None:
        res = avaliar_barra_antipanico(
            dados_barra=None,
            populacao=250,  # Geral >= 200 obriga barra
            ambiente=AmbienteInstalacao.CORREDOR_COMPARTIMENTACAO,
            largura_folha_m=Fraction(90, 100),
        )
        self.assertTrue(res.obrigatoria)
        self.assertFalse(res.instalada)
        self.assertFalse(res.conforme_geral)

    def test_dimensionar_porta_simples_conforme(self) -> None:
        porta = DadosPorta(
            identificacao="PCF-ESC-01",
            ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(90, 100),  # 1 UP (100 pess)
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=80,
            dados_folgas=DadosFolgasInstalacao(
                folga_superior_mm=Fraction(2, 1),
                folga_lateral_esquerda_mm=Fraction(2, 1),
                folga_lateral_direita_mm=Fraction(2, 1),
                folga_inferior_piso_mm=Fraction(7, 1),
            ),
        )
        res = dimensionar_porta(porta)
        self.assertTrue(res.conforme_geral)
        self.assertTrue(res.conforme_classe_resistencia)
        self.assertTrue(res.conforme_capacidade_fluxo)

    def test_dimensionar_projeto_portas(self) -> None:
        porta = DadosPorta(
            identificacao="PCF-01",
            ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(90, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=60,
        )
        proj = DadosProjetoPortas(
            nome_edificacao="Hospital Central",
            responsavel_tecnico="Eng. Lofrano",
            portas=(porta,),
        )
        res_proj = dimensionar_projeto_portas(proj)
        self.assertEqual(res_proj.total_portas, 1)
        self.assertEqual(res_proj.portas_conformes, 1)
        self.assertTrue(res_proj.sistema_totalmente_conforme)


if __name__ == "__main__":
    unittest.main()
