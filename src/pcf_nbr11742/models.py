"""Modelos de dados e dataclasses imutáveis para portas corta-fogo NBR 11742 / NBR 11785."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional


class ClasseResistenciaFogo(str, Enum):
    """Classes normativas de resistência ao fogo segundo ABNT NBR 11742."""
    P30 = "P-30"    # 30 minutos
    P60 = "P-60"    # 60 minutos
    P90 = "P-90"    # 90 minutos
    P120 = "P-120"  # 120 minutos


class TipoFolhaPorta(str, Enum):
    """Configuração da quantidade de folhas da porta corta-fogo."""
    UNICA = "folha_unica"
    DUPLA = "folha_dupla"


class AmbienteInstalacao(str, Enum):
    """Ambientes regulamentares de aplicação de portas corta-fogo."""
    ESCADA_ENCLAUSURADA_PROTEGIDA = "escada_enclausurada_protegida"
    ESCADA_ENCLAUSURADA_FUMACA = "escada_enclausurada_fumaca"
    ANTECAMARA_DUTO = "antecamara_duto"
    SUBESTACAO_SALA_ELETRICA = "subestacao_sala_eletrica"
    CENTRAL_GLP_INFLAMAVEIS = "central_glp_inflamaveis"
    CORREDOR_COMPARTIMENTACAO = "corredor_compartimentacao"
    LOCAL_REUNIAO_PUBLICO = "local_reuniao_publico"


@dataclass(frozen=True)
class DadosFolgasInstalacao:
    """Folgas dimensionais medidas na montagem da folha com o batente e piso."""
    folga_superior_mm: Fraction
    folga_lateral_esquerda_mm: Fraction
    folga_lateral_direita_mm: Fraction
    folga_inferior_piso_mm: Fraction
    folga_entre_folhas_mm: Optional[Fraction] = None

    def __post_init__(self) -> None:
        if self.folga_superior_mm < 0 or self.folga_lateral_esquerda_mm < 0 or self.folga_lateral_direita_mm < 0:
            raise ValueError("As folgas perimetrais do batente não podem ser negativas.")
        if self.folga_inferior_piso_mm < 0:
            raise ValueError("A folga em relação ao piso acabado não pode ser negativa.")
        if self.folga_entre_folhas_mm is not None and self.folga_entre_folhas_mm < 0:
            raise ValueError("A folga entre folhas não pode ser negativa.")


@dataclass(frozen=True)
class DadosBarraAntipanico:
    """Parâmetros da barra antipânico instalada segundo a ABNT NBR 11785."""
    instalada: bool
    altura_instalacao_m: Optional[Fraction] = None
    comprimento_barra_m: Optional[Fraction] = None
    forca_operacao_n: Optional[int] = None

    def __post_init__(self) -> None:
        if self.instalada:
            if self.altura_instalacao_m is not None and self.altura_instalacao_m <= 0:
                raise ValueError("A altura de instalação da barra deve ser positiva.")
            if self.comprimento_barra_m is not None and self.comprimento_barra_m <= 0:
                raise ValueError("O comprimento da barra deve ser positivo.")
            if self.forca_operacao_n is not None and self.forca_operacao_n <= 0:
                raise ValueError("A força de operação da barra deve ser positiva.")


@dataclass(frozen=True)
class DadosPorta:
    """Especificações de projeto de uma porta corta-fogo individual."""
    identificacao: str
    ambiente: AmbienteInstalacao
    tipo_folha: TipoFolhaPorta
    classe_especificada: ClasseResistenciaFogo
    largura_vao_livre_m: Fraction
    altura_vao_livre_m: Fraction
    populacao_atendida: int
    possui_seletor_fechamento: bool = False
    possui_eletroima_retencao: bool = False
    dados_folgas: Optional[DadosFolgasInstalacao] = None
    dados_barra: Optional[DadosBarraAntipanico] = None

    def __post_init__(self) -> None:
        if not self.identificacao.strip():
            raise ValueError("A identificação da porta não pode ser vazia.")
        if self.largura_vao_livre_m <= 0 or self.altura_vao_livre_m <= 0:
            raise ValueError("As dimensões do vão livre da porta devem ser estritamente positivas.")
        if self.populacao_atendida < 0:
            raise ValueError("A população atendida pela porta não pode ser negativa.")


@dataclass(frozen=True)
class DadosProjetoPortas:
    """Conjunto das portas corta-fogo inspecionadas na edificação."""
    nome_edificacao: str
    responsavel_tecnico: str
    portas: tuple[DadosPorta, ...]

    def __post_init__(self) -> None:
        if not self.nome_edificacao.strip():
            raise ValueError("O nome da edificação não pode ser vazio.")
        if not self.portas:
            raise ValueError("O projeto deve conter pelo menos uma porta corta-fogo.")


@dataclass(frozen=True)
class ResultadoFolgas:
    """Avaliação de conformidade das folgas dimensionais de instalação."""
    conforme_superior: bool
    conforme_laterais: bool
    conforme_piso: bool
    conforme_entre_folhas: bool
    conforme_geral: bool
    detalhes: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoBarra:
    """Avaliação de conformidade da barra antipânico segundo a NBR 11785."""
    obrigatoria: bool
    instalada: bool
    conforme_presenca: bool
    conforme_altura: bool
    conforme_comprimento: bool
    conforme_forca: bool
    conforme_geral: bool
    comprimento_minimo_requerido_m: Fraction
    detalhes: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoPorta:
    """Resultado detalhado do dimensionamento e auditoria de uma porta corta-fogo."""
    identificacao: str
    ambiente: AmbienteInstalacao
    tipo_folha: TipoFolhaPorta
    classe_especificada: ClasseResistenciaFogo
    classe_minima_normativa: ClasseResistenciaFogo
    conforme_classe_resistencia: bool
    largura_vao_livre_m: Fraction
    altura_vao_livre_m: Fraction
    unidades_passagem_fornecidas: int
    capacidade_escoamento_pessoas: int
    populacao_atendida: int
    conforme_capacidade_fluxo: bool
    largura_minima_requerida_m: Fraction
    conforme_largura_minima: bool
    mola_aerea_classe_en: str
    exige_seletor_fechamento: bool
    conforme_seletor: bool
    resultado_folgas: Optional[ResultadoFolgas]
    resultado_barra: ResultadoBarra
    conforme_geral: bool
    alertas: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoDimensionamento:
    """Relatório consolidado de todas as portas corta-fogo da edificação."""
    nome_edificacao: str
    responsavel_tecnico: str
    total_portas: int
    portas_conformes: int
    portas_inconformes: int
    sistema_totalmente_conforme: bool
    portas: tuple[ResultadoPorta, ...]
    alertas_gerais: tuple[str, ...]
    recomendacoes: tuple[str, ...]
