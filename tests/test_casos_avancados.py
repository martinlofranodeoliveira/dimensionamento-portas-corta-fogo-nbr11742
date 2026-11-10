"""Testes de casos avançados e situações limite da NBR 11742 e NBR 11785."""

import unittest
from fractions import Fraction

from pcf_nbr11742.calculator import (
    avaliar_barra_antipanico,
    avaliar_folgas_instalacao,
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


class TestCasosAvancados(unittest.TestCase):
    """Bateria de testes para validação de cenários complexos e bordas normativas."""

    def test_subestacao_eletrica_exige_p120(self) -> None:
        """Subestação elétrica com P-60 ou P-90 deve ser reprovada por exigir P-120."""
        porta_ruim = DadosPorta(
            identificacao="PCF-SUB-RUIM",
            ambiente=AmbienteInstalacao.SUBESTACAO_SALA_ELETRICA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P90,  # Insuficiente para subestação
            largura_vao_livre_m=Fraction(100, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=10,
        )
        res_ruim = dimensionar_porta(porta_ruim)
        self.assertFalse(res_ruim.conforme_classe_resistencia)
        self.assertFalse(res_ruim.conforme_geral)
        self.assertEqual(res_ruim.classe_minima_normativa, ClasseResistenciaFogo.P120)

        porta_boa = DadosPorta(
            identificacao="PCF-SUB-BOA",
            ambiente=AmbienteInstalacao.SUBESTACAO_SALA_ELETRICA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P120,
            largura_vao_livre_m=Fraction(100, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=10,
        )
        res_boa = dimensionar_porta(porta_boa)
        self.assertTrue(res_boa.conforme_classe_resistencia)
        self.assertTrue(res_boa.conforme_geral)

    def test_central_glp_exige_p120(self) -> None:
        """Centrais de GLP exigem estritamente P-120."""
        porta = DadosPorta(
            identificacao="PCF-GLP",
            ambiente=AmbienteInstalacao.CENTRAL_GLP_INFLAMAVEIS,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P120,
            largura_vao_livre_m=Fraction(100, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=5,
        )
        res = dimensionar_porta(porta)
        self.assertTrue(res.conforme_classe_resistencia)
        self.assertEqual(res.classe_minima_normativa, ClasseResistenciaFogo.P120)

    def test_escada_fumaca_exige_p90(self) -> None:
        """Escadas à prova de fumaça e antecâmaras exigem no mínimo P-90."""
        porta = DadosPorta(
            identificacao="PCF-PF",
            ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_FUMACA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P90,
            largura_vao_livre_m=Fraction(100, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=60,
        )
        res = dimensionar_porta(porta)
        self.assertTrue(res.conforme_classe_resistencia)
        self.assertEqual(res.classe_minima_normativa, ClasseResistenciaFogo.P90)

    def test_folha_dupla_sem_seletor_reprovada(self) -> None:
        """Porta de folha dupla sem seletor de fechamento sequencial deve ser reprovada."""
        porta = DadosPorta(
            identificacao="PCF-D-SEM-SELETOR",
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            tipo_folha=TipoFolhaPorta.DUPLA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(200, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=80,
            possui_seletor_fechamento=False,  # Violação
        )
        res = dimensionar_porta(porta)
        self.assertTrue(res.exige_seletor_fechamento)
        self.assertFalse(res.conforme_seletor)
        self.assertFalse(res.conforme_geral)
        self.assertTrue(any("seletor" in a.lower() for a in res.alertas))

    def test_folha_dupla_com_seletor_aprovada(self) -> None:
        """Porta de folha dupla com seletor de fechamento sequencial é conforme."""
        porta = DadosPorta(
            identificacao="PCF-D-COM-SELETOR",
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            tipo_folha=TipoFolhaPorta.DUPLA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(200, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=80,
            possui_seletor_fechamento=True,
        )
        res = dimensionar_porta(porta)
        self.assertTrue(res.conforme_seletor)
        self.assertTrue(res.conforme_geral)

    def test_barra_antipanico_altura_fora_da_faixa(self) -> None:
        """Altura fora de 0,90m a 1,10m deve ser reprovada pela NBR 11785."""
        # Altura baixa (ex: 0.85m)
        barra_baixa = DadosBarraAntipanico(
            instalada=True,
            altura_instalacao_m=Fraction(85, 100),
            comprimento_barra_m=Fraction(65, 100),
            forca_operacao_n=100,
        )
        res_baixa = avaliar_barra_antipanico(
            barra_baixa,
            populacao=120,
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            largura_folha_m=Fraction(1, 1),
        )
        self.assertFalse(res_baixa.conforme_altura)
        self.assertFalse(res_baixa.conforme_geral)

        # Altura alta (ex: 1.15m)
        barra_alta = DadosBarraAntipanico(
            instalada=True,
            altura_instalacao_m=Fraction(115, 100),
            comprimento_barra_m=Fraction(65, 100),
            forca_operacao_n=100,
        )
        res_alta = avaliar_barra_antipanico(
            barra_alta,
            populacao=120,
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            largura_folha_m=Fraction(1, 1),
        )
        self.assertFalse(res_alta.conforme_altura)
        self.assertFalse(res_alta.conforme_geral)

    def test_barra_antipanico_comprimento_insuficiente(self) -> None:
        """Comprimento inferior a 60% da folha é reprovado."""
        # Folha de 1.00m exige mínimo de 0.60m de barra
        barra_curta = DadosBarraAntipanico(
            instalada=True,
            altura_instalacao_m=Fraction(100, 100),
            comprimento_barra_m=Fraction(50, 100),  # 50 cm < 60 cm
            forca_operacao_n=120,
        )
        res = avaliar_barra_antipanico(
            barra_curta,
            populacao=120,
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            largura_folha_m=Fraction(1, 1),
        )
        self.assertFalse(res.conforme_comprimento)
        self.assertFalse(res.conforme_geral)

    def test_barra_antipanico_forca_excessiva(self) -> None:
        """Força de acionamento > 150 N é reprovada."""
        barra_dura = DadosBarraAntipanico(
            instalada=True,
            altura_instalacao_m=Fraction(100, 100),
            comprimento_barra_m=Fraction(65, 100),
            forca_operacao_n=180,  # > 150 N
        )
        res = avaliar_barra_antipanico(
            barra_dura,
            populacao=120,
            ambiente=AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO,
            largura_folha_m=Fraction(1, 1),
        )
        self.assertFalse(res.conforme_forca)
        self.assertFalse(res.conforme_geral)

    def test_folga_entre_folhas_duplas_inconforme(self) -> None:
        """Folga central entre folhas duplas > 3.0 mm é reprovada."""
        folgas = DadosFolgasInstalacao(
            folga_superior_mm=Fraction(2, 1),
            folga_lateral_esquerda_mm=Fraction(2, 1),
            folga_lateral_direita_mm=Fraction(2, 1),
            folga_inferior_piso_mm=Fraction(6, 1),
            folga_entre_folhas_mm=Fraction(45, 10),  # 4.5 mm > 3.0 mm
        )
        res = avaliar_folgas_instalacao(folgas, TipoFolhaPorta.DUPLA)
        self.assertFalse(res.conforme_entre_folhas)
        self.assertFalse(res.conforme_geral)

    def test_fluxo_insuficiente_populacao_maior_que_vão(self) -> None:
        """População de 250 pessoas em porta de 0.90m (1 UP = 100 pessoas) deve falhar."""
        porta = DadosPorta(
            identificacao="PCF-ESTREITA",
            ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(90, 100),  # 1 UP (100 pessoas)
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=250,  # Exige 3 UP
        )
        res = dimensionar_porta(porta)
        self.assertEqual(res.unidades_passagem_fornecidas, 1)
        self.assertEqual(res.capacidade_escoamento_pessoas, 100)
        self.assertFalse(res.conforme_capacidade_fluxo)
        self.assertFalse(res.conforme_geral)


if __name__ == "__main__":
    unittest.main()
