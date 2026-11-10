"""Testes das dataclasses e enums do modelo de dados."""

import unittest
from fractions import Fraction

from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosBarraAntipanico,
    DadosFolgasInstalacao,
    DadosPorta,
    DadosProjetoPortas,
    TipoFolhaPorta,
)


class TestModels(unittest.TestCase):
    """Testes de integridade e validação de limites de dataclasses."""

    def test_enums_valores(self) -> None:
        self.assertEqual(ClasseResistenciaFogo.P30.value, "P-30")
        self.assertEqual(ClasseResistenciaFogo.P60.value, "P-60")
        self.assertEqual(ClasseResistenciaFogo.P90.value, "P-90")
        self.assertEqual(ClasseResistenciaFogo.P120.value, "P-120")

        self.assertEqual(TipoFolhaPorta.UNICA.value, "folha_unica")
        self.assertEqual(TipoFolhaPorta.DUPLA.value, "folha_dupla")

        self.assertEqual(AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA.value, "escada_enclausurada_protegida")
        self.assertEqual(AmbienteInstalacao.SUBESTACAO_SALA_ELETRICA.value, "subestacao_sala_eletrica")

    def test_dados_folgas_valido_e_invalido(self) -> None:
        folgas_ok = DadosFolgasInstalacao(
            folga_superior_mm=Fraction(2, 1),
            folga_lateral_esquerda_mm=Fraction(25, 10),
            folga_lateral_direita_mm=Fraction(25, 10),
            folga_inferior_piso_mm=Fraction(8, 1),
            folga_entre_folhas_mm=Fraction(2, 1),
        )
        self.assertEqual(folgas_ok.folga_superior_mm, Fraction(2, 1))

        with self.assertRaises(ValueError):
            DadosFolgasInstalacao(
                folga_superior_mm=Fraction(-1, 1),
                folga_lateral_esquerda_mm=Fraction(2, 1),
                folga_lateral_direita_mm=Fraction(2, 1),
                folga_inferior_piso_mm=Fraction(8, 1),
            )

        with self.assertRaises(ValueError):
            DadosFolgasInstalacao(
                folga_superior_mm=Fraction(2, 1),
                folga_lateral_esquerda_mm=Fraction(2, 1),
                folga_lateral_direita_mm=Fraction(2, 1),
                folga_inferior_piso_mm=Fraction(-5, 1),
            )

    def test_dados_barra_valido_e_invalido(self) -> None:
        barra_ok = DadosBarraAntipanico(
            instalada=True,
            altura_instalacao_m=Fraction(100, 100),
            comprimento_barra_m=Fraction(65, 100),
            forca_operacao_n=120,
        )
        self.assertTrue(barra_ok.instalada)

        with self.assertRaises(ValueError):
            DadosBarraAntipanico(
                instalada=True,
                altura_instalacao_m=Fraction(-1, 1),
            )

        with self.assertRaises(ValueError):
            DadosBarraAntipanico(
                instalada=True,
                forca_operacao_n=-10,
            )

    def test_dados_porta_valido_e_invalido(self) -> None:
        porta_ok = DadosPorta(
            identificacao="PCF-01",
            ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA,
            tipo_folha=TipoFolhaPorta.UNICA,
            classe_especificada=ClasseResistenciaFogo.P60,
            largura_vao_livre_m=Fraction(90, 100),
            altura_vao_livre_m=Fraction(210, 100),
            populacao_atendida=60,
        )
        self.assertEqual(porta_ok.identificacao, "PCF-01")

        with self.assertRaises(ValueError):
            DadosPorta(
                identificacao="  ",
                ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA,
                tipo_folha=TipoFolhaPorta.UNICA,
                classe_especificada=ClasseResistenciaFogo.P60,
                largura_vao_livre_m=Fraction(90, 100),
                altura_vao_livre_m=Fraction(210, 100),
                populacao_atendida=60,
            )

        with self.assertRaises(ValueError):
            DadosPorta(
                identificacao="PCF-02",
                ambiente=AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA,
                tipo_folha=TipoFolhaPorta.UNICA,
                classe_especificada=ClasseResistenciaFogo.P60,
                largura_vao_livre_m=Fraction(0, 1),
                altura_vao_livre_m=Fraction(210, 100),
                populacao_atendida=60,
            )

    def test_dados_projeto_valido_e_invalido(self) -> None:
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
            nome_edificacao="Torre Alpha",
            responsavel_tecnico="Eng. Lofrano",
            portas=(porta,),
        )
        self.assertEqual(proj.nome_edificacao, "Torre Alpha")

        with self.assertRaises(ValueError):
            DadosProjetoPortas(
                nome_edificacao=" ",
                responsavel_tecnico="Eng. Lofrano",
                portas=(porta,),
            )

        with self.assertRaises(ValueError):
            DadosProjetoPortas(
                nome_edificacao="Torre Alpha",
                responsavel_tecnico="Eng. Lofrano",
                portas=(),
            )


if __name__ == "__main__":
    unittest.main()
