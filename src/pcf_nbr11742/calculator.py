"""Motor de cálculo e verificação normativa para portas corta-fogo NBR 11742 e NBR 11785."""

from fractions import Fraction
from typing import Optional

from pcf_nbr11742.constants import (
    ALTURA_MAXIMA_BARRA_M,
    ALTURA_MINIMA_BARRA_M,
    ALTURA_PADRAO_VAO_LIVRE_M,
    CAPACIDADE_ESCOAMENTO_PORTA_UP,
    FOLGA_MAX_BATENTE_LATERAIS_MM,
    FOLGA_MAX_BATENTE_SUPERIOR_MM,
    FOLGA_MAX_ENTRE_FOLHAS_MM,
    FOLGA_MAX_PISO_ACABADO_MM,
    FORCA_MAXIMA_ABERTURA_BARRA_N,
    FRACAO_MINIMA_COMPRIMENTO_BARRA,
    LARGURA_UNIDADE_PASSAGEM_M,
    POPULACAO_GATILHO_BARRA_GERAL,
    POPULACAO_GATILHO_BARRA_REUNIAO,
    TEMPO_RESISTENCIA_P120_MIN,
    TEMPO_RESISTENCIA_P30_MIN,
    TEMPO_RESISTENCIA_P60_MIN,
    TEMPO_RESISTENCIA_P90_MIN,
    VAO_LIVRE_MINIMO_FOLHA_UNICA_M,
)
from pcf_nbr11742.models import (
    AmbienteInstalacao,
    ClasseResistenciaFogo,
    DadosBarraAntipanico,
    DadosFolgasInstalacao,
    DadosPorta,
    DadosProjetoPortas,
    ResultadoBarra,
    ResultadoDimensionamento,
    ResultadoFolgas,
    ResultadoPorta,
    TipoFolhaPorta,
)


def _teto_fracao(f: Fraction) -> int:
    """Calcula o teto (ceil) de uma fração com precisão aritmética exata."""
    if f.denominator == 1:
        return f.numerator
    inteiro = f.numerator // f.denominator
    return inteiro + 1 if f.numerator > 0 else inteiro


def _obter_minutos_classe(classe: ClasseResistenciaFogo) -> int:
    """Retorna o tempo de resistência em minutos associado à classe."""
    mapeamento = {
        ClasseResistenciaFogo.P30: TEMPO_RESISTENCIA_P30_MIN,
        ClasseResistenciaFogo.P60: TEMPO_RESISTENCIA_P60_MIN,
        ClasseResistenciaFogo.P90: TEMPO_RESISTENCIA_P90_MIN,
        ClasseResistenciaFogo.P120: TEMPO_RESISTENCIA_P120_MIN,
    }
    return mapeamento[classe]


def determinar_classe_minima(ambiente: AmbienteInstalacao) -> ClasseResistenciaFogo:
    """Determina a classe mínima de resistência ao fogo exigida pela NBR 11742 conforme o ambiente."""
    if ambiente in (AmbienteInstalacao.SUBESTACAO_SALA_ELETRICA, AmbienteInstalacao.CENTRAL_GLP_INFLAMAVEIS):
        return ClasseResistenciaFogo.P120
    if ambiente in (AmbienteInstalacao.ESCADA_ENCLAUSURADA_FUMACA, AmbienteInstalacao.ANTECAMARA_DUTO):
        return ClasseResistenciaFogo.P90
    if ambiente in (AmbienteInstalacao.ESCADA_ENCLAUSURADA_PROTEGIDA, AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO):
        return ClasseResistenciaFogo.P60
    return ClasseResistenciaFogo.P30


def comparar_classes_resistencia(especificada: ClasseResistenciaFogo, minima: ClasseResistenciaFogo) -> bool:
    """Verifica se a classe especificada atende ou supera a exigência normativa mínima."""
    return _obter_minutos_classe(especificada) >= _obter_minutos_classe(minima)


def determinar_classe_mola_en(largura_folha_m: Fraction) -> str:
    """Determina a classe de força da mola aérea hidráulica segundo EN 1154 baseada na largura da folha."""
    if largura_folha_m <= Fraction(85, 100):
        return "EN 2 (Folhas até 850 mm)"
    if largura_folha_m <= Fraction(95, 100):
        return "EN 3 (Folhas até 950 mm)"
    if largura_folha_m <= Fraction(110, 100):
        return "EN 4 (Folhas até 1100 mm)"
    if largura_folha_m <= Fraction(125, 100):
        return "EN 5 (Folhas até 1250 mm)"
    return "EN 6 (Folhas acima de 1250 mm)"


def avaliar_folgas_instalacao(
    folgas: DadosFolgasInstalacao,
    tipo_folha: TipoFolhaPorta,
) -> ResultadoFolgas:
    """Audita as folgas perimetrais e inferiores segundo o item 5.2.3 da NBR 11742:2018."""
    detalhes: list[str] = []

    conforme_sup = folgas.folga_superior_mm <= FOLGA_MAX_BATENTE_SUPERIOR_MM
    if not conforme_sup:
        detalhes.append(
            f"Folga superior de {folgas.folga_superior_mm} mm excede o máximo de {FOLGA_MAX_BATENTE_SUPERIOR_MM} mm."
        )

    conforme_lat = (
        folgas.folga_lateral_esquerda_mm <= FOLGA_MAX_BATENTE_LATERAIS_MM
        and folgas.folga_lateral_direita_mm <= FOLGA_MAX_BATENTE_LATERAIS_MM
    )
    if not conforme_lat:
        detalhes.append(
            f"Folgas laterais (Esq: {folgas.folga_lateral_esquerda_mm} mm, Dir: {folgas.folga_lateral_direita_mm} mm) "
            f"excedem o limite máximo de {FOLGA_MAX_BATENTE_LATERAIS_MM} mm."
        )

    conforme_piso = folgas.folga_inferior_piso_mm <= FOLGA_MAX_PISO_ACABADO_MM
    if not conforme_piso:
        detalhes.append(
            f"Folga inferior em relação ao piso ({folgas.folga_inferior_piso_mm} mm) excede o limite normativo de {FOLGA_MAX_PISO_ACABADO_MM} mm."
        )

    conforme_entre_folhas = True
    if tipo_folha == TipoFolhaPorta.DUPLA:
        if folgas.folga_entre_folhas_mm is None:
            conforme_entre_folhas = False
            detalhes.append("Porta de folha dupla exige medição da folga de encontro central entre as folhas.")
        elif folgas.folga_entre_folhas_mm > FOLGA_MAX_ENTRE_FOLHAS_MM:
            conforme_entre_folhas = False
            detalhes.append(
                f"Folga central entre folhas ({folgas.folga_entre_folhas_mm} mm) excede o limite de {FOLGA_MAX_ENTRE_FOLHAS_MM} mm."
            )

    conforme_geral = conforme_sup and conforme_lat and conforme_piso and conforme_entre_folhas

    return ResultadoFolgas(
        conforme_superior=conforme_sup,
        conforme_laterais=conforme_lat,
        conforme_piso=conforme_piso,
        conforme_entre_folhas=conforme_entre_folhas,
        conforme_geral=conforme_geral,
        detalhes=tuple(detalhes),
    )


def avaliar_barra_antipanico(
    dados_barra: Optional[DadosBarraAntipanico],
    populacao: int,
    ambiente: AmbienteInstalacao,
    largura_folha_m: Fraction,
) -> ResultadoBarra:
    """Avalia a necessidade e a conformidade da barra antipânico conforme a NBR 11785:2018."""
    detalhes: list[str] = []

    obrigatoria = (
        (ambiente == AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO and populacao >= POPULACAO_GATILHO_BARRA_REUNIAO)
        or (populacao >= POPULACAO_GATILHO_BARRA_GERAL)
    )

    comprimento_minimo = largura_folha_m * FRACAO_MINIMA_COMPRIMENTO_BARRA

    if not dados_barra or not dados_barra.instalada:
        conforme_presenca = not obrigatoria
        if obrigatoria:
            detalhes.append(
                f"Barra antipânico obrigatória para população de {populacao} pessoas "
                f"(limite de gatilho: {POPULACAO_GATILHO_BARRA_REUNIAO if ambiente == AmbienteInstalacao.LOCAL_REUNIAO_PUBLICO else POPULACAO_GATILHO_BARRA_GERAL} pessoas)."
            )
        return ResultadoBarra(
            obrigatoria=obrigatoria,
            instalada=False,
            conforme_presenca=conforme_presenca,
            conforme_altura=True,
            conforme_comprimento=True,
            conforme_forca=True,
            conforme_geral=conforme_presenca,
            comprimento_minimo_requerido_m=comprimento_minimo,
            detalhes=tuple(detalhes),
        )

    conforme_presenca = True

    conforme_altura = True
    if dados_barra.altura_instalacao_m is not None:
        if not (ALTURA_MINIMA_BARRA_M <= dados_barra.altura_instalacao_m <= ALTURA_MAXIMA_BARRA_M):
            conforme_altura = False
            detalhes.append(
                f"Altura da barra ({dados_barra.altura_instalacao_m} m) fora da faixa regulamentar "
                f"({ALTURA_MINIMA_BARRA_M} m a {ALTURA_MAXIMA_BARRA_M} m)."
            )

    conforme_comp = True
    if dados_barra.comprimento_barra_m is not None:
        if dados_barra.comprimento_barra_m < comprimento_minimo:
            conforme_comp = False
            detalhes.append(
                f"Comprimento da barra ({dados_barra.comprimento_barra_m} m) é inferior a 60% da folha "
                f"(mínimo de {comprimento_minimo} m)."
            )

    conforme_forca = True
    if dados_barra.forca_operacao_n is not None:
        if dados_barra.forca_operacao_n > FORCA_MAXIMA_ABERTURA_BARRA_N:
            conforme_forca = False
            detalhes.append(
                f"Força de abertura da barra ({dados_barra.forca_operacao_n} N) excede o limite máximo de {FORCA_MAXIMA_ABERTURA_BARRA_N} N."
            )

    conforme_geral = conforme_presenca and conforme_altura and conforme_comp and conforme_forca

    return ResultadoBarra(
        obrigatoria=obrigatoria,
        instalada=True,
        conforme_presenca=conforme_presenca,
        conforme_altura=conforme_altura,
        conforme_comprimento=conforme_comp,
        conforme_forca=conforme_forca,
        conforme_geral=conforme_geral,
        comprimento_minimo_requerido_m=comprimento_minimo,
        detalhes=tuple(detalhes),
    )


def dimensionar_porta(porta: DadosPorta) -> ResultadoPorta:
    """Dimensiona e audita uma porta corta-fogo conforme as normas NBR 11742 e NBR 11785."""
    alertas: list[str] = []

    # 1. Classe de Resistência ao Fogo
    classe_minima = determinar_classe_minima(porta.ambiente)
    conforme_classe = comparar_classes_resistencia(porta.classe_especificada, classe_minima)
    if not conforme_classe:
        alertas.append(
            f"Porta '{porta.identificacao}': ambiente '{porta.ambiente.value}' exige classe mínima {classe_minima.value}, "
            f"porém foi especificada {porta.classe_especificada.value}."
        )

    # 2. Vão livre e capacidade de escoamento
    largura_folha_efetiva = (
        porta.largura_vao_livre_m / 2 if porta.tipo_folha == TipoFolhaPorta.DUPLA else porta.largura_vao_livre_m
    )

    unidades_passagem = int(porta.largura_vao_livre_m / LARGURA_UNIDADE_PASSAGEM_M)
    capacidade_fluxo = unidades_passagem * CAPACIDADE_ESCOAMENTO_PORTA_UP
    conforme_capacidade = capacidade_fluxo >= porta.populacao_atendida

    if not conforme_capacidade:
        up_necessaria = _teto_fracao(Fraction(porta.populacao_atendida, CAPACIDADE_ESCOAMENTO_PORTA_UP))
        alertas.append(
            f"Porta '{porta.identificacao}': população de {porta.populacao_atendida} pessoas requer "
            f"{up_necessaria} UP ({up_necessaria * LARGURA_UNIDADE_PASSAGEM_M} m), porém vão atual fornece apenas "
            f"{unidades_passagem} UP ({capacidade_fluxo} pessoas)."
        )

    largura_minima_requerida = max(
        VAO_LIVRE_MINIMO_FOLHA_UNICA_M,
        Fraction(_teto_fracao(Fraction(porta.populacao_atendida, CAPACIDADE_ESCOAMENTO_PORTA_UP)), 1)
        * LARGURA_UNIDADE_PASSAGEM_M,
    )
    conforme_largura = porta.largura_vao_livre_m >= largura_minima_requerida
    if not conforme_largura:
        alertas.append(
            f"Porta '{porta.identificacao}': largura do vão livre ({porta.largura_vao_livre_m} m) é inferior à largura mínima "
            f"regulamentar de {largura_minima_requerida} m."
        )

    # 3. Força da mola aérea regulamentar
    classe_mola = determinar_classe_mola_en(largura_folha_efetiva)

    # 4. Seletor de fechamento em porta dupla
    exige_seletor = porta.tipo_folha == TipoFolhaPorta.DUPLA
    conforme_seletor = True
    if exige_seletor and not porta.possui_seletor_fechamento:
        conforme_seletor = False
        alertas.append(
            f"Porta '{porta.identificacao}': porta de folha dupla exige coordenador/seletor de sequência de fechamento com batente sobreposto."
        )

    # 5. Avaliação de folgas de montagem
    res_folgas: Optional[ResultadoFolgas] = None
    if porta.dados_folgas is not None:
        res_folgas = avaliar_folgas_instalacao(porta.dados_folgas, porta.tipo_folha)
        if not res_folgas.conforme_geral:
            for det in res_folgas.detalhes:
                alertas.append(f"Porta '{porta.identificacao}': {det}")

    # 6. Avaliação da barra antipânico
    res_barra = avaliar_barra_antipanico(
        porta.dados_barra,
        porta.populacao_atendida,
        porta.ambiente,
        largura_folha_efetiva,
    )
    if not res_barra.conforme_geral:
        for det in res_barra.detalhes:
            alertas.append(f"Porta '{porta.identificacao}': {det}")

    # Conformidade geral da porta
    conforme_geral = (
        conforme_classe
        and conforme_capacidade
        and conforme_largura
        and conforme_seletor
        and (res_folgas is None or res_folgas.conforme_geral)
        and res_barra.conforme_geral
    )

    return ResultadoPorta(
        identificacao=porta.identificacao,
        ambiente=porta.ambiente,
        tipo_folha=porta.tipo_folha,
        classe_especificada=porta.classe_especificada,
        classe_minima_normativa=classe_minima,
        conforme_classe_resistencia=conforme_classe,
        largura_vao_livre_m=porta.largura_vao_livre_m,
        altura_vao_livre_m=porta.altura_vao_livre_m,
        unidades_passagem_fornecidas=unidades_passagem,
        capacidade_escoamento_pessoas=capacidade_fluxo,
        populacao_atendida=porta.populacao_atendida,
        conforme_capacidade_fluxo=conforme_capacidade,
        largura_minima_requerida_m=largura_minima_requerida,
        conforme_largura_minima=conforme_largura,
        mola_aerea_classe_en=classe_mola,
        exige_seletor_fechamento=exige_seletor,
        conforme_seletor=conforme_seletor,
        resultado_folgas=res_folgas,
        resultado_barra=res_barra,
        conforme_geral=conforme_geral,
        alertas=tuple(alertas),
    )


def dimensionar_projeto_portas(projeto: DadosProjetoPortas) -> ResultadoDimensionamento:
    """Processa todas as portas corta-fogo do projeto e gera o relatório conclusivo."""
    res_portas: list[ResultadoPorta] = []
    alertas_gerais: list[str] = []
    recomendacoes: list[str] = []

    portas_conformes = 0
    portas_inconformes = 0

    for porta in projeto.portas:
        res_p = dimensionar_porta(porta)
        res_portas.append(res_p)
        if res_p.conforme_geral:
            portas_conformes += 1
        else:
            portas_inconformes += 1
            for a in res_p.alertas:
                alertas_gerais.append(a)

    recomendacoes.append(
        "Portas corta-fogo devem ser mantidas permanentemente fechadas por mola aérea regulamentar ou retidas por eletroímã comandado pelo alarme de incêndio."
    )
    recomendacoes.append(
        "É terminantemente vedada a utilização de cunhas, calços ou travas mecânicas improvisadas para manter portas corta-fogo abertas."
    )
    recomendacoes.append(
        "As folgas entre folha e batente devem ser inspecionadas periodicamente e não ultrapassar 3,0 mm (laterais e topo) e 10,0 mm no piso."
    )
    recomendacoes.append(
        "Barras antipânico devem ser testadas semestralmente, garantindo acionamento suave com força não superior a 150 N em toda a extensão móvel."
    )

    sistema_conforme = portas_inconformes == 0

    return ResultadoDimensionamento(
        nome_edificacao=projeto.nome_edificacao,
        responsavel_tecnico=projeto.responsavel_tecnico,
        total_portas=len(res_portas),
        portas_conformes=portas_conformes,
        portas_inconformes=portas_inconformes,
        sistema_totalmente_conforme=sistema_conforme,
        portas=tuple(res_portas),
        alertas_gerais=tuple(alertas_gerais),
        recomendacoes=tuple(recomendacoes),
    )
