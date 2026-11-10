"""Interface de Linha de Comando (CLI) para portas corta-fogo NBR 11742 e NBR 11785."""

import argparse
import sys
from typing import Sequence

from pcf_nbr11742 import __version__
from pcf_nbr11742.calculator import dimensionar_projeto_portas
from pcf_nbr11742.codecs import carregar_projeto_portas_json, exportar_resultado_json
from pcf_nbr11742.exporters import gerar_csv_sanitizado, gerar_pacote_zip, gerar_relatorio_texto
from pcf_nbr11742.svg_generator import gerar_painel_svg


def _comando_calcular(args: argparse.Namespace) -> int:
    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except Exception as err:
        print(f"Erro ao ler arquivo de entrada: {err}", file=sys.stderr)
        return 1

    try:
        dados = carregar_projeto_portas_json(conteudo)
    except Exception as err:
        print(f"Erro ao processar JSON: {err}", file=sys.stderr)
        return 1

    resultado = dimensionar_projeto_portas(dados)

    # Geração do pacote ZIP determinístico se solicitado
    if args.pacote_zip:
        try:
            svg_conteudo = gerar_painel_svg(resultado)
            gerar_pacote_zip(resultado, args.pacote_zip, svg_conteudo)
            print(f"[ZIP] Pacote determinístico gerado com sucesso em '{args.pacote_zip}'")
        except Exception as err:
            print(f"Erro ao gerar pacote ZIP: {err}", file=sys.stderr)
            return 1

    # Formatação da saída solicitada
    formato = args.formato.lower()
    if formato == "json":
        saida_str = exportar_resultado_json(resultado)
    elif formato == "csv":
        saida_str = gerar_csv_sanitizado(resultado)
    elif formato == "svg":
        saida_str = gerar_painel_svg(resultado)
    else:
        saida_str = gerar_relatorio_texto(resultado)

    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(saida_str)
            print(f"[OK] Saída ({formato}) salva com sucesso em '{args.saida}'")
        except Exception as err:
            print(f"Erro ao salvar arquivo de saída: {err}", file=sys.stderr)
            return 1
    else:
        print(saida_str)

    return 0


def _comando_catalogo(args: argparse.Namespace) -> int:
    print("=" * 80)
    print("    LOFRANO TECNOLOGIA - PARÂMETROS NORMATIVOS DA NBR 11742 / NBR 11785")
    print("=" * 80)
    print("1. CLASSES DE RESISTÊNCIA AO FOGO (NBR 11742:2018)")
    print("  - P-30  (>= 30 min):  Corredores de compartimentação secundários")
    print("  - P-60  (>= 60 min):  Escadas enclausuradas protegidas (EP), reunião público")
    print("  - P-90  (>= 90 min):  Escadas enclausuradas à prova de fumaça (PF), antecâmaras")
    print("  - P-120 (>= 120 min): Subestações elétricas, salas de geradores, depósitos GLP")
    print("-" * 80)
    print("2. FOLGAS MÁXIMAS DE MONTAGEM E INSTALAÇÃO (Item 5.2.3)")
    print("  - Folga superior entre folha e batente:       máximo 3,0 mm")
    print("  - Folgas laterais entre folha e batente:      máximo 3,0 mm")
    print("  - Folga inferior em relação ao piso acabado:  máximo 10,0 mm")
    print("  - Folga central de encontro em folha dupla:   máximo 3,0 mm")
    print("-" * 80)
    print("3. BARRAS ANTIPÂNICO (ABNT NBR 11785:2018)")
    print("  - Obrigatoriedade: locais de reunião (F) com lotação >= 100 pessoas")
    print("  - Demais ocupações: rotas de fuga com lotação >= 200 pessoas")
    print("  - Altura regulamentar de instalação: entre 0,90 m e 1,10 m (nominal 1,00 m)")
    print("  - Comprimento da barra móvel: no mínimo 60% da largura útil da folha")
    print("  - Força máxima de abertura manual: 150 N (sem pressão)")
    print("-" * 80)
    print("4. DISPOSITIVOS DE FECHAMENTO AUTOMÁTICO E COORDENAÇÃO")
    print("  - Mola aérea obrigatória em todas as portas corta-fogo")
    print("  - Porta dupla exige seletor de fechamento para sobreposição correta do batente")
    print("=" * 80)
    return 0


def _comando_gerar_exemplo(args: argparse.Namespace) -> int:
    exemplo_json = """{
  "nome_edificacao": "Torre Empresarial Paulista",
  "responsavel_tecnico": "Eng. Martin Lofrano",
  "portas": [
    {
      "identificacao": "PCF-01 (Térreo - Escada Protegida)",
      "ambiente": "escada_enclausurada_protegida",
      "tipo_folha": "folha_unica",
      "classe_especificada": "P-60",
      "largura_vao_livre_m": "0.90",
      "altura_vao_livre_m": "2.10",
      "populacao_atendida": 80,
      "possui_seletor_fechamento": false,
      "possui_eletroima_retencao": false,
      "dados_folgas": {
        "folga_superior_mm": "2.5",
        "folga_lateral_esquerda_mm": "2.5",
        "folga_lateral_direita_mm": "2.5",
        "folga_inferior_piso_mm": "8.0"
      },
      "dados_barra": {
        "instalada": false
      }
    },
    {
      "identificacao": "PCF-02 (Auditório Principal)",
      "ambiente": "local_reuniao_publico",
      "tipo_folha": "folha_dupla",
      "classe_especificada": "P-60",
      "largura_vao_livre_m": "1.80",
      "altura_vao_livre_m": "2.10",
      "populacao_atendida": 250,
      "possui_seletor_fechamento": true,
      "possui_eletroima_retencao": true,
      "dados_folgas": {
        "folga_superior_mm": "2.8",
        "folga_lateral_esquerda_mm": "2.5",
        "folga_lateral_direita_mm": "2.5",
        "folga_inferior_piso_mm": "7.0",
        "folga_entre_folhas_mm": "2.8"
      },
      "dados_barra": {
        "instalada": true,
        "altura_instalacao_m": "1.00",
        "comprimento_barra_m": "0.65",
        "forca_operacao_n": 120
      }
    },
    {
      "identificacao": "PCF-03 (Subestação Elétrica Transformadores)",
      "ambiente": "subestacao_sala_eletrica",
      "tipo_folha": "folha_unica",
      "classe_especificada": "P-120",
      "largura_vao_livre_m": "1.10",
      "altura_vao_livre_m": "2.10",
      "populacao_atendida": 10,
      "possui_seletor_fechamento": false,
      "possui_eletroima_retencao": false,
      "dados_folgas": {
        "folga_superior_mm": "2.0",
        "folga_lateral_esquerda_mm": "2.0",
        "folga_lateral_direita_mm": "2.0",
        "folga_inferior_piso_mm": "6.0"
      },
      "dados_barra": {
        "instalada": false
      }
    }
  ]
}
"""
    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(exemplo_json)
            print(f"[OK] Modelo de exemplo gravado em '{args.saida}'")
        except Exception as err:
            print(f"Erro ao gravar arquivo de exemplo: {err}", file=sys.stderr)
            return 1
    else:
        print(exemplo_json)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="pcf-nbr11742",
        description="Dimensionamento e Especificação de Portas Corta-Fogo e Barras Antipânico (ABNT NBR 11742 / ABNT NBR 11785) - Lofrano Tecnologia",
        add_help=False,
    )

    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Exibe esta mensagem de ajuda e encerra.")
    parser.add_argument(
        "-v",
        "--version",
        "--versao",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão do programa.",
    )

    subparsers = parser.add_subparsers(dest="subcomando", title="Subcomandos Disponíveis")

    # Subcomando 'calcular'
    parser_calc = subparsers.add_parser("calcular", help="Dimensiona e audita as portas corta-fogo a partir de JSON.")
    parser_calc.add_argument("arquivo", help="Caminho do arquivo JSON de entrada.")
    parser_calc.add_argument(
        "--formato",
        choices=["texto", "json", "csv", "svg"],
        default="texto",
        help="Formato de saída dos resultados (padrão: texto).",
    )
    parser_calc.add_argument("--saida", help="Arquivo de destino para salvar a saída.")
    parser_calc.add_argument("--pacote-zip", help="Gera pacote ZIP determinístico completo no caminho especificado.")

    # Subcomando 'catalogo'
    subparsers.add_parser("catalogo", help="Exibe o catálogo de referências e critérios normativos das NBR 11742 e 11785.")

    # Subcomando 'gerar-exemplo'
    parser_ex = subparsers.add_parser("gerar-exemplo", help="Gera arquivo JSON modelo de exemplo para preenchimento.")
    parser_ex.add_argument("--saida", help="Arquivo de destino para gravar o JSON de exemplo.")

    args = parser.parse_args(argv)

    if not args.subcomando:
        parser.print_help()
        return 0

    if args.subcomando == "calcular":
        return _comando_calcular(args)
    elif args.subcomando == "catalogo":
        return _comando_catalogo(args)
    elif args.subcomando == "gerar-exemplo":
        return _comando_gerar_exemplo(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
