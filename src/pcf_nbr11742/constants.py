"""Constantes e parâmetros normativos da ABNT NBR 11742:2018 e NBR 11785:2018.

ABNT NBR 11742:2018 - Porta corta-fogo para saída de emergência.
ABNT NBR 11785:2018 - Barra antipânico - Requisitos.
"""

from fractions import Fraction
from typing import Final

# Unidade de Passagem (UP) e Capacidade de Escoamento (NBR 9077 / NBR 11742)
LARGURA_UNIDADE_PASSAGEM_M: Final[Fraction] = Fraction(55, 100)  # 0.55 m
CAPACIDADE_ESCOAMENTO_PORTA_UP: Final[int] = 100                 # 100 pessoas / UP

# Tempos de Resistência ao Fogo Regulamentares (minutos)
TEMPO_RESISTENCIA_P30_MIN: Final[int] = 30
TEMPO_RESISTENCIA_P60_MIN: Final[int] = 60
TEMPO_RESISTENCIA_P90_MIN: Final[int] = 90
TEMPO_RESISTENCIA_P120_MIN: Final[int] = 120

# Folgas Dimensionais Máximas de Montagem e Funcionamento (NBR 11742:2018 item 5.2.3)
FOLGA_MAX_BATENTE_SUPERIOR_MM: Final[Fraction] = Fraction(3, 1)  # 3.0 mm
FOLGA_MAX_BATENTE_LATERAIS_MM: Final[Fraction] = Fraction(3, 1)  # 3.0 mm
FOLGA_MAX_ENTRE_FOLHAS_MM: Final[Fraction] = Fraction(3, 1)      # 3.0 mm (porta dupla)
FOLGA_MAX_PISO_ACABADO_MM: Final[Fraction] = Fraction(10, 1)     # 10.0 mm

# Parâmetros Normativos da Barra Antipânico (ABNT NBR 11785:2018)
ALTURA_MINIMA_BARRA_M: Final[Fraction] = Fraction(90, 100)       # 0.90 m
ALTURA_MAXIMA_BARRA_M: Final[Fraction] = Fraction(110, 100)      # 1.10 m
ALTURA_NOMINAL_BARRA_M: Final[Fraction] = Fraction(1, 1)         # 1.00 m
FRACAO_MINIMA_COMPRIMENTO_BARRA: Final[Fraction] = Fraction(6, 10)  # Mínimo 60% da largura da folha
FORCA_MAXIMA_ABERTURA_BARRA_N: Final[int] = 150                  # 150 N (manual sem pressão)
FORCA_MAXIMA_PRESSAO_ESTATICA_N: Final[int] = 220                # 220 N

# Critérios de Obrigatoriedade de Barra Antipânico por População
POPULACAO_GATILHO_BARRA_REUNIAO: Final[int] = 100  # Locais de reunião (Grupo F) >= 100 pessoas
POPULACAO_GATILHO_BARRA_GERAL: Final[int] = 200    # Demais ocupações na rota de fuga >= 200 pessoas

# Vãos Livres Mínimos e Padrões Regulamentares (metros)
VAO_LIVRE_MINIMO_FOLHA_UNICA_M: Final[Fraction] = Fraction(80, 100)    # 0.80 m
VAO_LIVRE_MINIMO_HOSPITAIS_M: Final[Fraction] = Fraction(220, 100)     # 2.20 m (passagem de leitos)
ALTURA_PADRAO_VAO_LIVRE_M: Final[Fraction] = Fraction(210, 100)        # 2.10 m
