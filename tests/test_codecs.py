"""Testes do módulo codecs (JSON canônico RFC 8259 sem float)."""

import json
import unittest
from fractions import Fraction

from pcf_nbr11742.calculator import dimensionar_projeto_portas
from pcf_nbr11742.codecs import (
    _para_fracao,
    _rejeitar_chaves_duplicadas,
    _rejeitar_float,
    _verificar_profundidade,
    carregar_projeto_portas_json,
    exportar_resultado_json,
)
from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosPorta,
    DadosProjetoPortas,
    TipoFolhaPorta,
)


class TestCodecs(unittest.TestCase):
    """Testes de conformidade e integridade do parser/serializer JSON canônico."""

    def test_para_fracao(self) -> None:
        self.assertEqual(_para_fracao(10), Fraction(10, 1))
        self.assertEqual(_para_fracao("2.5"), Fraction(5, 2))
        self.assertEqual(_para_fracao(Fraction(3, 4)), Fraction(3, 4))
        with self.assertRaises(ValueError):
            _para_fracao(2.5)  # type: ignore[arg-type]

    def test_rejeitar_float(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _rejeitar_float("12.5")
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeitar_chaves_duplicadas(self) -> None:
        pares_validos = [("a", 1), ("b", 2)]
        self.assertEqual(_rejeitar_chaves_duplicadas(pares_validos), {"a": 1, "b": 2})

        pares_duplicados = [("a", 1), ("a", 2)]
        with self.assertRaises(ValueError) as ctx:
            _rejeitar_chaves_duplicadas(pares_duplicados)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_verificar_profundidade(self) -> None:
        obj_ok: dict = {"a": {"b": {"c": [1, 2, 3]}}}
        _verificar_profundidade(obj_ok, profundidade=1, limite=5)

        profundo: dict = {"k": 1}
        for _ in range(35):
            profundo = {"k": profundo}
        with self.assertRaises(ValueError) as ctx:
            _verificar_profundidade(profundo, profundidade=1, limite=32)
        self.assertIn("Profundidade", str(ctx.exception))

    def test_carregar_json_valido(self) -> None:
        json_txt = """{
            "nome_edificacao": "Torre Beta",
            "responsavel_tecnico": "Eng. Lofrano",
            "portas": [
                {
                    "identificacao": "PCF-01",
                    "ambiente": "escada_enclausurada_protegida",
                    "tipo_folha": "folha_unica",
                    "classe_especificada": "P-60",
                    "largura_vao_livre_m": "0.90",
                    "altura_vao_livre_m": "2.10",
                    "populacao_atendida": 50
                }
            ]
        }"""
        proj = carregar_projeto_portas_json(json_txt)
        self.assertEqual(proj.nome_edificacao, "Torre Beta")
        self.assertEqual(len(proj.portas), 1)
        self.assertEqual(proj.portas[0].classe_especificada, ClasseResistenciaFogo.P60)
        self.assertEqual(proj.portas[0].largura_vao_livre_m, Fraction(9, 10))

    def test_rejeitar_bom(self) -> None:
        json_com_bom = "\ufeff" + '{"nome_edificacao": "Teste"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_portas_json(json_com_bom)
        self.assertIn("Byte Order Mark", str(ctx.exception))

    def test_rejeitar_float_no_json(self) -> None:
        json_com_float = '{"nome_edificacao": "Teste", "largura": 1.25}'
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_portas_json(json_com_float)
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeitar_chave_duplicada_no_json(self) -> None:
        json_com_duplicata = '{"nome_edificacao": "A", "nome_edificacao": "B"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_portas_json(json_com_duplicata)
        self.assertIn("Chave duplicada", str(ctx.exception))

    def test_rejeitar_estrutura_invalida(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_portas_json("[1, 2, 3]")
        self.assertIn("deve ser um objeto dicionário", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_portas_json('{"portas": "invalido"}')
        self.assertIn("portas' deve ser uma lista", str(ctx.exception))

    def test_exportar_resultado_json(self) -> None:
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
        res = dimensionar_projeto_portas(proj)
        json_out = exportar_resultado_json(res)
        dados = json.loads(json_out)
        self.assertEqual(dados["nome_edificacao"], "Torre Alpha")
        self.assertEqual(dados["total_portas"], 1)
        self.assertEqual(len(dados["portas"]), 1)
        self.assertEqual(dados["portas"][0]["classe_especificada"], "P-60")


if __name__ == "__main__":
    unittest.main()
