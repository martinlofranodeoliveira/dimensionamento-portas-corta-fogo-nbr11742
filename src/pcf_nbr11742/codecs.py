"""Codec JSON canônico RFC 8259 para portas corta-fogo NBR 11742 e NBR 11785."""

import json
from enum import Enum
from fractions import Fraction
from typing import Any

from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosBarraAntipanico,
    DadosFolgasInstalacao,
    DadosPorta,
    DadosProjetoPortas,
    ResultadoDimensionamento,
    TipoFolhaPorta,
)


def _rejeitar_float(valor: str) -> None:
    raise ValueError(f"Ponto flutuante ({valor}) não é permitido. Utilize inteiros ou strings decimais exatas.")


def _rejeitar_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada encontrada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def _verificar_profundidade(obj: Any, profundidade: int = 1, limite: int = 32) -> None:
    if profundidade > limite:
        raise ValueError(f"Profundidade da estrutura JSON ({profundidade}) excede o limite máximo permitido de {limite}.")
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, profundidade + 1, limite)
    elif isinstance(obj, list):
        for elem in obj:
            _verificar_profundidade(elem, profundidade + 1, limite)


def _para_fracao(val: Any) -> Fraction:
    if isinstance(val, (int, str)):
        return Fraction(val)
    if isinstance(val, Fraction):
        return val
    raise ValueError(f"Tipo inválido para conversão fracionária: {type(val).__name__} ({val})")


def carregar_projeto_portas_json(conteudo: str) -> DadosProjetoPortas:
    """Carrega e valida a especificação do projeto de portas corta-fogo em JSON canônico sem float."""
    if conteudo.startswith(("\ufeff", "\xef\xbb\xbf")):
        raise ValueError("Byte Order Mark (BOM) detectado. O arquivo deve ser codificado estritamente em UTF-8 puro.")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_rejeitar_chaves_duplicadas,
            parse_float=_rejeitar_float,
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"Erro de decodificação JSON: {err}") from err

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise ValueError("O JSON raiz deve ser um objeto dicionário.")

    nome_edificacao = str(dados.get("nome_edificacao", "Edificação"))
    responsavel = str(dados.get("responsavel_tecnico", "Engenharia Lofrano"))

    portas_raw = dados.get("portas", [])
    if not isinstance(portas_raw, list):
        raise ValueError("O campo 'portas' deve ser uma lista.")

    portas_parsed: list[DadosPorta] = []
    for idx, p_dict in enumerate(portas_raw):
        if not isinstance(p_dict, dict):
            raise ValueError(f"Elemento da porta no índice {idx} deve ser um dicionário.")

        identificacao = str(p_dict.get("identificacao", f"PCF-{idx + 1:02d}"))

        amb_str = str(p_dict.get("ambiente", "escada_enclausurada_protegida")).lower()
        try:
            ambiente = AmbienteInstalacao(amb_str)
        except ValueError:
            ambiente = AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA

        folha_str = str(p_dict.get("tipo_folha", "folha_unica")).lower()
        try:
            tipo_folha = TipoFolhaPorta(folha_str)
        except ValueError:
            tipo_folha = TipoFolhaPorta.UNICA

        classe_str = str(p_dict.get("classe_especificada", "P-60")).upper()
        try:
            classe_especificada = ClasseResistenciaFogo(classe_str)
        except ValueError:
            classe_especificada = ClasseResistenciaFogo.P60

        largura_m = _para_fracao(p_dict.get("largura_vao_livre_m", "0.90"))
        altura_m = _para_fracao(p_dict.get("altura_vao_livre_m", "2.10"))
        populacao = int(p_dict.get("populacao_atendida", 50))
        seletor = bool(p_dict.get("possui_seletor_fechamento", False))
        eletroima = bool(p_dict.get("possui_eletroima_retencao", False))

        # Folgas
        folgas_obj: DadosFolgasInstalacao | None = None
        folgas_raw = p_dict.get("dados_folgas")
        if isinstance(folgas_raw, dict):
            f_sup = _para_fracao(folgas_raw.get("folga_superior_mm", "2.5"))
            f_esq = _para_fracao(folgas_raw.get("folga_lateral_esquerda_mm", "2.5"))
            f_dir = _para_fracao(folgas_raw.get("folga_lateral_direita_mm", "2.5"))
            f_piso = _para_fracao(folgas_raw.get("folga_inferior_piso_mm", "8.0"))
            f_entre = (
                _para_fracao(folgas_raw["folga_entre_folhas_mm"])
                if folgas_raw.get("folga_entre_folhas_mm") is not None
                else None
            )
            folgas_obj = DadosFolgasInstalacao(
                folga_superior_mm=f_sup,
                folga_lateral_esquerda_mm=f_esq,
                folga_lateral_direita_mm=f_dir,
                folga_inferior_piso_mm=f_piso,
                folga_entre_folhas_mm=f_entre,
            )

        # Barra antipânico
        barra_obj: DadosBarraAntipanico | None = None
        barra_raw = p_dict.get("dados_barra")
        if isinstance(barra_raw, dict):
            inst = bool(barra_raw.get("instalada", False))
            alt_b = (
                _para_fracao(barra_raw["altura_instalacao_m"])
                if barra_raw.get("altura_instalacao_m") is not None
                else None
            )
            comp_b = (
                _para_fracao(barra_raw["comprimento_barra_m"])
                if barra_raw.get("comprimento_barra_m") is not None
                else None
            )
            forca_b = (
                int(barra_raw["forca_operacao_n"])
                if barra_raw.get("forca_operacao_n") is not None
                else None
            )
            barra_obj = DadosBarraAntipanico(
                instalada=inst,
                altura_instalacao_m=alt_b,
                comprimento_barra_m=comp_b,
                forca_operacao_n=forca_b,
            )

        portas_parsed.append(
            DadosPorta(
                identificacao=identificacao,
                ambiente=ambiente,
                tipo_folha=tipo_folha,
                classe_especificada=classe_especificada,
                largura_vao_livre_m=largura_m,
                altura_vao_livre_m=altura_m,
                populacao_atendida=populacao,
                possui_seletor_fechamento=seletor,
                possui_eletroima_retencao=eletroima,
                dados_folgas=folgas_obj,
                dados_barra=barra_obj,
            )
        )

    return DadosProjetoPortas(
        nome_edificacao=nome_edificacao,
        responsavel_tecnico=responsavel,
        portas=tuple(portas_parsed),
    )


def _serializar_valor(val: Any) -> Any:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return val.numerator
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, tuple):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, dict):
        return {k: _serializar_valor(v) for k, v in val.items()}
    return val


def exportar_resultado_json(res: ResultadoDimensionamento) -> str:
    """Serializa o resultado em JSON canônico RFC 8259 determinístico."""
    dados: dict[str, Any] = {
        "normas": ["ABNT NBR 11742:2018", "ABNT NBR 11785:2018", "ABNT NBR 9077:2001"],
        "nome_edificacao": res.nome_edificacao,
        "responsavel_tecnico": res.responsavel_tecnico,
        "total_portas": res.total_portas,
        "portas_conformes": res.portas_conformes,
        "portas_inconformes": res.portas_inconformes,
        "sistema_totalmente_conforme": res.sistema_totalmente_conforme,
        "portas": [
            {
                "identificacao": p.identificacao,
                "ambiente": p.ambiente.value,
                "tipo_folha": p.tipo_folha.value,
                "classe_especificada": p.classe_especificada.value,
                "classe_minima_normativa": p.classe_minima_normativa.value,
                "conforme_classe_resistencia": p.conforme_classe_resistencia,
                "largura_vao_livre_m": _serializar_valor(p.largura_vao_livre_m),
                "altura_vao_livre_m": _serializar_valor(p.altura_vao_livre_m),
                "unidades_passagem_fornecidas": p.unidades_passagem_fornecidas,
                "capacidade_escoamento_pessoas": p.capacidade_escoamento_pessoas,
                "populacao_atendida": p.populacao_atendida,
                "conforme_capacidade_fluxo": p.conforme_capacidade_fluxo,
                "largura_minima_requerida_m": _serializar_valor(p.largura_minima_requerida_m),
                "conforme_largura_minima": p.conforme_largura_minima,
                "mola_aerea_classe_en": p.mola_aerea_classe_en,
                "exige_seletor_fechamento": p.exige_seletor_fechamento,
                "conforme_seletor": p.conforme_seletor,
                "folgas": {
                    "conforme_geral": p.resultado_folgas.conforme_geral,
                    "conforme_superior": p.resultado_folgas.conforme_superior,
                    "conforme_laterais": p.resultado_folgas.conforme_laterais,
                    "conforme_piso": p.resultado_folgas.conforme_piso,
                    "conforme_entre_folhas": p.resultado_folgas.conforme_entre_folhas,
                    "detalhes": list(p.resultado_folgas.detalhes),
                }
                if p.resultado_folgas
                else None,
                "barra_antipanico": {
                    "obrigatoria": p.resultado_barra.obrigatoria,
                    "instalada": p.resultado_barra.instalada,
                    "conforme_geral": p.resultado_barra.conforme_geral,
                    "conforme_presenca": p.resultado_barra.conforme_presenca,
                    "conforme_altura": p.resultado_barra.conforme_altura,
                    "conforme_comprimento": p.resultado_barra.conforme_comprimento,
                    "conforme_forca": p.resultado_barra.conforme_forca,
                    "comprimento_minimo_requerido_m": _serializar_valor(
                        p.resultado_barra.comprimento_minimo_requerido_m
                    ),
                    "detalhes": list(p.resultado_barra.detalhes),
                },
                "conforme_geral": p.conforme_geral,
                "alertas": list(p.alertas),
            }
            for p in res.portas
        ],
        "alertas_gerais": list(res.alertas_gerais),
        "recomendacoes": list(res.recomendacoes),
    }

    return json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True)
