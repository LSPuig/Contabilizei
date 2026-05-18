"""
Gerador do case Contabilizei em PPTX.
Execução: uv run --with python-pptx --with matplotlib --with kaleido --with plotly python Entrega/gen_pptx.py
"""

from __future__ import annotations

import os
from typing import Callable

import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ---------------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------------

GREEN       = RGBColor(0x00, 0xC1, 0x6E)   # primário
GREEN_DARK  = RGBColor(0x00, 0x9A, 0x57)   # escuro
GREEN_LIGHT = RGBColor(0xD6, 0xF5, 0xE8)   # fundo claro

GRAY_900 = RGBColor(0x1A, 0x1A, 0x2E)
GRAY_700 = RGBColor(0x3D, 0x3D, 0x5C)
GRAY_500 = RGBColor(0x6B, 0x6B, 0x8A)
GRAY_300 = RGBColor(0xB0, 0xB0, 0xC8)
GRAY_100 = RGBColor(0xF4, 0xF4, 0xF9)

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xF5, 0x9E, 0x0B)
RED = RGBColor(0xDC, 0x26, 0x26)
BLUE = RGBColor(0x25, 0x63, 0xEB)

# Dimensões padrão (widescreen 16:9)
SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _rgb(color: RGBColor):
    return color


def _solid_fill(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def _set_text(tf, text: str, font_size: int, bold: bool = False,
              color: RGBColor = GRAY_900, align=PP_ALIGN.LEFT):
    tf.word_wrap = True
    para = tf.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color


def _add_textbox(slide, x, y, w, h, text: str, font_size: int = 11,
                 bold: bool = False, color: RGBColor = GRAY_900,
                 align=PP_ALIGN.LEFT) -> object:
    txb = slide.shapes.add_textbox(x, y, w, h)
    _set_text(txb.text_frame, text, font_size, bold, color, align)
    return txb


def _add_rect(slide, x, y, w, h, fill: RGBColor, line: RGBColor | None = None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        x, y, w, h
    )
    _solid_fill(shape, fill)
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    return shape


def _format_chart(chart, has_legend: bool = True):
    chart.has_legend = has_legend
    if has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    chart.chart_title.has_text_frame = False
    if chart.category_axis:
        chart.category_axis.tick_labels.font.size = Pt(8)
    if chart.value_axis:
        chart.value_axis.tick_labels.font.size = Pt(8)
        chart.value_axis.has_major_gridlines = True


def _add_message(slide, x, y, w, text: str):
    add_callout(slide, x, y, w, Inches(0.55), text, kind="insight")


def _add_source(slide, x, y, w, text: str):
    _add_textbox(slide, x, y, w, Inches(0.2), text, font_size=6, color=GRAY_500)


def _add_table(slide, x, y, w, h, headers, rows, font_size: int = 8):
    table = slide.shapes.add_table(len(rows) + 1, len(headers), x, y, w, h).table
    for col, header in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = header
        _solid_fill(cell, GREEN)
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(font_size)
            p.font.bold = True
            p.font.color.rgb = WHITE
    for row_idx, row in enumerate(rows, start=1):
        for col, value in enumerate(row):
            cell = table.cell(row_idx, col)
            cell.text = str(value)
            _solid_fill(cell, WHITE if row_idx % 2 else GRAY_100)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(font_size)
                p.font.color.rgb = GRAY_700
    return table


# ---------------------------------------------------------------------------
# apply_master — cabeçalho e rodapé globais adicionados via layout placeholder
# ---------------------------------------------------------------------------

def apply_master(prs: Presentation) -> None:
    """
    Configura dimensões do deck e aplica logo + rodapé ao slide master.
    python-pptx não expõe header/footer de forma direta, por isso
    desenhamos as bandas manualmente em cada slide pelo slide_action_title.
    """
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H


# ---------------------------------------------------------------------------
# Primitivos de slide reutilizáveis
# ---------------------------------------------------------------------------

def _add_header_bar(slide, slide_number: int | None = None):
    """Faixa superior verde com logo e número de slide."""
    bar = _add_rect(slide, 0, 0, SLIDE_W, Inches(0.55), GREEN)
    _add_textbox(
        slide,
        Inches(0.2), Inches(0.07),
        Inches(6), Inches(0.42),
        "Case Contabilizei",
        font_size=14, bold=True, color=WHITE,
    )
    if slide_number is not None:
        _add_textbox(
            slide,
            Inches(12.3), Inches(0.07),
            Inches(0.8), Inches(0.42),
            str(slide_number),
            font_size=12, bold=False, color=WHITE,
            align=PP_ALIGN.RIGHT,
        )
    return bar


def _add_footer_bar(slide):
    """Rodapé cinza claro com data e fonte."""
    _add_rect(slide, 0, SLIDE_H - Inches(0.3), SLIDE_W, Inches(0.3), GRAY_100)
    _add_textbox(
        slide,
        Inches(0.2), SLIDE_H - Inches(0.28),
        Inches(10), Inches(0.26),
        "Análise — 2026-05-18  ·  fonte: Pesquisa/",
        font_size=7, color=GRAY_500,
    )


def slide_action_title(
    prs: Presentation,
    title: str,
    body_fn: Callable[[object, float, float, float, float], None],
    slide_number: int | None = None,
) -> object:
    """
    Cria slide estilo McKinsey/Bain:
    - cabeçalho verde fixo
    - faixa de action title abaixo do cabeçalho (título = conclusão, não tópico)
    - área de body disponibilizada para body_fn(slide, x, y, w, h)
    - rodapé fixo
    """
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)

    _add_header_bar(slide, slide_number)
    _add_footer_bar(slide)

    # Faixa de action title
    title_y = Inches(0.55)
    title_h = Inches(0.75)
    _add_rect(slide, 0, title_y, SLIDE_W, title_h, GREEN_LIGHT)
    _add_textbox(
        slide,
        Inches(0.3), title_y + Inches(0.08),
        SLIDE_W - Inches(0.6), title_h - Inches(0.1),
        title,
        font_size=16, bold=True, color=GREEN_DARK,
    )

    # Área de body
    body_y = title_y + title_h + Inches(0.1)
    body_h = SLIDE_H - body_y - Inches(0.35)
    body_fn(slide, Inches(0.3), body_y, SLIDE_W - Inches(0.6), body_h)

    return slide


# ---------------------------------------------------------------------------
# Componentes compostos
# ---------------------------------------------------------------------------

def add_kpi_card(slide, x, y, label: str, value: str, sublabel: str = ""):
    """Card de KPI com rótulo, valor grande e sub-rótulo opcional."""
    w, h = Inches(2.2), Inches(1.4)
    card = _add_rect(slide, x, y, w, h, WHITE, line=GREEN)
    _add_textbox(slide, x + Inches(0.1), y + Inches(0.08),
                 w - Inches(0.2), Inches(0.28),
                 label, font_size=9, color=GRAY_500)
    _add_textbox(slide, x + Inches(0.1), y + Inches(0.38),
                 w - Inches(0.2), Inches(0.5),
                 value, font_size=24, bold=True, color=GREEN_DARK)
    if sublabel:
        _add_textbox(slide, x + Inches(0.1), y + Inches(0.95),
                     w - Inches(0.2), Inches(0.28),
                     sublabel, font_size=8, color=GRAY_500)
    return card


def add_callout(slide, x, y, w, h, text: str, kind: str = "insight"):
    """Caixa de insight ou aviso com borda colorida à esquerda."""
    bg    = GREEN_LIGHT if kind == "insight" else RGBColor(0xFF, 0xF3, 0xCD)
    accent = GREEN      if kind == "insight" else RGBColor(0xFF, 0xA0, 0x00)

    _add_rect(slide, x, y, w, h, bg)
    _add_rect(slide, x, y, Inches(0.07), h, accent)
    _add_textbox(slide, x + Inches(0.15), y + Inches(0.08),
                 w - Inches(0.2), h - Inches(0.12),
                 text, font_size=10, color=GRAY_900)


def add_takeaway_footer(slide, text: str):
    """Faixa de takeaway verde escuro na parte inferior do slide."""
    y = SLIDE_H - Inches(0.85)
    _add_rect(slide, 0, y, SLIDE_W, Inches(0.5), GREEN_DARK)
    _add_textbox(
        slide, Inches(0.3), y + Inches(0.06),
        SLIDE_W - Inches(0.6), Inches(0.38),
        f"▶  {text}",
        font_size=10, bold=True, color=WHITE,
    )


# ---------------------------------------------------------------------------
# Slides individuais
# ---------------------------------------------------------------------------

def slide_01(prs: Presentation):
    """Capa."""
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)

    # Fundo dividido: metade esquerda verde, metade direita branca
    _add_rect(slide, 0, 0, SLIDE_W * 0.45, SLIDE_H, GREEN)
    _add_rect(slide, SLIDE_W * 0.45, 0, SLIDE_W * 0.55, SLIDE_H, WHITE)

    # Título principal
    _add_textbox(
        slide,
        Inches(0.4), Inches(1.8),
        Inches(5.4), Inches(1.6),
        "Case\nContabilizei",
        font_size=40, bold=True, color=WHITE,
    )

    # Subtítulo
    _add_textbox(
        slide,
        Inches(0.4), Inches(3.6),
        Inches(5.4), Inches(0.7),
        "Análise de produto e crescimento",
        font_size=15, color=WHITE,
    )

    # Data + candidato
    _add_textbox(
        slide,
        Inches(0.4), Inches(4.5),
        Inches(5.4), Inches(0.5),
        "Maio 2026",
        font_size=11, color=RGBColor(0xD6, 0xF5, 0xE8),
    )

    # Rodapé
    _add_footer_bar(slide)

    return slide


def slide_02(prs: Presentation):
    """Executive Summary — 5 takeaways das perguntas P1–P5."""
    takeaways = [
        ("P1", "Share comprado",
         "Market share subiu 4,14 % → 5,53 %, mas investimento cresceu "
         "+288,9 % enquanto vendas avançaram só +22,6 %."),
        ("P2", "Funil menos eficiente",
         "CAC saiu de R$ 114 para R$ 362 (+217 %) e conversão Lead→Venda "
         "caiu de 29,6 % para 22,8 %."),
        ("P3", "Saturação evidente",
         "Correlação Investimento↔CAC = 0,934; quatro anomalias apontam "
         "dependência de mídia, sazonalidade e lead menos qualificado."),
        ("P4", "Mercado mudou",
         "MEI digital, Reforma Tributária, IA fiscal, Open Finance e "
         "consolidação redefinem onde capturar crescimento em 2026."),
        ("P5", "Quatro caminhos",
         "Para 6 %+: estratégico e sazonal preservam capital; linear pede "
         "R$ 2,17M/ano e realista R$ 10,1M/ano em mídia (ε = 0,10)."),
    ]

    def body(slide, x, y, w, h):
        card_w = Inches(2.35)
        card_h = Inches(3.2)
        gap    = Inches(0.22)
        total  = 5 * card_w + 4 * gap
        start_x = x + (w - total) / 2

        for i, (tag, label, text) in enumerate(takeaways):
            cx = start_x + i * (card_w + gap)
            cy = y + Inches(0.1)

            # Fundo do card
            _add_rect(slide, cx, cy, card_w, card_h, GRAY_100, line=GRAY_300)

            # Tag colorida
            _add_rect(slide, cx, cy, card_w, Inches(0.38), GREEN)
            _add_textbox(slide, cx + Inches(0.08), cy + Inches(0.04),
                         card_w - Inches(0.1), Inches(0.3),
                         tag, font_size=13, bold=True, color=WHITE)

            # Label
            _add_textbox(slide, cx + Inches(0.1), cy + Inches(0.45),
                         card_w - Inches(0.2), Inches(0.32),
                         label, font_size=10, bold=True, color=GREEN_DARK)

            # Texto
            _add_textbox(slide, cx + Inches(0.1), cy + Inches(0.82),
                         card_w - Inches(0.2), card_h - Inches(1.0),
                         text, font_size=9, color=GRAY_700)

    slide_action_title(
        prs,
        "A Contabilizei ganhou share, mas o motor atual mostra rendimentos decrescentes claros",
        body,
        slide_number=2,
    )


def slide_03(prs: Presentation):
    """P1 — Variação Mercado x Contabilizei."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: o ganho de share veio junto de deterioração severa de eficiência; o mercado não explica sozinho o aumento de CAC.",
        )

        chart_data = CategoryChartData()
        chart_data.categories = ["Vendas", "Leads", "Usuários", "Invest.", "CAC", "Mkt share"]
        chart_data.add_series("Variação YoY", (22.6, 59.1, 44.6, 288.9, 217.0, 33.6))
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.BAR_CLUSTERED,
            x, y + Inches(0.85), Inches(7.1), Inches(4.15),
            chart_data,
        ).chart
        _format_chart(chart, has_legend=False)
        chart.value_axis.axis_title.has_text_frame = True
        chart.value_axis.axis_title.text_frame.text = "Variação abr/21 → abr/22 (%)"

        rows = [
            ("Investimento", "R$ 250k", "R$ 974k", "+288,9%"),
            ("Vendas", "2.190", "2.686", "+22,6%"),
            ("CAC", "R$ 114", "R$ 362", "+217,0%"),
            ("Market share", "4,14%", "5,53%", "+1,39 p.p."),
        ]
        _add_table(
            slide,
            x + Inches(7.45), y + Inches(0.95), Inches(4.95), Inches(2.05),
            ["Métrica", "Abr/21", "Abr/22", "Δ"], rows, font_size=8,
        )
        add_callout(
            slide,
            x + Inches(7.45), y + Inches(3.25), Inches(4.95), Inches(1.1),
            "Sinal de alerta do dataset: o investimento cresceu ~4x mais rápido que as vendas no mesmo período.",
            kind="warning",
        )
        _add_source(slide, x, y + Inches(5.05), w, "Fonte: Pesquisa/02_analise_dados.md, seções 3.1 e Resumo executivo.")
        add_takeaway_footer(slide, "Antes de acelerar mídia, é preciso provar que o CAC marginal ainda cria valor.")

    slide_action_title(
        prs,
        "Investimento quase quadruplicou, mas vendas só +22,6% — o share foi comprado com custo",
        body,
        slide_number=3,
    )


def slide_04(prs: Presentation):
    """P1 — Sazonalidade."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: dezembro distorce a leitura de market share porque o denominador encolhe mais que as vendas.",
        )
        chart_data = CategoryChartData()
        chart_data.categories = [
            "Abr/21", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez", "Jan/22", "Fev", "Mar", "Abr/22",
        ]
        chart_data.add_series("Vendas", (2190, 2326, 2310, 2374, 2488, 2306, 2057, 2030, 1906, 2769, 2574, 2934, 2686))
        chart_data.add_series("Mkt share (%)", (4.14, 3.84, 4.08, 4.20, 4.14, 4.43, 3.63, 3.95, 5.89, 5.04, 5.19, 5.06, 5.53))
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.LINE,
            x, y + Inches(0.8), Inches(8.15), Inches(4.15),
            chart_data,
        ).chart
        _format_chart(chart)

        add_kpi_card(slide, x + Inches(8.55), y + Inches(0.85), "Mercado em dez/21", "32.338", "menor total da série")
        add_kpi_card(slide, x + Inches(10.9), y + Inches(0.85), "Vendas em dez/21", "1.906", "menor volume da série")
        add_kpi_card(slide, x + Inches(8.55), y + Inches(2.55), "Share em dez/21", "5,89%", "pico por denominador")
        add_kpi_card(slide, x + Inches(10.9), y + Inches(2.55), "CAC em dez/21", "R$ 301", "investimento ainda alto")

        add_callout(
            slide,
            x + Inches(8.55), y + Inches(4.25), Inches(4.6), Inches(0.75),
            "Leitura prática: usar dezembro como referência de meta superestima tração real.",
            kind="warning",
        )
        _add_source(slide, x, y + Inches(5.05), w, "Fonte: Pesquisa/02_analise_dados.md, seções 2, 4.1 e 4.5.")
        add_takeaway_footer(slide, "Meta de share deve usar abril/22 ou média recente, não o pico sazonal de dezembro.")

    slide_action_title(
        prs,
        "Dezembro elevou share para 5,89%, mas por contração do mercado — não por tração saudável",
        body,
        slide_number=4,
    )


def slide_05(prs: Presentation):
    """P2 — KPIs."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: os KPIs mostram escala no topo, mas eficiência em queda no meio e fundo do funil.",
        )
        cards = [
            ("CAC médio", "R$ 257", "mín R$ 114 / máx R$ 363"),
            ("Lead→Venda", "26,0%", "29,6% → 22,8% YoY"),
            ("Usuário→Lead", "0,71%", "média do período"),
            ("Usuário→Venda", "0,18%", "média do período"),
            ("Market share", "4,55%", "média; máx 5,89%"),
        ]
        for i, card in enumerate(cards):
            add_kpi_card(slide, x + Inches(0.1) + i * Inches(2.45), y + Inches(0.85), *card)

        rows = [
            ("Usuários", "~1.319.277/mês", "topo de funil"),
            ("Leads", "~9.289/mês", "0,71% dos usuários"),
            ("Vendas", "~2.381/mês", "26,0% dos leads"),
            ("Mercado", "~53.091/mês", "4,55% de share médio"),
        ]
        _add_table(
            slide, x + Inches(0.15), y + Inches(2.75), Inches(6.3), Inches(1.75),
            ["Etapa", "Volume médio", "Leitura"], rows, font_size=9,
        )
        add_callout(
            slide,
            x + Inches(6.9), y + Inches(2.75), Inches(5.7), Inches(1.75),
            "O dataset não traz LTV, MRR, churn, ticket médio ou breakdown por canal; portanto, CAC/LTV e ROAS por canal não são calculáveis.",
            kind="warning",
        )
        _add_source(slide, x, y + Inches(5.05), w, "Fonte: Pesquisa/02_analise_dados.md, seções 1, 2, 3.1 e 5.")
        add_takeaway_footer(slide, "O gargalo mensurável está na qualidade/fechamento dos leads, não na falta de audiência.")

    slide_action_title(
        prs,
        "Topo de funil escala, mas conversão e CAC contam outra história",
        body,
        slide_number=5,
    )


def slide_06(prs: Presentation):
    """P2 — Tendências mensais."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: mês a mês, CAC sobe enquanto a conversão Lead→Venda cai — o funil fica mais caro e menos seletivo.",
        )
        months = ["Abr/21", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez", "Jan/22", "Fev", "Mar", "Abr/22"]
        cac = (114.34, 144.57, 165.05, 185.23, 291.07, 269.02, 265.96, 272.04, 300.81, 324.74, 319.25, 321.14, 362.51)
        conv = (29.63, 28.80, 24.91, 31.70, 27.89, 26.41, 24.55, 25.84, 24.93, 22.39, 23.15, 24.95, 22.84)

        cac_data = CategoryChartData()
        cac_data.categories = months
        cac_data.add_series("CAC (R$)", cac)
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.LINE, x, y + Inches(0.8), Inches(6.1), Inches(3.65), cac_data,
        ).chart
        _format_chart(chart, has_legend=False)

        conv_data = CategoryChartData()
        conv_data.categories = months
        conv_data.add_series("Lead→Venda (%)", conv)
        chart2 = slide.shapes.add_chart(
            XL_CHART_TYPE.LINE, x + Inches(6.55), y + Inches(0.8), Inches(6.1), Inches(3.65), conv_data,
        ).chart
        _format_chart(chart2, has_legend=False)

        rows = [
            ("Vendas", "+37 unidades/mês", "positivo"),
            ("Investimento", "+R$ 55.715/mês", "crescente"),
            ("CAC", "+R$ 18,84/mês", "piora"),
            ("Conv. L→V", "−0,56 p.p./mês", "piora"),
            ("Market share", "+0,13 p.p./mês", "positivo"),
        ]
        _add_table(slide, x + Inches(2.0), y + Inches(4.55), Inches(8.7), Inches(0.75), ["Métrica", "Tendência linear", "Direção"], rows, font_size=7)
        _add_source(slide, x, y + Inches(5.35), w, "Fonte: Pesquisa/02_analise_dados.md, seções 2 e 3.2.")
        add_takeaway_footer(slide, "A trajetória mensal reforça rendimentos decrescentes: crescer volume exigiu aceitar CAC maior.")

    slide_action_title(
        prs,
        "A tendência mensal é inequívoca: CAC +R$18,84/mês e conversão −0,56 p.p./mês",
        body,
        slide_number=6,
    )


def _build_heatmap_png(out_path: str):
    labels = ["Invest.", "Usuários", "Leads", "Vendas", "CAC"]
    data = [
        [1.000, 0.906, 0.866, 0.716, 0.934],
        [0.906, 1.000, 0.735, 0.585, 0.876],
        [0.866, 0.735, 1.000, 0.864, 0.679],
        [0.716, 0.585, 0.864, 1.000, 0.421],
        [0.934, 0.876, 0.679, 0.421, 1.000],
    ]
    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=180)
    im = ax.imshow(data, cmap="YlGn", vmin=0.35, vmax=1.0)
    ax.set_xticks(range(len(labels)), labels=labels)
    ax.set_yticks(range(len(labels)), labels=labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            weight = "bold" if {i, j} == {0, 4} else "normal"
            ax.text(j, i, f"{data[i][j]:.3f}", ha="center", va="center", fontsize=9, fontweight=weight)
    ax.set_title("Correlação entre métricas do funil", fontsize=12, pad=10)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def slide_07(prs: Presentation):
    """P3 — Heatmap correlação."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: a relação mais forte do dataset é Investimento↔CAC, evidência de saturação ou rendimento marginal decrescente.",
        )
        heatmap_path = os.path.join(os.path.dirname(__file__), "heatmap_corr.png")
        _build_heatmap_png(heatmap_path)
        slide.shapes.add_picture(heatmap_path, x + Inches(0.4), y + Inches(0.8), width=Inches(6.45))
        add_callout(
            slide,
            x + Inches(7.2), y + Inches(1.05), Inches(5.15), Inches(1.25),
            "Correlação Investimento↔CAC = 0,934: mais gasto não converte proporcionalmente em vendas; compra custo.",
            kind="warning",
        )
        rows = [
            ("Investimento↔CAC", "0,934", "sinal mais relevante"),
            ("Investimento↔Vendas", "0,716", "cresce, mas menos"),
            ("Leads↔Vendas", "0,864", "volume ainda importa"),
            ("Vendas↔CAC", "0,421", "baixo alinhamento"),
        ]
        _add_table(slide, x + Inches(7.2), y + Inches(2.65), Inches(5.15), Inches(1.55), ["Par", "Correlação", "Leitura"], rows, font_size=8)
        _add_source(slide, x, y + Inches(5.15), w, "Fonte: Pesquisa/02_analise_dados.md, seção 3.4.")
        add_takeaway_footer(slide, "A pergunta não é quanto aumentar o investimento; é onde o investimento deixa de render.")

    slide_action_title(
        prs,
        "Correlação Inv↔CAC de 0,934 mostra que o motor atual compra custo junto com crescimento",
        body,
        slide_number=7,
    )


def slide_08(prs: Presentation):
    """P3 — Anomalias."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: quatro anomalias explicam por que projeções lineares de crescimento subestimam risco operacional.",
        )
        xy = XyChartData()
        series = xy.add_series("Meses")
        points = [
            (250.407, 114.34), (336.276, 144.57), (381.262, 165.05), (439.728, 185.23),
            (724.186, 291.07), (620.353, 269.02), (547.078, 265.96), (552.240, 272.04),
            (573.339, 300.81), (899.200, 324.74), (821.753, 319.25), (942.215, 321.14), (973.712, 362.51),
        ]
        for px, py in points:
            series.add_data_point(px, py)
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.XY_SCATTER, x, y + Inches(0.85), Inches(6.2), Inches(3.75), xy,
        ).chart
        _format_chart(chart, has_legend=False)
        chart.category_axis.axis_title.has_text_frame = True
        chart.category_axis.axis_title.text_frame.text = "Investimento (R$ mil)"
        chart.value_axis.axis_title.has_text_frame = True
        chart.value_axis.axis_title.text_frame.text = "CAC (R$)"

        rows = [
            ("Dez/21", "Menor mercado (32.338) e vendas (1.906), mas share 5,89%"),
            ("Jan/22", "Leads +61,7% m/m; conversão cai para 22,39%"),
            ("Novos usuários", "Faixa estrutural de 81,7% a 85,9% dos usuários"),
            ("Inv × vendas", "Investimento +288,9% vs vendas +22,6%"),
        ]
        _add_table(slide, x + Inches(6.65), y + Inches(0.95), Inches(5.9), Inches(2.4), ["Anomalia", "Evidência literal"], rows, font_size=8)
        add_callout(
            slide,
            x + Inches(6.65), y + Inches(3.6), Inches(5.9), Inches(0.95),
            "Interpretação: campanha de maior volume parece ter trazido lead menos qualificado e dependência de tráfego novo.",
            kind="insight",
        )
        _add_source(slide, x, y + Inches(5.05), w, "Fonte: Pesquisa/02_analise_dados.md, seção 4.")
        add_takeaway_footer(slide, "As anomalias apontam para qualificação, sazonalidade e canal, não apenas para orçamento.")

    slide_action_title(
        prs,
        "Quatro anomalias mostram um funil dependente de mídia, sazonalidade e lead menos qualificado",
        body,
        slide_number=8,
    )


def slide_09(prs: Presentation):
    """P4 — Mercado 2026."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: 2026 redefine o TAM: abertura de empresa é só uma camada; o valor migra para automação fiscal e verticalização.",
        )
        rows = [
            ("MEI digital", "4,6M novos pequenos negócios em 2025; MEIs = 77% das aberturas", "produto vertical"),
            ("Creator economy", "2M influenciadores no Brasil; +67% em 12 meses", "novo funil"),
            ("E-commerce MPE", "R$ 67 bi em 2024; +1.200% desde 2019", "integrações"),
            ("Reforma Tributária", "2026–2033; campos IBS/CBS obrigatórios nos DF-e", "urgência fiscal"),
            ("Open Finance", "picos de 4 bi chamadas/semana em 2025", "conciliação automática"),
            ("Consolidação", "85k empresas contábeis; M&A Brasil +71% no H1/25", "M&A/carteiras"),
        ]
        _add_table(slide, x + Inches(0.2), y + Inches(0.95), Inches(12.1), Inches(3.25), ["Tendência", "Evidência", "Implicação"], rows, font_size=8)
        add_callout(
            slide,
            x + Inches(1.1), y + Inches(4.45), Inches(10.3), Inches(0.75),
            "O TAM mensal de ~53k aberturas da planilha mede aquisição; não mede monetização pós-abertura nem complexidade fiscal crescente.",
            kind="insight",
        )
        _add_source(slide, x, y + Inches(5.3), w, "Fonte: Pesquisa/05_tendencias.md, seções 1–5.")
        add_takeaway_footer(slide, "A oportunidade 2026 é capturar segmentos e obrigações novas, não só mais cliques para abertura.")

    slide_action_title(
        prs,
        "O mercado de 2026 favorece quem automatiza complexidade fiscal para o novo MEI digital",
        body,
        slide_number=9,
    )


def slide_10(prs: Presentation):
    """P4 — Concorrência."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: o diferencial da Contabilizei é o cruzamento banking + ERP + contabilidade, mas concorrentes atacam pelas bordas.",
        )
        rows = [
            ("Conta Azul", "ERP", "R$ 160–R$ 720", "cliente mantém contador separado"),
            ("Omie", "ERP + rede", "a partir de R$ 99", "10k+ contadores parceiros"),
            ("Nubank PJ", "banking", "gratuito", "100M+ clientes PF como funil"),
            ("Stone PJ", "banking/adquirência", "gratuito", "2,1M PJs e principalidade"),
            ("Cora", "banking", "gratuito / Pro R$ 44,90", "parcerias com escritórios"),
            ("BPO tradicional", "contabilidade", "R$ 800–R$ 1.500+", "advisory e relacionamento"),
            ("Autônomos", "contabilidade", "R$ 150–R$ 450", "personalização e preço"),
        ]
        _add_table(slide, x + Inches(0.15), y + Inches(0.9), Inches(12.2), Inches(3.45), ["Player", "Camada", "Ticket", "Ameaça principal"], rows, font_size=7)
        add_callout(
            slide,
            x + Inches(0.75), y + Inches(4.55), Inches(11.1), Inches(0.75),
            "Síntese do mapeamento: nenhum concorrente cobre simultaneamente banking + ERP + contabilidade para MEI/ME; esse é o moat convertível em crescimento.",
            kind="insight",
        )
        _add_source(slide, x, y + Inches(5.35), w, "Fonte: Pesquisa/04_concorrentes.md, seções 2 e 4.")
        add_takeaway_footer(slide, "Defender passivamente o moat é insuficiente; Nubank, Stone, Cora e Omie podem fechar o gap pela borda.")

    slide_action_title(
        prs,
        "A Contabilizei é única nas três camadas, mas bancos e ERPs têm distribuição para invadir contabilidade",
        body,
        slide_number=10,
    )


def slide_11(prs: Presentation):
    """P4 — Três alavancas."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: para chegar a 6% e além, o mix vencedor troca dependência de mídia por eficiência, distribuição e produto vertical.",
        )
        rows = [
            ("1. Eficiência de funil", "Recuperar conversão L→V para patamar inicial", "29,6% em abr/21 vs 22,8% em abr/22", "mais vendas sem mídia incremental"),
            ("2. Distribuição B2B2C", "White-label/API para marketplaces, fintechs e creators", "Canais já concentram MEI digital", "CAC próximo de zero via parceiro"),
            ("3. Produto vertical + IA", "MEI digital + agente Reforma Tributária", "IBS/CBS 2026; IA fiscal ainda pouco madura", "ARPU/LTV maior e diferenciação"),
        ]
        _add_table(slide, x + Inches(0.25), y + Inches(0.95), Inches(12.0), Inches(2.4), ["Alavanca", "Ação", "Base factual", "Impacto esperado"], rows, font_size=8)

        chart_data = CategoryChartData()
        chart_data.categories = ["Linear: mídia", "Estratégico: mix"]
        chart_data.add_series("Dependência de CAC", (100, 35))
        chart_data.add_series("Qualidade/distribuição/produto", (20, 100))
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.BAR_CLUSTERED,
            x + Inches(2.1), y + Inches(3.65), Inches(8.4), Inches(1.55),
            chart_data,
        ).chart
        _format_chart(chart)

        _add_source(slide, x, y + Inches(5.35), w, "Fonte: Apresentação/00_storyline.md, mensagens 1–5; Pesquisa/02_analise_dados.md e 05_tendencias.md.")
        add_takeaway_footer(slide, "Recomendação: financiar 6% com mix de eficiência + B2B2C + verticalização, usando mídia como complemento.")

    slide_action_title(
        prs,
        "Três alavancas mudam a curva: eficiência de funil, B2B2C e produto vertical com IA fiscal",
        body,
        slide_number=11,
    )


def slide_12(prs: Presentation):
    """P5 — Quatro caminhos para 6% lado a lado."""

    paths = [
        {
            "tag": "1. Linear",
            "tag_color": GRAY_500,
            "title": "Regra de três simples",
            "value": "R$ 2,17M/ano",
            "sub": "+R$ 181k/mês",
            "premise": "CAC médio R$ 362 × 500 vendas/mês adicionais.",
            "weakness": "Ignora retornos decrescentes: piso teórico, não plano executável.",
        },
        {
            "tag": "2. Realista",
            "tag_color": ORANGE,
            "title": "Elasticidade investimento-vendas",
            "value": "R$ 10,1M/ano",
            "sub": "+R$ 841k/mês",
            "premise": "CAC_marginal = CAC_base·(V_alvo/V_atual)^((1−ε)/ε), ε = 0,10 (baixa elasticidade investimento↔vendas observada).",
            "weakness": "Resultado sensível à premissa de ε: variações pequenas em torno de 0,10 alteram o investimento incremental em ordens de grandeza.",
        },
        {
            "tag": "3. Estratégico",
            "tag_color": GREEN_DARK,
            "title": "Eficiência de funil",
            "value": "R$ 0",
            "sub": "investimento incremental",
            "premise": "Conv L→V de 22,8% → 27,8% com os ~11.700 leads/mês atuais ⇒ ~3.253 vendas (acima da meta de 3.186).",
            "weakness": "Exige operação: qualificação de lead, scoring, atendimento. Aritmética reversa só funciona com plano.",
        },
        {
            "tag": "4. Sazonal (novo)",
            "tag_color": BLUE,
            "title": "Realocação proporcional",
            "value": "R$ 0",
            "sub": "mesmo orçamento total",
            "premise": "CAC_mês = CAC_base·(Mercado_médio/Mercado_mês)^γ, γ = 0,5; concentrar verba nos meses de maior abertura captura 6% sem aumentar gasto.",
            "weakness": "Depende de confirmar a curva sazonal em séries longas; risco de ruído estrutural.",
        },
    ]

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: a meta de 6% pode ser perseguida por quatro caminhos — só dois deles dependem de cheque incremental relevante.",
        )

        card_w = Inches(2.95)
        card_h = Inches(4.05)
        gap    = Inches(0.18)
        total  = 4 * card_w + 3 * gap
        start_x = x + (w - total) / 2
        cy = y + Inches(0.75)

        for i, p in enumerate(paths):
            cx = start_x + i * (card_w + gap)
            _add_rect(slide, cx, cy, card_w, card_h, WHITE, line=GRAY_300)
            _add_rect(slide, cx, cy, card_w, Inches(0.42), p["tag_color"])
            _add_textbox(slide, cx + Inches(0.12), cy + Inches(0.05),
                         card_w - Inches(0.2), Inches(0.34),
                         p["tag"], font_size=12, bold=True, color=WHITE)

            _add_textbox(slide, cx + Inches(0.12), cy + Inches(0.5),
                         card_w - Inches(0.2), Inches(0.32),
                         p["title"], font_size=10, bold=True, color=GREEN_DARK)
            _add_textbox(slide, cx + Inches(0.12), cy + Inches(0.85),
                         card_w - Inches(0.2), Inches(0.55),
                         p["value"], font_size=22, bold=True, color=p["tag_color"])
            _add_textbox(slide, cx + Inches(0.12), cy + Inches(1.45),
                         card_w - Inches(0.2), Inches(0.28),
                         p["sub"], font_size=9, color=GRAY_500)

            _add_textbox(slide, cx + Inches(0.12), cy + Inches(1.78),
                         card_w - Inches(0.2), Inches(0.28),
                         "Premissa", font_size=8, bold=True, color=GRAY_700)
            _add_textbox(slide, cx + Inches(0.12), cy + Inches(2.02),
                         card_w - Inches(0.2), Inches(1.0),
                         p["premise"], font_size=8, color=GRAY_700)

            _add_textbox(slide, cx + Inches(0.12), cy + Inches(3.0),
                         card_w - Inches(0.2), Inches(0.28),
                         "Leitura crítica", font_size=8, bold=True, color=GRAY_700)
            _add_textbox(slide, cx + Inches(0.12), cy + Inches(3.24),
                         card_w - Inches(0.2), Inches(0.78),
                         p["weakness"], font_size=8, color=GRAY_700)

        _add_source(slide, x, y + Inches(5.18), w, "Fonte: Entrega/index.html (Simuladores 1–4); Apresentação/00_storyline.md, mensagem 5.")
        add_takeaway_footer(slide, "Apresentar os quatro caminhos lado a lado; defender estratégico + sazonal como o mix de menor custo e menor risco de saturação.")

    slide_action_title(
        prs,
        "Quatro caminhos para 6%: dois exigem cheque, dois pedem operação — só dois são defensáveis",
        body,
        slide_number=12,
    )


def slide_13(prs: Presentation):
    """P5 — Defesa do estratégico + sazonal com barras comparativas."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: o investimento incremental anual entre os caminhos varia em ordens de grandeza; o ônus de provar valor recai sobre o realista, não sobre a operação.",
        )

        chart_data = CategoryChartData()
        chart_data.categories = ["Linear", "Realista (auditado)", "Estratégico", "Sazonal (novo)"]
        chart_data.add_series("Investimento incremental anual (R$ M)", (2.17, 16.09, 0.0, 0.0))
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.COLUMN_CLUSTERED,
            x, y + Inches(0.8), Inches(7.1), Inches(4.2),
            chart_data,
        ).chart
        _format_chart(chart, has_legend=False)
        chart.value_axis.axis_title.has_text_frame = True
        chart.value_axis.axis_title.text_frame.text = "R$ milhões/ano"

        # Tabela comparativa lateral
        rows = [
            ("Estratégico", "R$ 0 incremental", "+5 p.p. de conversão"),
            ("Sazonal", "R$ 0 incremental", "Mesmo orçamento, melhor timing"),
            ("Linear", "R$ 2,17M/ano", "Piso teórico, sem saturação"),
            ("Realista", "R$ 16,1M/ano", "Custo real via mídia (ε=0,197)"),
        ]
        _add_table(
            slide,
            x + Inches(7.45), y + Inches(0.85), Inches(4.95), Inches(1.95),
            ["Cenário", "Investimento", "Mecanismo"], rows, font_size=8,
        )

        add_callout(
            slide,
            x + Inches(7.45), y + Inches(2.95), Inches(4.95), Inches(0.95),
            "Por que defender estratégico + sazonal: ambos preservam capital, atacam o sinal mais forte do dataset (correlação Inv↔CAC=0,934) e respondem ao gargalo real (qualidade de lead, não volume).",
            kind="insight",
        )
        add_callout(
            slide,
            x + Inches(7.45), y + Inches(4.0), Inches(4.95), Inches(1.0),
            "Como apresentar à banca: o realista define o teto de custo via mídia; estratégico+sazonal mostram que 6% é alcançável antes mesmo de gastar mais.",
            kind="warning",
        )

        _add_source(slide, x, y + Inches(5.05), w, "Fonte: Pesquisa/06_auditoria_realista.md (Tabela V); Entrega/index.html (Simuladores 2 e 4).")
        add_takeaway_footer(slide, "Recomendação: financiar 6% por eficiência + sazonalidade; manter o cheque do realista como contingência, não como plano A.")

    slide_action_title(
        prs,
        "Defendemos o caminho estratégico + sazonal: zero incremental contra R$ 16,1M do caminho via mídia",
        body,
        slide_number=13,
    )


def slide_14(prs: Presentation):
    """Plano 0-30 / 30-90 / 3-12 meses — timeline horizontal."""

    horizons = [
        {
            "tag": "0–30 dias",
            "title": "Diagnóstico e quick wins",
            "color": GREEN,
            "items": [
                "Auditoria de origem dos leads: breakdown por canal, custo, conversão e qualidade.",
                "Implementar lead scoring com base em intenção (formulário, página, fonte).",
                "Plano-piloto de realocação sazonal: reduzir verba em meses de baixa, reforçar mai-jun e mar-abr.",
                "Definir KPIs de funil por canal (CAC, L→V, retenção 90d).",
            ],
        },
        {
            "tag": "30–90 dias",
            "title": "Eficiência + B2B2C piloto",
            "color": GREEN_DARK,
            "items": [
                "Programa de qualificação de leads: SDR/automação para puxar conv L→V de 22,8% rumo a 27%.",
                "Piloto B2B2C: 1–2 parceiros (Mercado Livre, Shopee ou Hotmart) com white-label de abertura.",
                "Roadmap de produto vertical MEI digital: emissão de NF, conciliação, repasses de plataforma.",
                "Modelo de M&A de carteira: critérios, ticket-alvo e CAC equivalente.",
            ],
        },
        {
            "tag": "3–12 meses",
            "title": "Escala e diferenciação",
            "color": GREEN_DARK,
            "items": [
                "Lançar agente IA para Reforma Tributária (IBS/CBS) — diferenciação 2026–2033.",
                "Escalar parcerias B2B2C para 5+ canais; medir CAC blended e ARPU/LTV.",
                "Aquisição de 2–3 carteiras de escritórios fragmentados (M&A) com pricing modelado.",
                "Re-avaliar meta 6% → 7%+ se conv L→V e B2B2C entregarem; só então retomar cheque incremental.",
            ],
        },
    ]

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: sequenciar diagnóstico → eficiência/B2B2C → escala; cada horizonte só desbloqueia o seguinte com prova de valor.",
        )

        col_w = Inches(4.0)
        col_h = Inches(4.05)
        gap   = Inches(0.18)
        total = 3 * col_w + 2 * gap
        start_x = x + (w - total) / 2
        cy = y + Inches(0.85)

        # Linha base da timeline
        line_y = cy + Inches(0.22)
        _add_rect(slide, start_x, line_y, total, Inches(0.04), GREEN)

        for i, hz in enumerate(horizons):
            cx = start_x + i * (col_w + gap)
            # Marker
            marker_x = cx + col_w / 2 - Inches(0.12)
            _add_rect(slide, marker_x, line_y - Inches(0.1), Inches(0.24), Inches(0.24), hz["color"])

            # Card
            card_y = cy + Inches(0.5)
            _add_rect(slide, cx, card_y, col_w, col_h - Inches(0.5), WHITE, line=GRAY_300)
            _add_rect(slide, cx, card_y, col_w, Inches(0.42), hz["color"])
            _add_textbox(slide, cx + Inches(0.15), card_y + Inches(0.05),
                         col_w - Inches(0.3), Inches(0.34),
                         hz["tag"], font_size=12, bold=True, color=WHITE)

            _add_textbox(slide, cx + Inches(0.15), card_y + Inches(0.5),
                         col_w - Inches(0.3), Inches(0.32),
                         hz["title"], font_size=11, bold=True, color=GREEN_DARK)

            items_txb = slide.shapes.add_textbox(
                cx + Inches(0.15), card_y + Inches(0.85),
                col_w - Inches(0.3), col_h - Inches(1.4),
            )
            tf = items_txb.text_frame
            tf.word_wrap = True
            for j, item in enumerate(hz["items"]):
                para = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                para.alignment = PP_ALIGN.LEFT
                run = para.add_run()
                run.text = "• " + item
                run.font.size = Pt(8)
                run.font.color.rgb = GRAY_700

        _add_source(slide, x, y + Inches(5.18), w, "Fonte: Apresentação/00_storyline.md (mensagens 2, 4 e 5); Pesquisa/05_tendencias.md; Pesquisa/04_concorrentes.md.")
        add_takeaway_footer(slide, "Sem cheque adicional nos 90 primeiros dias: o objetivo é provar que estratégico+sazonal entregam antes de ampliar o orçamento.")

    slide_action_title(
        prs,
        "Plano em três horizontes: diagnóstico imediato, eficiência+B2B2C no curto prazo, escala e M&A no médio",
        body,
        slide_number=14,
    )


def slide_15(prs: Presentation):
    """Considerações finais — conclusão + próximos tópicos de pesquisa."""

    def body(slide, x, y, w, h):
        # Coluna esquerda: conclusão geral
        col_w = Inches(6.0)
        col_x = x

        _add_textbox(
            slide, col_x, y + Inches(0.1),
            col_w, Inches(0.35),
            "Conclusão consolidada",
            font_size=12, bold=True, color=GREEN_DARK,
        )

        conclusion = (
            "A Contabilizei comprou +1,39 p.p. de market share triplicando o investimento — "
            "evidência clara de rendimentos decrescentes (correlação Inv↔CAC=0,934, conv L→V "
            "29,6%→22,8%). O caminho para 6%+ não está em acelerar o mesmo motor, mas em "
            "re-alavancar três motores subutilizados: eficiência de funil, distribuição B2B2C "
            "e produtos verticais para o novo MEI digital.\n\n"
            "Entre os quatro caminhos para a meta, dois preservam capital (estratégico e "
            "sazonal); o caminho realista, recalibrado pela auditoria (R$ 16,1M/ano), "
            "define o teto de custo via mídia e justifica priorizar operação antes de cheque.\n\n"
            "A tese da Warburg Pincus (IA + automação fiscal) e os movimentos recentes "
            "(Contabilizei.bank, Multibenefícios, parcerias B2B2C) confirmam a direção — o "
            "que mudamos é a prioridade relativa e a ancoragem nos números da planilha."
        )
        txb = slide.shapes.add_textbox(col_x, y + Inches(0.5), col_w, Inches(4.5))
        tf = txb.text_frame
        tf.word_wrap = True
        for i, para_text in enumerate(conclusion.split("\n\n")):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = PP_ALIGN.LEFT
            run = para.add_run()
            run.text = para_text
            run.font.size = Pt(10)
            run.font.color.rgb = GRAY_700
            para.space_after = Pt(6)

        # Coluna direita: próximos tópicos de pesquisa
        right_x = x + Inches(6.35)
        right_w = w - Inches(6.35)

        _add_textbox(
            slide, right_x, y + Inches(0.1),
            right_w, Inches(0.35),
            "Próximos tópicos de pesquisa",
            font_size=12, bold=True, color=GREEN_DARK,
        )

        rows = [
            ("LTV / CAC por coorte", "Justifica ou não a aquisição incremental atual"),
            ("Breakdown de canal e ROAS", "Onde há saturação real vs escala eficiente"),
            ("Qualidade de lead por origem", "Decide entre cortar mídia ou corrigir venda"),
            ("Churn, MRR, ticket, expansão", "Quanto cresce margem após a venda"),
            ("Eficácia das parcerias B2B2C", "B2B2C já é motor ou ainda hipótese"),
            ("Benchmark CAC vs concorrentes", "Ineficiência específica ou estrutural"),
            ("Viabilidade do produto MEI digital", "Roadmap rápido vs concorrentes pela borda"),
            ("Sazonalidade em séries longas", "Confirma curva para planejamento de mídia"),
            ("Modelo de M&A de carteiras", "Aquisição não orgânica vs CAC orgânico"),
        ]
        _add_table(
            slide,
            right_x, y + Inches(0.5), right_w, Inches(4.5),
            ["Tópico", "Por que importa"], rows, font_size=8,
        )

        _add_source(slide, x, y + Inches(5.18), w, "Fonte: Entrega/index.html (Considerações finais); Apresentação/00_storyline.md (tese central e mensagens 1–5).")
        add_takeaway_footer(slide, "A entrega vira plano de growth para diretor: o que sabemos, o que ainda precisamos saber e a sequência de decisões.")

    slide_action_title(
        prs,
        "Conclusão: 6% via operação primeiro, cheque depois — e nove perguntas que sustentam a decisão de growth",
        body,
        slide_number=15,
    )


def slide_16(prs: Presentation):
    """Apêndice — pontos cegos do dataset."""

    def body(slide, x, y, w, h):
        _add_message(
            slide, x, y, w,
            "Mensagem central: a planilha cobre só aquisição em 13 meses; decisões sobre LTV, canal e retenção dependem de dados que não estão nela.",
        )

        rows = [
            ("LTV, MRR, churn e expansão", "Sem retenção, não há CAC/LTV ratio — base do business de assinatura.",
             "Pedir cohort analysis 24m da base atual; expandir simuladores com payback."),
            ("Breakdown por canal", "Investimento aparece consolidado; impossível separar Google, Meta, SEO, indicação e parceiros.",
             "Sem isso, qualquer recomendação de realocação é direcional, não cirúrgica."),
            ("Qualidade de lead por origem", "Conversão L→V caiu 6,8 p.p. mas a planilha não distingue lead vindo de marca, SEO ou paid.",
             "É o gargalo que mais sangra valor; primeira prioridade de pesquisa adicional."),
            ("ARPU / ticket médio", "Sem preço médio nem mix de produto (contábil x banking x multibenefícios), receita projetada vira chute.",
             "Reforma Tributária e cross-sell mudam ARPU; precisamos do baseline."),
            ("Sazonalidade em série longa", "Apenas 13 meses; dez/21 sozinho domina conclusões sobre realocação sazonal.",
             "Validar curva com 5+ anos antes de comprometer plano sazonal."),
            ("Concorrentes e benchmarks externos", "Não há CAC, churn nem conversão de Conta Azul, Omie, Nubank PJ.",
             "Sem benchmark, não dá para saber se ineficiência é Contabilizei ou de mercado."),
            ("Coorte pós-venda (D30, D90, D365)", "Dataset corta no instante da venda; nada sobre ativação, retenção precoce ou downgrade.",
             "Em SaaS, retenção precoce define se aquisição compõe ou destrói valor."),
        ]
        _add_table(
            slide, x + Inches(0.1), y + Inches(0.95), w - Inches(0.2), Inches(3.45),
            ["Ponto cego", "O que falta", "Impacto na recomendação"], rows, font_size=8,
        )

        add_callout(
            slide,
            x + Inches(0.5), y + Inches(4.5), w - Inches(1.0), Inches(0.7),
            "Apontar lacunas é maturidade, não desculpa: a tese central segue em pé, mas o passo seguinte exige instrumentação interna mais granular antes de comprometer capital adicional.",
            kind="insight",
        )

        _add_source(slide, x, y + Inches(5.3), w, "Fonte: Pesquisa/02_analise_dados.md §5; Apresentação/00_storyline.md (so what e R3).")
        add_takeaway_footer(slide, "Ponto cego ≠ omissão: cada lacuna abaixo muda a recomendação se preenchida.")

    slide_action_title(
        prs,
        "Apêndice — sete pontos cegos da planilha que mudam a recomendação se preenchidos",
        body,
        slide_number=16,
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    prs = Presentation()
    apply_master(prs)

    slide_01(prs)
    slide_02(prs)
    slide_03(prs)
    slide_04(prs)
    slide_05(prs)
    slide_06(prs)
    slide_07(prs)
    slide_08(prs)
    slide_09(prs)
    slide_10(prs)
    slide_11(prs)
    slide_12(prs)
    slide_13(prs)
    slide_14(prs)
    slide_15(prs)
    slide_16(prs)

    out_path = os.path.join(os.path.dirname(__file__), "case_contabilizei.pptx")
    prs.save(out_path)
    print(f"Salvo em {out_path}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
