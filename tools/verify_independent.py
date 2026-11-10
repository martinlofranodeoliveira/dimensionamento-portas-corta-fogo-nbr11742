#!/usr/bin/env python3
"""Auditor independente em SQLite em memória para portas corta-fogo NBR 11742 / NBR 11785.

Este script é 100% desacoplado do código de produção de 'src/pcf_nbr11742' e não importa
nenhum módulo do pacote. Utiliza exclusivamente a biblioteca padrão do Python e SQLite
em memória para verificar a conformidade regulamentar dos cenários em 'examples/'.
"""

import glob
import json
import os
import sqlite3
import sys
from fractions import Fraction


def para_fracao(val) -> Fraction:
    return Fraction(str(val))


def classe_minima_por_ambiente(amb: str) -> str:
    if amb in ("subestacao_sala_eletrica", "central_glp_inflamaveis"):
        return "P-120"
    if amb in ("escada_enclausurada_fumaca", "antecamara_duto"):
        return "P-90"
    if amb in ("escada_enclausurada_protegida", "local_reuniao_publico"):
        return "P-60"
    return "P-30"


def minutos_classe(cls_str: str) -> int:
    mapeamento = {"P-30": 30, "P-60": 60, "P-90": 90, "P-120": 120}
    return mapeamento.get(cls_str, 0)


def auditar_arquivo(caminho_json: str) -> bool:
    print(f"\n[AUDITORIA INDEPENDENTE] Verificando arquivo: {os.path.basename(caminho_json)}")

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE portas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT,
            ambiente TEXT,
            tipo_folha TEXT,
            classe_especificada TEXT,
            largura_m_num INTEGER,
            largura_m_den INTEGER,
            altura_m_num INTEGER,
            altura_m_den INTEGER,
            populacao INTEGER,
            seletor_fechamento INTEGER,
            folga_sup_mm_num INTEGER,
            folga_sup_mm_den INTEGER,
            folga_esq_mm_num INTEGER,
            folga_esq_mm_den INTEGER,
            folga_dir_mm_num INTEGER,
            folga_dir_mm_den INTEGER,
            folga_piso_mm_num INTEGER,
            folga_piso_mm_den INTEGER,
            folga_entre_mm_num INTEGER,
            folga_entre_mm_den INTEGER,
            barra_instalada INTEGER,
            barra_alt_num INTEGER,
            barra_alt_den INTEGER,
            barra_comp_num INTEGER,
            barra_comp_den INTEGER,
            barra_forca_n INTEGER
        )
    """)

    for p in dados.get("portas", []):
        larg = para_fracao(p["largura_vao_livre_m"])
        alt = para_fracao(p["altura_vao_livre_m"])
        folgas = p.get("dados_folgas", {})
        f_sup = para_fracao(folgas.get("folga_superior_mm", "2.0")) if folgas else Fraction(0)
        f_esq = para_fracao(folgas.get("folga_lateral_esquerda_mm", "2.0")) if folgas else Fraction(0)
        f_dir = para_fracao(folgas.get("folga_lateral_direita_mm", "2.0")) if folgas else Fraction(0)
        f_piso = para_fracao(folgas.get("folga_inferior_piso_mm", "5.0")) if folgas else Fraction(0)
        f_entre = (
            para_fracao(folgas["folga_entre_folhas_mm"])
            if folgas and folgas.get("folga_entre_folhas_mm") is not None
            else None
        )

        barra = p.get("dados_barra", {})
        b_inst = 1 if barra.get("instalada") else 0
        b_alt = para_fracao(barra["altura_instalacao_m"]) if barra.get("altura_instalacao_m") else None
        b_comp = para_fracao(barra["comprimento_barra_m"]) if barra.get("comprimento_barra_m") else None
        b_forca = barra.get("forca_operacao_n")

        cursor.execute(
            """
            INSERT INTO portas (
                identificacao, ambiente, tipo_folha, classe_especificada,
                largura_m_num, largura_m_den, altura_m_num, altura_m_den,
                populacao, seletor_fechamento,
                folga_sup_mm_num, folga_sup_mm_den,
                folga_esq_mm_num, folga_esq_mm_den,
                folga_dir_mm_num, folga_dir_mm_den,
                folga_piso_mm_num, folga_piso_mm_den,
                folga_entre_mm_num, folga_entre_mm_den,
                barra_instalada, barra_alt_num, barra_alt_den,
                barra_comp_num, barra_comp_den, barra_forca_n
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                p["identificacao"],
                p["ambiente"],
                p["tipo_folha"],
                p["classe_especificada"],
                larg.numerator,
                larg.denominator,
                alt.numerator,
                alt.denominator,
                p["populacao_atendida"],
                1 if p.get("possui_seletor_fechamento") else 0,
                f_sup.numerator,
                f_sup.denominator,
                f_esq.numerator,
                f_esq.denominator,
                f_dir.numerator,
                f_dir.denominator,
                f_piso.numerator,
                f_piso.denominator,
                f_entre.numerator if f_entre is not None else None,
                f_entre.denominator if f_entre is not None else None,
                b_inst,
                b_alt.numerator if b_alt is not None else None,
                b_alt.denominator if b_alt is not None else None,
                b_comp.numerator if b_comp is not None else None,
                b_comp.denominator if b_comp is not None else None,
                b_forca,
            ),
        )

    conn.commit()

    cursor.execute("SELECT * FROM portas")
    linhas = cursor.fetchall()

    sucesso = True
    for row in linhas:
        (
            _,
            ident,
            amb,
            folha,
            classe_esp,
            l_num,
            l_den,
            a_num,
            a_den,
            pop,
            seletor,
            fs_num,
            fs_den,
            fe_num,
            fe_den,
            fd_num,
            fd_den,
            fp_num,
            fp_den,
            fen_num,
            fen_den,
            b_inst,
            ba_num,
            ba_den,
            bc_num,
            bc_den,
            b_forca,
        ) = row

        larg = Fraction(l_num, l_den)
        alt = Fraction(a_num, a_den)

        # 1. Auditoria de classe de resistência
        classe_min = classe_minima_por_ambiente(amb)
        if minutos_classe(classe_esp) < minutos_classe(classe_min):
            print(f"  [FALHA] {ident}: Classe {classe_esp} inferior à mínima exigida ({classe_min})")
            sucesso = False
        else:
            print(f"  [OK] {ident}: Classe {classe_esp} atende ou supera a exigência ({classe_min})")

        # 2. Capacidade de fluxo (UP = 0,55 m, 100 pess/UP)
        up = int(larg / Fraction(55, 100))
        cap = up * 100
        if cap < pop:
            print(f"  [FALHA] {ident}: Vão de {larg}m ({up} UP = {cap} pess) não suporta população de {pop}")
            sucesso = False
        else:
            print(f"  [OK] {ident}: Vão de {larg}m ({up} UP) atende população de {pop} pessoas")

        # 3. Folga no batente e piso
        fs = Fraction(fs_num, fs_den)
        fe = Fraction(fe_num, fe_den)
        fd = Fraction(fd_num, fd_den)
        fp = Fraction(fp_num, fp_den)
        if fs > Fraction(3, 1) or fe > Fraction(3, 1) or fd > Fraction(3, 1):
            print(f"  [FALHA] {ident}: Folgas laterais/topo excedem 3.0 mm (S:{fs}, E:{fe}, D:{fd})")
            sucesso = False
        if fp > Fraction(10, 1):
            print(f"  [FALHA] {ident}: Folga do piso ({fp} mm) excede 10.0 mm")
            sucesso = False

        if folha == "folha_dupla":
            if fen_num is not None and fen_den is not None:
                fen = Fraction(fen_num, fen_den)
                if fen > Fraction(3, 1):
                    print(f"  [FALHA] {ident}: Folga entre folhas ({fen} mm) excede 3.0 mm")
                    sucesso = False
            if not seletor:
                print(f"  [FALHA] {ident}: Folha dupla sem seletor de sequência de fechamento")
                sucesso = False

        # 4. Barra antipânico
        obrigatoria = (amb == "local_reuniao_publico" and pop >= 100) or pop >= 200
        if obrigatoria and not b_inst:
            print(f"  [FALHA] {ident}: Barra antipânico obrigatória para pop={pop} mas ausente")
            sucesso = False
        elif b_inst:
            larg_folha = larg / 2 if folha == "folha_dupla" else larg
            if ba_num and ba_den:
                ba = Fraction(ba_num, ba_den)
                if not (Fraction(9, 10) <= ba <= Fraction(11, 10)):
                    print(f"  [FALHA] {ident}: Altura da barra ({ba}m) fora da faixa 0,90m a 1,10m")
                    sucesso = False
            if bc_num and bc_den:
                bc = Fraction(bc_num, bc_den)
                if bc < larg_folha * Fraction(6, 10):
                    print(f"  [FALHA] {ident}: Barra ({bc}m) inferior a 60% da folha ({larg_folha * Fraction(6, 10)}m)")
                    sucesso = False
            if b_forca and b_forca > 150:
                print(f"  [FALHA] {ident}: Força de abertura ({b_forca}N) excede 150 N")
                sucesso = False

    conn.close()

    if sucesso:
        print(f"  [SUCESSO] Auditoria independente de {os.path.basename(caminho_json)} aprovada 100%!")
    return sucesso


def main() -> int:
    arquivos = sorted(glob.glob("examples/*.json"))
    if not arquivos:
        print("Nenhum arquivo de exemplo encontrado em examples/")
        return 1

    todos_sucesso = True
    for arq in arquivos:
        if not auditar_arquivo(arq):
            todos_sucesso = False

    print("\n" + "=" * 80)
    if todos_sucesso:
        print("TODAS AS AUDITORIAS INDEPENDENTES FORAM APROVADAS COM SUCESSO!")
        print("=" * 80)
        return 0
    else:
        print("ERRO: UMA OU MAIS AUDITORIAS INDEPENDENTES FALHARAM!")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
