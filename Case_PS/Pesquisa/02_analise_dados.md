# Análise de Dados — Case Growth Novos Negócios

**Fonte:** `Referencias/Case-Growth-NovosNegocios.xlsx`  
**Período:** Abril/2021 – Abril/2022 (13 meses)  
**Gerado em:** 2026-05-17

---

## 1. Métricas-chave identificadas

### Métricas diretamente presentes na planilha

| Métrica | Descrição | Natureza |
|---------|-----------|----------|
| Usuários | Visitantes únicos mensais do site | Topo de funil |
| Novos Usuários | Visitantes pela primeira vez | Aquisição |
| Leads | Interessados em abrir empresa pela Contabilizei | Meio de funil |
| Vendas | Clientes que efetivamente abriram empresa | Fundo de funil |
| Investimento | Gasto total em marketing | Custo de aquisição |
| Mercado de Abertura | Total de empresas abertas no mercado | TAM mensal |

### Métricas derivadas calculadas

> Market Share estava no glossário mas ausente da planilha — confirmado como derivada.  
> CAC, conversões e taxa de novos usuários foram calculados a partir das colunas disponíveis.  
> **Não há dados de LTV, MRR, churn ou ticket médio** — a planilha cobre exclusivamente a etapa de aquisição.

| Métrica Derivada | Fórmula | Mín | Máx | Média | Mediana |
|-----------------|---------|-----|-----|-------|---------|
| CAC (R$) | Investimento / Vendas | 114,34 | 362,51 | 256,59 | 272,04 |
| Conv. Lead → Venda (%) | Vendas / Leads | 22,39% | 31,70% | 26,00% | 24,95% |
| Conv. Usuário → Lead (%) | Leads / Usuários | 0,57% | 0,93% | 0,71% | 0,71% |
| Conv. Usuário → Venda (%) | Vendas / Usuários | 0,15% | 0,23% | 0,18% | 0,18% |
| Market Share (%) | Vendas / Mercado Abertura | 3,63% | 5,89% | 4,55% | 4,20% |
| Taxa Novos Usuários (%) | Novos / Usuários | 81,72% | 85,86% | 83,17% | 82,90% |
| CPL — Custo por Lead (R$) | Investimento / Leads | 33,88 | 82,81 | 65,21 | 71,06 |

---

## 2. Funil de aquisição — visão geral

```
Mercado (TAM mensal)  ~53.091 aberturas/mês
        ↓
Usuários              ~1.319.277/mês  (sem relação causal direta com TAM)
        ↓  0,71%
Leads                    ~9.289/mês
        ↓  26,0%
Vendas                   ~2.381/mês   →  ~4,55% do mercado total
```

### Tabela completa mês a mês

| Mês | Vendas | Leads | Investimento (R$) | CAC (R$) | L→V (%) | Mkt Share (%) |
|-----|-------:|------:|------------------:|---------:|--------:|--------------:|
| Abr/2021 | 2.190 | 7.392 | 250.407 | 114,34 | 29,63% | 4,14% |
| Mai/2021 | 2.326 | 8.075 | 336.276 | 144,57 | 28,80% | 3,84% |
| Jun/2021 | 2.310 | 9.273 | 381.262 | 165,05 | 24,91% | 4,08% |
| Jul/2021 | 2.374 | 7.489 | 439.728 | 185,23 | 31,70% | 4,20% |
| Ago/2021 | 2.488 | 8.921 | 724.186 | 291,07 | 27,89% | 4,14% |
| Set/2021 | 2.306 | 8.730 | 620.353 | 269,02 | 26,41% | 4,43% |
| Out/2021 | 2.057 | 8.378 | 547.078 | 265,96 | 24,55% | 3,63% |
| Nov/2021 | 2.030 | 7.855 | 552.240 | 272,04 | 25,84% | 3,95% |
| Dez/2021 | 1.906 | 7.645 | 573.339 | 300,81 | 24,93% | 5,89% |
| Jan/2022 | 2.769 | 12.368 | 899.200 | 324,74 | 22,39% | 5,04% |
| Fev/2022 | 2.574 | 11.118 | 821.753 | 319,25 | 23,15% | 5,19% |
| Mar/2022 | 2.934 | 11.758 | 942.215 | 321,14 | 24,95% | 5,06% |
| Abr/2022 | 2.686 | 11.759 | 973.712 | 362,51 | 22,84% | 5,53% |
| **Total/Média** | **30.950** | **120.761** | **R$ 8.061.748** | **256,59** | **26,00%** | **4,55%** |

---

## 3. Tendências temporais

### 3.1 Crescimento YoY — Abril/2021 vs Abril/2022

| Métrica | Abr/2021 | Abr/2022 | Variação |
|---------|----------:|----------:|---------:|
| Vendas | 2.190 | 2.686 | **+22,6%** |
| Leads | 7.392 | 11.759 | **+59,1%** |
| Usuários | 1.038.285 | 1.501.622 | **+44,6%** |
| Investimento | R$ 250.407 | R$ 973.712 | **+288,9%** |
| CAC | R$ 114,34 | R$ 362,51 | **+217,0%** |
| Market Share | 4,14% | 5,53% | **+1,39 p.p.** |

> **Sinal de alerta:** o investimento cresceu ~4× mais rápido que as vendas no mesmo período.

### 3.2 Tendências lineares mensais (slope da regressão)

| Métrica | Tendência/mês | Direção |
|---------|:-------------:|:-------:|
| Vendas | +37 unidades | ↑ positivo |
| Investimento | +R$ 55.715 | ↑ crescente |
| CAC | +R$ 18,84 | ↑ negativo (piora) |
| Conv. Lead→Venda | −0,56 p.p. | ↓ negativo |
| Market Share | +0,13 p.p. | ↑ positivo |

### 3.3 Análise por período

| Período | Vendas/mês (média) | CAC médio | Conv L→V | Investimento/mês |
|---------|------------------:|-----------:|---------:|-----------------:|
| Abr–Set/2021 (6 m) | 2.332 | R$ 194,88 | 28,22% | R$ 458.702 |
| Out–Dez/2021 (3 m) | 1.998 | R$ 279,60 | 25,11% | R$ 557.552 |
| Jan–Abr/2022 (4 m) | 2.741 | R$ 331,91 | 23,33% | R$ 909.220 |

**Leitura:** o período final apresenta o maior volume de vendas e maior market share, porém ao custo de um CAC 70% superior ao período inicial e conversão 5 p.p. menor.

### 3.4 Correlações entre variáveis

| | Investimento | Usuários | Leads | Vendas | CAC |
|--|:---:|:---:|:---:|:---:|:---:|
| Investimento | 1,000 | 0,906 | 0,866 | 0,716 | **0,934** |
| Usuários | 0,906 | 1,000 | 0,735 | 0,585 | 0,876 |
| Leads | 0,866 | 0,735 | 1,000 | 0,864 | 0,679 |
| Vendas | 0,716 | 0,585 | 0,864 | 1,000 | 0,421 |
| CAC | **0,934** | 0,876 | 0,679 | 0,421 | 1,000 |

> A correlação investimento–CAC de **0,934** é o sinal mais relevante: mais gasto não converte proporcionalmente em mais vendas, indicando rendimentos decrescentes ou saturação de canal.

---

## 4. Anomalias e inconsistências

### 4.1 Dezembro/2021 — outlier de sazonalidade

Dezembro registra **o menor mercado total (32.338)** e **o menor número de vendas (1.906)** do período — queda de ~23% em relação à média. Apesar disso, o **market share sobe para 5,89%** (maior do H2/2021), pois o mercado contrai mais do que as vendas. O investimento, no entanto, continua alto (R$ 573k), elevando o CAC para R$ 300,81 sem recuperação de volume.

> **Inconsistência prática:** manter investimento de marketing elevado em dezembro tem baixo retorno de vendas, mas pode ter justificativa de branding/conquista de share em janela de baixa concorrência.

### 4.2 Salto abrupto de Leads em Janeiro/2022

Os leads saltam de 7.645 (dez/2021) para **12.368 (jan/2022)** — crescimento de **+61,7% em um único mês** — enquanto as vendas crescem apenas +45,3%. A taxa de conversão lead→venda despenca para **22,39%**, o menor valor do período. Isso sugere:
- Mudança na definição ou captura de leads (qualidade do lead piorou); ou  
- Campanha de alto volume com baixa qualificação no início de 2022; ou  
- Atraso natural entre geração de lead e fechamento (pipeline lag).

### 4.3 Taxa de novos usuários estruturalmente alta (~83%)

Em todos os 13 meses, entre **81,7% e 85,9% dos usuários são novos**. Isso indica retenção orgânica muito baixa no site — a base de visitantes recorrentes é minúscula (~17%). Para um produto de recorrência mensal (contabilidade), é esperado que clientes ativos não voltem ao site de aquisição, mas o número também pode sinalizar que a comunicação pós-venda não direciona o cliente de volta ao ambiente web.

### 4.4 Crescimento assimétrico investimento × vendas

No período completo, o investimento cresce **+288,9%** enquanto as vendas crescem **+22,6%**. A elasticidade implícita é inferior a 0,1 — cada 1% de aumento no investimento gera menos de 0,1% de aumento em vendas. Esse padrão de rendimento decrescente normalmente indica:
- Saturação do canal principal de mídia paga;  
- Aumento de CPCs/CPMs por competição;  
- Ampliação do targeting para públicos menos qualificados.

### 4.5 Market Share de dezembro (5,89%) vs contexto

O market share máximo ocorre em dezembro, quando o mercado está no mínimo histórico (32.338). Isso pode criar uma percepção distorcida de crescimento de share — o numerador cai mas o denominador cai mais. A métrica de market share neste dataset é instável por depender fortemente de sazonalidade do mercado.

---

## 5. Perguntas de negócio que os dados levantam, mas não respondem

1. **Qual é o LTV do cliente adquirido?**  
   O CAC médio de R$ 256,59 e a curva de crescimento (+217% YoY) são sustentáveis somente se o LTV suportar esse patamar. Sem receita recorrente, churn e tempo de vida do cliente, é impossível avaliar a saúde econômica do negócio.

2. **A deterioração da conversão lead→venda (29,6% → 22,8%) é problema de qualidade de lead ou de processo comercial?**  
   O volume de leads quase dobrou de 2021 para 2022, mas a taxa de fechamento caiu. Precisamos de dados de qualificação dos leads (MQL vs SQL, fonte, etapa de abandono no funil de vendas) para distinguir as causas.

3. **Qual canal de marketing responde pelo aumento de investimento e qual o ROAS por canal?**  
   O dataset consolida todo o investimento em uma única linha. Sem breakdown por canal (Google, Meta, SEO, parceiros etc.), não é possível identificar quais canais têm rendimento decrescente e quais ainda têm espaço de escala.

4. **Qual é a taxa de churn pós-venda e como ela evoluiu?**  
   A planilha cobre exclusivamente aquisição. Uma empresa de contabilidade opera em modelo de assinatura — o valor gerado ou destruído pós-conversão (churn, expansão, NPS) é tão ou mais relevante do que o funil de novos negócios.

5. **O crescimento de usuários (+44,6% YoY) é pago ou orgânico?**  
   A taxa de novos usuários ~83% constante ao longo dos 13 meses indica que a base cresce via aquisição nova, não reativação. Entender quanto desse tráfego vem de mídia paga vs. orgânico/SEO/indicação determina se o crescimento de usuários é sustentável ou diretamente dependente do orçamento.

6. **Por que o mercado total de abertura de empresas (TAM mensal) cai acentuadamente em dezembro e oscila entre 32k–60k?**  
   A variável "Mercado de Abertura de Empresa" flutua sem tendência clara (+/−15% entre meses). Entender a fonte desse dado (JUCESB, Receita Federal, IBGE?) e sua granularidade geográfica é essencial para avaliar se o market share calculado é comparável entre meses.

7. **Existe correlação entre o perfil do lead gerado e a conversão?**  
   Junho/2021 e Janeiro/2022 tiveram os maiores volumes de leads, mas conversões abaixo da média (24,9% e 22,4%). Há dados de origem do lead, porte da empresa, regime tributário pretendido ou estado que permitam segmentar a qualidade?

8. **O ticket médio (MRR por cliente) se manteve estável ou variou ao longo do período?**  
   Sem essa informação, não é possível calcular CAC/LTV ratio nem saber se o crescimento de market share está sendo conquistado via price competition (descontos para fechar vendas) ou via melhora de proposta de valor.

---

## Resumo executivo

| Dimensão | Sinal | Interpretação |
|----------|:-----:|---------------|
| Volume de vendas | ↑ +22,6% YoY | Crescimento real, mas modesto dado o investimento |
| Market Share | ↑ 4,14% → 5,53% | Ganho consistente de participação |
| CAC | ↓ R$ 114 → R$ 362 | **Principal risco:** +217% em 12 meses |
| Conv. Lead→Venda | ↓ 29,6% → 22,8% | Degradação progressiva da eficiência |
| Funil topo (usuários) | ↑ +44,6% YoY | Escala de audiência funcionando |
| Investimento | ↑ +288,9% YoY | Crescimento muito superior ao retorno em vendas |
| Dados ausentes | — | LTV, churn, MRR, ticket médio, breakdown de canal |

> O dataset descreve uma operação de aquisição em escala crescente com **rendimentos marginais decrescentes claros**. A viabilidade estratégica depende de dados de retenção e monetização que não estão nesta planilha.
