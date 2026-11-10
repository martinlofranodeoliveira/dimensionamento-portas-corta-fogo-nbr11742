"""Gerador de painel técnico vetorial SVG para portas corta-fogo NBR 11742 / NBR 11785."""

from pcf_nbr11742.exporters import _fmt
from pcf_nbr11742.models import ResultadoDimensionamento


def gerar_painel_svg(res: ResultadoDimensionamento) -> str:
    """Gera painel vetorial SVG em alta resolução (1440x900) com esquema técnico de portas corta-fogo."""
    largura = 1440
    altura = 900

    linhas: list[str] = []
    linhas.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}">')
    linhas.append('  <defs>')
    linhas.append('    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#090d16" />')
    linhas.append('      <stop offset="100%" stop-color="#1e293b" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="portaGrad" x1="0" y1="0" x2="1" y2="0">')
    linhas.append('      <stop offset="0%" stop-color="#dc2626" />')
    linhas.append('      <stop offset="50%" stop-color="#ef4444" />')
    linhas.append('      <stop offset="100%" stop-color="#b91c1c" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="batenteGrad" x1="0" y1="0" x2="0" y2="1">')
    linhas.append('      <stop offset="0%" stop-color="#475569" />')
    linhas.append('      <stop offset="100%" stop-color="#334155" />')
    linhas.append('    </linearGradient>')
    linhas.append('    <linearGradient id="barraGrad" x1="0" y1="0" x2="1" y2="0">')
    linhas.append('      <stop offset="0%" stop-color="#e2e8f0" />')
    linhas.append('      <stop offset="100%" stop-color="#94a3b8" />')
    linhas.append('    </linearGradient>')
    linhas.append('  </defs>')

    # Fundo geral
    linhas.append(f'  <rect width="{largura}" height="{altura}" fill="url(#bgGrad)" />')

    # Cabeçalho
    linhas.append('  <rect x="30" y="25" width="1380" height="75" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />')
    linhas.append('  <text x="60" y="58" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="bold">LOFRANO TECNOLOGIA — ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO</text>')
    linhas.append('  <text x="60" y="82" fill="#38bdf8" font-family="system-ui, -apple-system, sans-serif" font-size="14">PORTAS CORTA-FOGO E BARRAS ANTIPÂNICO — ABNT NBR 11742:2018 / NBR 11785:2018</text>')
    linhas.append(f'  <text x="1380" y="70" text-anchor="end" fill="#94a3b8" font-family="monospace" font-size="13">Edificação: {res.nome_edificacao} | Total: {res.total_portas} porta(s)</text>')

    # Painel Esquerdo: Parâmetros do Projeto e Normativos
    linhas.append('  <g transform="translate(30, 120)">')
    linhas.append('    <rect width="360" height="745" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="20" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">PARÂMETROS REGULAMENTARES</text>')
    linhas.append('    <line x1="20" y1="48" x2="340" y2="48" stroke="#334155" stroke-width="1" />')

    status_glo = "TOTALMENTE CONFORME" if res.sistema_totalmente_conforme else "INCONFORMIDADES DETECTADAS"
    cor_glo = "#4ade80" if res.sistema_totalmente_conforme else "#f87171"

    dados_painel_esq = [
        ("Status Global", status_glo, cor_glo),
        ("Portas Conformes", f"{res.portas_conformes} / {res.total_portas}", "#f8fafc"),
        ("Portas Inconformes", f"{res.portas_inconformes}", "#f87171" if res.portas_inconformes > 0 else "#4ade80"),
        ("Unidade de Passagem (UP)", "0,55 m (100 pessoas / UP)", "#38bdf8"),
        ("Folga Lateral / Superior", "Máximo 3,0 mm (batente)", "#38bdf8"),
        ("Folga em Relação ao Piso", "Máximo 10,0 mm", "#38bdf8"),
        ("Folga Entre Folhas (Dupla)", "Máximo 3,0 mm", "#38bdf8"),
        ("Altura Barra Antipânico", "0,90 m a 1,10 m (NBR 11785)", "#38bdf8"),
        ("Comprimento Mínimo Barra", "60% da largura útil da folha", "#38bdf8"),
        ("Força Máxima de Abertura", "150 N (manual sem pressão)", "#38bdf8"),
    ]

    y_pos = 75
    for rotulo, val, cor in dados_painel_esq:
        linhas.append(f'    <text x="20" y="{y_pos}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">{rotulo}</text>')
        linhas.append(f'    <text x="20" y="{y_pos + 18}" fill="{cor}" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">{val}</text>')
        y_pos += 46

    # Caixa de classes normativas
    linhas.append('    <rect x="20" y="550" width="320" height="175" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="35" y="575" fill="#facc15" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">CLASSES DE RESISTÊNCIA AO FOGO</text>')
    linhas.append('    <text x="35" y="600" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">• P-30 (>= 30 min): Corredores comuns</text>')
    linhas.append('    <text x="35" y="625" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">• P-60 (>= 60 min): Escadas protegidas / Reunião</text>')
    linhas.append('    <text x="35" y="650" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">• P-90 (>= 90 min): Escadas à prova fumaça / Antecâmara</text>')
    linhas.append('    <text x="35" y="675" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">• P-120 (>= 120 min): Subestações / Centrais GLP</text>')
    linhas.append('    <text x="35" y="705" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10">Classificação conforme ABNT NBR 11742:2018</text>')
    linhas.append('  </g>')

    # Painel Central: Elevação Técnica Detalhada da Porta Corta-Fogo
    linhas.append('  <g transform="translate(410, 120)">')
    linhas.append('    <rect width="600" height="745" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="20" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">DETALHE EXECUTIVO DA PORTA CORTA-FOGO (PCF)</text>')
    linhas.append('    <line x1="20" y1="48" x2="580" y2="48" stroke="#334155" stroke-width="1" />')

    # Parede e vão
    linhas.append('    <rect x="70" y="80" width="460" height="540" fill="#0f172a" stroke="#334155" stroke-width="1.5" />')

    # Batente metálico
    linhas.append('    <rect x="110" y="110" width="380" height="480" fill="url(#batenteGrad)" stroke="#64748b" stroke-width="2" />')

    # Folha da porta
    linhas.append('    <rect x="125" y="125" width="350" height="455" rx="3" fill="url(#portaGrad)" stroke="#7f1d1d" stroke-width="2" />')

    # Mola aérea hidráulica no topo
    linhas.append('    <rect x="150" y="132" width="100" height="22" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="1.5" />')
    linhas.append('    <line x1="250" y1="143" x2="310" y2="120" stroke="#94a3b8" stroke-width="3" />')
    linhas.append('    <circle cx="310" cy="120" r="4" fill="#facc15" />')
    linhas.append('    <text x="200" y="147" text-anchor="middle" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">MOLA AÉREA</text>')

    # Placa regulamentar "PORTA CORTA-FOGO - MANTENHA FECHADA"
    linhas.append('    <rect x="220" y="240" width="160" height="40" rx="3" fill="#ffffff" stroke="#dc2626" stroke-width="2" />')
    linhas.append('    <text x="300" y="256" text-anchor="middle" fill="#dc2626" font-family="system-ui, sans-serif" font-size="9" font-weight="bold">PORTA CORTA-FOGO</text>')
    linhas.append('    <text x="300" y="271" text-anchor="middle" fill="#000000" font-family="system-ui, sans-serif" font-size="8" font-weight="bold">MANTENHA FECHADA</text>')

    # Barra antipânico (NBR 11785)
    linhas.append('    <g transform="translate(145, 380)">')
    linhas.append('      <rect width="310" height="20" rx="4" fill="url(#barraGrad)" stroke="#475569" stroke-width="1.5" />')
    linhas.append('      <rect x="10" y="5" width="40" height="10" rx="2" fill="#ef4444" />')
    linhas.append('      <rect x="260" y="5" width="40" height="10" rx="2" fill="#ef4444" />')
    linhas.append('      <text x="155" y="14" text-anchor="middle" fill="#0f172a" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">BARRA ANTIPÂNICO (ABNT NBR 11785)</text>')
    linhas.append('    </g>')

    # Cotas de folgas
    linhas.append('    <line x1="110" y1="120" x2="125" y2="120" stroke="#facc15" stroke-width="1.5" />')
    linhas.append('    <text x="95" y="123" text-anchor="end" fill="#facc15" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">folga &lt;= 3mm</text>')

    linhas.append('    <line x1="300" y1="580" x2="300" y2="590" stroke="#4ade80" stroke-width="2" />')
    linhas.append('    <text x="300" y="605" text-anchor="middle" fill="#4ade80" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">Folga no piso &lt;= 10mm</text>')

    linhas.append('    <line x1="50" y1="390" x2="145" y2="390" stroke="#38bdf8" stroke-dasharray="3,3" stroke-width="1.5" />')
    linhas.append('    <text x="45" y="394" text-anchor="end" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="10" font-weight="bold">h = 1,00 m (0,90 a 1,10m)</text>')

    # Linha do piso acabado
    linhas.append('    <line x1="50" y1="590" x2="550" y2="590" stroke="#64748b" stroke-width="3" />')
    linhas.append('    <text x="500" y="610" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10">Piso acabado</text>')

    # Caixa de notas técnicas
    linhas.append('    <rect x="30" y="640" width="540" height="85" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="45" y="665" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">REQUISITOS DE FECHAMENTO AUTOMÁTICO E OPERAÇÃO</text>')
    linhas.append('    <text x="45" y="685" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Fechamento automático obrigatório por mola aérea regulamentar em todas as portas.</text>')
    linhas.append('    <text x="45" y="702" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Folha dupla exige seletor sequencial de fechamento para sobreposição correta do batente.</text>')
    linhas.append('    <text x="45" y="718" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• Força de abertura da barra limitada a 150 N em evacuação emergencial de pânico.</text>')
    linhas.append('  </g>')

    # Painel Direito: Lista de Portas e Diagnóstico
    linhas.append('  <g transform="translate(1030, 120)">')
    linhas.append('    <rect width="380" height="745" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="20" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">PORTAS INSPECIONADAS</text>')
    linhas.append('    <line x1="20" y1="48" x2="360" y2="48" stroke="#334155" stroke-width="1" />')

    y_card = 65
    for p in res.portas[:5]:  # Primeiras 5 portas em destaque
        cor_card = "#166534" if p.conforme_geral else "#991b1b"
        status_card = "CONFORME" if p.conforme_geral else "NÃO CONFORME"
        linhas.append(f'    <rect x="20" y="{y_card}" width="340" height="115" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
        linhas.append(f'    <rect x="20" y="{y_card}" width="8" height="115" rx="3" fill="{cor_card}" />')
        linhas.append(f'    <text x="35" y="{y_card + 22}" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="13" font-weight="bold">{p.identificacao} — {p.classe_especificada.value}</text>')
        linhas.append(f'    <text x="35" y="{y_card + 40}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">{p.ambiente.value}</text>')
        linhas.append(f'    <text x="35" y="{y_card + 58}" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">Vão: {_fmt(p.largura_vao_livre_m, 2)}m x {_fmt(p.altura_vao_livre_m, 2)}m | {p.tipo_folha.value}</text>')
        linhas.append(f'    <text x="35" y="{y_card + 76}" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">Fluxo: {p.capacidade_escoamento_pessoas} pess ({p.unidades_passagem_fornecidas} UP) | Pop: {p.populacao_atendida}</text>')
        cor_txt_st = "#4ade80" if p.conforme_geral else "#f87171"
        linhas.append(f'    <text x="35" y="{y_card + 96}" fill="{cor_txt_st}" font-family="system-ui, sans-serif" font-size="11" font-weight="bold">Status: {status_card}</text>')
        y_card += 125

    # Caixa inferior de certificação
    linhas.append('    <rect x="20" y="650" width="340" height="75" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />')
    linhas.append('    <text x="35" y="675" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">CERTIFICAÇÃO TÉCNICA DE PORTAS</text>')
    linhas.append(f'    <text x="35" y="698" fill="{cor_glo}" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">{status_glo}</text>')
    linhas.append('    <text x="35" y="715" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10">Auditoria Lofrano Tecnologia — NBR 11742 / NBR 11785</text>')
    linhas.append('  </g>')

    linhas.append('</svg>')
    return "\n".join(linhas)
