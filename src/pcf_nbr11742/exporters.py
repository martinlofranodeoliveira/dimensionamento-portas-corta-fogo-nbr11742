"""Exportadores técnicos: memorial descritivo, CSV sanitizado e ZIP determinístico."""

import csv
import io
import os
import zipfile
from fractions import Fraction
from typing import Optional

from pcf_nbr11742.codecs import exportar_resultado_json
from pcf_nbr11742.models import ResultadoDimensionamento


def _fmt(val: Fraction, casas: int = 2) -> str:
    """Formata fração para string decimal com número fixo de casas sem IEEE float."""
    num = val.numerator
    den = val.denominator
    if den == 1:
        return f"{num}.0" if casas > 0 else str(num)
    inteiro = num // den
    resto = abs(num % den)
    fator = 10**casas
    frac_parte = (resto * fator + den // 2) // den
    return f"{inteiro}.{frac_parte:0{casas}d}"


def _sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings contra injeção de fórmulas de planilhas."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_relatorio_texto(res: ResultadoDimensionamento) -> str:
    """Gera memorial descritivo técnico detalhado de portas corta-fogo NBR 11742 e NBR 11785."""
    linhas: list[str] = []
    w = 80
    linhas.append("=" * w)
    linhas.append("    LOFRANO TECNOLOGIA - ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO")
    linhas.append("    PORTAS CORTA-FOGO E BARRAS ANTIPÂNICO - ABNT NBR 11742 / NBR 11785")
    linhas.append("=" * w)
    linhas.append(f"Edificação:           {res.nome_edificacao}")
    linhas.append(f"Responsável Técnico:  {res.responsavel_tecnico}")
    linhas.append(f"Total de Portas:      {res.total_portas}")
    linhas.append(f"Portas Conformes:     {res.portas_conformes}")
    linhas.append(f"Portas Inconformes:   {res.portas_inconformes}")
    status_glo = "CONFORME" if res.sistema_totalmente_conforme else "NÃO CONFORME"
    linhas.append(f"Status Global:        {status_glo}")
    linhas.append("-" * w)

    linhas.append("1. ESPECIFICAÇÃO E AUDITORIA DETALHADA POR PORTA")
    for idx, p in enumerate(res.portas, start=1):
        status_p = "CONFORME" if p.conforme_geral else "NÃO CONFORME"
        linhas.append(f"  [{idx}] Porta: {p.identificacao} [{status_p}]")
        linhas.append(f"      - Ambiente: {p.ambiente.value} | Tipo: {p.tipo_folha.value}")
        status_c = "CONFORME" if p.conforme_classe_resistencia else "NÃO CONFORME"
        linhas.append(
            f"      - Resistência ao Fogo: {p.classe_especificada.value} (Exigência Mínima: {p.classe_minima_normativa.value}) [{status_c}]"
        )
        linhas.append(
            f"      - Vão Livre: {_fmt(p.largura_vao_livre_m, 2)} m x {_fmt(p.altura_vao_livre_m, 2)} m"
        )
        status_fl = "CONFORME" if p.conforme_capacidade_fluxo else "NÃO CONFORME"
        linhas.append(
            f"      - Capacidade de Fluxo: {p.unidades_passagem_fornecidas} UP ({p.capacidade_escoamento_pessoas} pess) | População: {p.populacao_atendida} pess [{status_fl}]"
        )
        linhas.append(f"      - Mola Aérea Hidráulica: {p.mola_aerea_classe_en}")

        if p.exige_seletor_fechamento:
            status_sel = "CONFORME" if p.conforme_seletor else "NÃO CONFORME"
            linhas.append(f"      - Seletor de Fechamento (Folha Dupla): {status_sel}")

        # Folgas
        if p.resultado_folgas is not None:
            status_fg = "CONFORME" if p.resultado_folgas.conforme_geral else "NÃO CONFORME"
            linhas.append(f"      - Folgas Perimetrais e Piso: [{status_fg}]")
            for det in p.resultado_folgas.detalhes:
                linhas.append(f"          * {det}")

        # Barra antipânico
        rb = p.resultado_barra
        status_bar = "CONFORME" if rb.conforme_geral else "NÃO CONFORME"
        bar_info = "Instalada" if rb.instalada else "Não Instalada"
        linhas.append(f"      - Barra Antipânico: {bar_info} (Obrigatória: {'SIM' if rb.obrigatoria else 'NÃO'}) [{status_bar}]")
        for det in rb.detalhes:
            linhas.append(f"          * {det}")

        if p.alertas:
            for alerta in p.alertas:
                linhas.append(f"      [ALERTA] {alerta}")
        linhas.append("-" * w)

    if res.alertas_gerais:
        linhas.append("2. RESUMO DE ALERTAS E INCONFORMIDADES REGISTRADAS")
        for alerta in res.alertas_gerais:
            linhas.append(f"  [ALERTA] {alerta}")
        linhas.append("-" * w)

    linhas.append("3. DIRETRIZES TÉCNICAS E RECOMENDAÇÕES NORMATIVAS")
    for rec in res.recomendacoes:
        linhas.append(f"  * {rec}")
    linhas.append("=" * w)
    linhas.append("Emitido via Lofrano Tecnologia - Conforme ABNT NBR 11742 / NBR 11785")
    linhas.append("=" * w)

    return "\n".join(linhas)


def gerar_csv_sanitizado(res: ResultadoDimensionamento) -> str:
    """Gera resumo tabular estruturado em CSV sanitizado contra injeção de fórmulas."""
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";", lineterminator="\n")

    writer.writerow([
        _sanitizar_campo_csv("identificacao"),
        _sanitizar_campo_csv("ambiente"),
        _sanitizar_campo_csv("tipo_folha"),
        _sanitizar_campo_csv("classe_especificada"),
        _sanitizar_campo_csv("classe_minima"),
        _sanitizar_campo_csv("conforme_classe"),
        _sanitizar_campo_csv("largura_vao_m"),
        _sanitizar_campo_csv("altura_vao_m"),
        _sanitizar_campo_csv("up_fornecido"),
        _sanitizar_campo_csv("capacidade_pessoas"),
        _sanitizar_campo_csv("populacao_atendida"),
        _sanitizar_campo_csv("conforme_fluxo"),
        _sanitizar_campo_csv("mola_en"),
        _sanitizar_campo_csv("barra_obrigatoria"),
        _sanitizar_campo_csv("barra_instalada"),
        _sanitizar_campo_csv("conforme_barra"),
        _sanitizar_campo_csv("conforme_geral"),
    ])

    for p in res.portas:
        writer.writerow([
            _sanitizar_campo_csv(p.identificacao),
            p.ambiente.value,
            p.tipo_folha.value,
            p.classe_especificada.value,
            p.classe_minima_normativa.value,
            "SIM" if p.conforme_classe_resistencia else "NAO",
            _fmt(p.largura_vao_livre_m, 2),
            _fmt(p.altura_vao_livre_m, 2),
            str(p.unidades_passagem_fornecidas),
            str(p.capacidade_escoamento_pessoas),
            str(p.populacao_atendida),
            "SIM" if p.conforme_capacidade_fluxo else "NAO",
            _sanitizar_campo_csv(p.mola_aerea_classe_en),
            "SIM" if p.resultado_barra.obrigatoria else "NAO",
            "SIM" if p.resultado_barra.instalada else "NAO",
            "SIM" if p.resultado_barra.conforme_geral else "NAO",
            "SIM" if p.conforme_geral else "NAO",
        ])

    return saida.getvalue()


def gerar_pacote_zip(
    res: ResultadoDimensionamento,
    caminho_zip: str,
    svg_conteudo: Optional[str] = None,
) -> None:
    """Gera pacote determinístico ZIP com O_EXCL, evitando sobrescrita acidental."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    fd = os.open(caminho_zip, flags, 0o644)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    try:
        with open(fd, "wb", closefd=True) as f_out:
            with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # 1. Memorial descritivo em texto
                txt = gerar_relatorio_texto(res).encode("utf-8")
                zi_txt = zipfile.ZipInfo(filename="memorial_descritivo.txt", date_time=fixed_time)
                zf.writestr(zi_txt, txt)

                # 2. Dados em JSON canônico
                js = exportar_resultado_json(res).encode("utf-8")
                zi_js = zipfile.ZipInfo(filename="dados_portas.json", date_time=fixed_time)
                zf.writestr(zi_js, js)

                # 3. Resumo tabular em CSV
                csv_data = gerar_csv_sanitizado(res).encode("utf-8")
                zi_csv = zipfile.ZipInfo(filename="resumo_portas.csv", date_time=fixed_time)
                zf.writestr(zi_csv, csv_data)

                # 4. Diagrama vetorial SVG se fornecido
                if svg_conteudo is not None:
                    zi_svg = zipfile.ZipInfo(filename="painel_esquematico.svg", date_time=fixed_time)
                    zf.writestr(zi_svg, svg_conteudo.encode("utf-8"))
    except Exception:
        if os.path.exists(caminho_zip):
            try:
                os.remove(caminho_zip)
            except OSError:
                pass
        raise
