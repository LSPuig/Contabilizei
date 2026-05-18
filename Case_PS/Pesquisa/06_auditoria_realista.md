# Auditoria do Cenário Realista — Simulador 2

**Arquivo auditado:** `Entrega/index.html`, função `getShareSimulatorState()` (linhas 2806–2848)  
**Dados:** `Referencias/Case-Growth-NovosNegocios.xlsx`, aba "Dados" (N=13 obs, abr/21–abr/22)  
**Data:** 2026-05-18

---

## I. Reconstrução Numérica dos Valores do Simulador

### Defaults carregados no HTML

| Parâmetro | ID do controle | Valor default |
|-----------|---------------|---------------|
| Meta share | `share-meta-range` | **6 %** |
| Mercado mensal | `share-mercado-range` | **53.091** aberturas |
| Vendas atuais | `share-vendas-atuais-range` | **2.686** vendas (abr/22) |
| CAC base (realista) | `share-realista-cac-range` | **R$ 362** |
| Elasticidade | `share-elasticidade-range` | **0,10** |

### Passo a passo da fórmula implementada

```
// JavaScript — Entrega/index.html, linha 2816 ss.

vendasAlvo         = Math.ceil(53091 × 0,06)          = Math.ceil(3185,46) = 3.186
vendasIncrementais = max(0, 3186 − 2686)               = 500
ratioEscala        = max(1, 3186 / 2686)               = 1,18615041
expoenteElasticidade = (1 − 0,10) / 0,10              = 9
cacMarginal        = 362 × (1,18615041)^9             = 362 × 4,64904   = 1.682,55
realistaInvestMensal = 500 × 1682,55                  = 841.272
realistaInvestAnual  = 841.272 × 12                   = 10.095.264
```

### Verificação exata (Python/numpy)

```
ratioEscala         = 1.18615041  (3186/2686)
expoente            = 9.0         ((1−0,1)/0,1)
cacMarginal         = 362 × 1.18615041^9 = 1.682,544  → exibido R$ 1.683 ✓
invMensal           = 500 × 1.682,544    = R$ 841.272  ✓
invAnual            = 841.272 × 12       = R$ 10.095.264 ✓
```

### Fórmula implícita usada

```
CAC_marginal  = CAC_base × (V_alvo / V_atual)^((1 − ε) / ε)
inv_incremental_mensal = Δvendas × CAC_marginal
```

onde `Δvendas = V_alvo − V_atual = 500`, `CAC_base = R$ 362`, `ε = 0,10`.

---

## II. Teste das 5 Hipóteses de Erro

### (a) "Incremental" rotulado seria, na verdade, total

**Verificação:** `realistaInvestMensal = vendasIncrementais × cacMarginal`

O multiplicador é `vendasIncrementais = 500`, não `vendasAlvo = 3.186`.  
**Conclusão: falso.** O simulador usa corretamente o delta de vendas. O rótulo "incremental" está certo — o erro está na fórmula de CAC_marginal, não na escala da métrica.

---

### (b) Elasticidade YoY naive confundida com sazonalidade

A elasticidade-padrão de `ε = 0,10` foi justificada no simulador como "evidência de elasticidade baixa". A fonte implícita é o cálculo YoY:

```
Abr/21: Invest = R$ 250.407  |  Vendas = 2.190
Abr/22: Invest = R$ 973.712  |  Vendas = 2.686

ΔInvest = +288,9%   ΔVendas = +22,6%
ε_YoY naive = 22,6% / 288,9% = 0,0784
```

**Problema duplo:**
1. **Sazonalidade**: comparar abril com abril anula sazonalidade de mercado, mas não a variação estrutural do mercado (abr/21 = 52.888 aberturas × 6% share vs abr/22 = 48.602 × 6% share — o mercado *caiu* 8% YoY). Parte da demanda respondia ao mercado, não ao investimento.
2. **Simultaneidade**: o aumento de investimento coincidiu com mudança de mix de canais e estratégia (os dados mostram CAC passando de R$ 114 em abr/21 para R$ 362 em abr/22 — crescimento de 217% no CAC), sugerindo que a correlação reflete degradação de eficiência, não apenas retorno marginal decrescente "puro".

**Conclusão: parcialmente verdadeiro.** A elasticidade de 0,10 é estimada de forma ingênua a partir de dois pontos extremos do painel, ignorando confundidores (mercado, tendência temporal). A regressão M2 com controle de mercado dá ε ≈ 0,197, mais que o dobro do valor usado.

---

### (c) Erro de fórmula econômica sob Cobb-Douglas

**Esta é a hipótese de erro mais grave.**

O simulador usa:
```
inv_inc = Δvendas × CAC_marginal
       = 500 × [R$ 362 × (3186/2686)^9]
       = R$ 841.272 / mês
```

Sob uma função Cobb-Douglas `V = A × I^ε`, o investimento necessário para atingir `V_alvo` partindo de `(I_atual, V_atual)` é:

```
V_alvo / V_atual = (I_alvo / I_atual)^ε
⟹ I_alvo = I_atual × (V_alvo / V_atual)^(1/ε)
⟹ I_incremental = I_alvo − I_atual
```

**Aplicando com ε = 0,10:**
```
I_alvo = 973.712 × (3186/2686)^(1/0,10)
       = 973.712 × (1,18615)^10
       = 973.712 × 5,51315
       = R$ 5.368.191 / mês

I_incremental = 5.368.191 − 973.712 = R$ 4.394.479 / mês
             = R$ 52.733.752 / ano
```

A fórmula do simulador produz R$ 10,1M/ano; a Cobb-Douglas correta com o mesmo ε produz **R$ 52,7M/ano — 5,2× maior**.

**Por que diferem?**

A fórmula `inv_inc = Δvendas × CAC_marginal` tem a estrutura de um produto marginalista, mas combina dois erros:

1. Multiplica o *custo médio elevado* (cacMarginal) por uma *quantidade incremental* (Δvendas), mas esquece que cada unidade incremental de venda custa progressivamente mais — não apenas a última. O custo total adicional é a integral de `dI/dV` de `V_atual` a `V_alvo`, não `Δvendas × CAC_marginal(V_alvo)`.

2. A potenciação `CAC_base × ratio^((1−ε)/ε)` deriva de `∂I/∂V` avaliado em `V_alvo` sob C-D, mas não é o CAC marginal — é o **custo marginal por venda** em `V_alvo`. Multiplicar esse custo marginal pelo delta total subestima o custo real porque ignora as unidades intermediárias que também têm custo superior ao CAC_base.

**Conclusão: verdadeiro.** O correto é `I_incremental = I_alvo − I_atual` com `I_alvo = I_atual × (V_alvo/V_atual)^(1/ε)`.

---

### (d) Defaults inconsistentes

Comparação dos defaults entre os dois simuladores da página:

| Parâmetro | Simulador 2 (Share) | Simulador 3 (Elasticidade) |
|-----------|--------------------|-----------------------------|
| Investimento base | 2.686 × R$362 = R$ 972.332 aprox. | R$ 974.000 |
| CAC base | R$ 362 | R$ 362,51 |
| Elasticidade | 0,10 | 0,10 |
| V_atual | 2.686 | implícito via base |

O investimento de referência do Simulador 3 (`elasticidadeBaseInvestimento = 974000`, linha 2954) é aproximadamente consistente com o dado real de abr/22 (R$ 973.712). O CAC de R$ 362,51 no Sim-3 vs R$ 362 no Sim-2 é arredondamento.

**Conclusão: inconsistência menor** — a diferença de R$ 362 vs R$ 362,51 é cosmética (0,14%) mas tecnicamente os simuladores deveriam usar o mesmo valor exato.

---

### (e) Elasticidade constante por toda a faixa

A fórmula assume ε constante de V_atual=2.686 a V_alvo=3.186 (incremento de +18,6%). Isso é razoável para variações pequenas. Porém:

- O modelo C-D puro (`V = A × I^ε`) impõe rendimentos constantes a escala em `I` por construção — uma hipótese forte.
- Os dados mostram CAC crescente monotonicamente (R$ 114 → R$ 363), consistente com ε < 1, mas a taxa de aumento desacelerou entre ago/21 e abr/22 (plateau de CAC ~R$265–R$362), sugerindo que ε pode não ser estritamente constante.
- Para o intervalo de 18,6% de crescimento de vendas, a hipótese de ε constante gera erro de aproximação pequeno (< 5%) e é defensável.

**Conclusão: hipótese simplificadora aceitável** para o intervalo considerado, mas o IC de ε é muito largo (ver seção III).

---

## III. Re-estimação de ε por Regressão Log-Log

### Dados utilizados

13 observações mensais: abr/2021–abr/2022  
Variável dependente: `log(Vendas)`  
Regressores: `log(Investimento)`, `log(Mercado)`, `trend` (0..12)

### Tabela de resultados

| Modelo | Especificação | β̂ (ε) | Erro Padrão | IC 95% | R² | F-stat | p(F) | N |
|--------|--------------|--------|-------------|--------|-----|--------|------|---|
| **M1** | `log(V) ~ log(I)` | **0,1779** | 0,0735 | [0,0162; 0,3396] | 0,348 | 5,87 | 0,034 | 13 |
| **M2** | `log(V) ~ log(I) + log(M)` | **0,1970** | 0,0580 | [0,0677; 0,3263] | 0,635 | 8,71 | 0,006 | 13 |
| **M3** | M2 + trend | **0,1233** | 0,1680 | [−0,257; 0,503] | 0,644 | 5,43 | 0,021 | 13 |
| **M4** | M3 sem dez/21 | **0,2299** | 0,1925 | [−0,214; 0,674] | 0,514 | 2,82 | 0,107 | 12 |

**Notas:**
- M1 é o modelo mais simples e significativo em nível 5% (p=0,034).
- M2 adiciona controle de mercado (β_logM = 0,426, IC=[0,088; 0,764], significativo), eleva R² de 0,35 para 0,64 e é o **modelo preferido** — controla o confundidor mais importante.
- M3 adiciona trend linear: coeficiente de trend não significativo (β_trend=0,009, SE=0,019), e o IC de β_logI alarga para incluir zero — multicolinearidade entre trend e logI (ambos sobem monotonicamente na 2ª metade da amostra).
- M4 exclui dezembro/2021 (sazonalidade extrema, menor mercado da série): IC de logI ainda inclui zero com N=12. Modelo não converge com clareza estatística.

### Diagnóstico

Com apenas 13 observações e variáveis altamente correlacionadas (logI e trend têm r=0,93 no período), a identificação de ε é frágil. M2 é o mais robusto: controla o maior confundidor (demanda de mercado) sem multicolinearidade severa.

**ε re-estimado recomendado: 0,197 (M2), IC 95% = [0,068; 0,326]**

O valor de 0,10 usado no simulador está abaixo do IC inferior de M2 (0,068) e de M1 (0,016), sendo tecnicamente defensável como valor pessimista mas **não é o centro da distribuição empírica**.

---

## IV. Derivação Matemática Completa — Fórmula Cobb-Douglas Correta

### 4.1 Modelo estrutural

Assuma função de produção de vendas Cobb-Douglas:

```
V(I) = A · I^ε                              (1)
```

onde `A > 0` é uma constante de eficiência, `ε ∈ (0,1)` é a elasticidade investimento-vendas e `I` é o investimento em marketing.

### 4.2 Calibração de A a partir do estado atual

Observamos `(I_atual, V_atual)` em abr/22:

```
V_atual = A · I_atual^ε
⟹ A = V_atual / I_atual^ε                   (2)
```

### 4.3 Investimento alvo

Para atingir `V_alvo`:

```
V_alvo = A · I_alvo^ε
       = (V_atual / I_atual^ε) · I_alvo^ε   (substituindo (2))
⟹ V_alvo / V_atual = (I_alvo / I_atual)^ε
⟹ I_alvo / I_atual = (V_alvo / V_atual)^(1/ε)
⟹ I_alvo = I_atual · (V_alvo / V_atual)^(1/ε)  (3)
```

### 4.4 Investimento incremental

```
I_incremental = I_alvo − I_atual
              = I_atual · [(V_alvo / V_atual)^(1/ε) − 1]   (4)
```

### 4.5 Aplicação numérica com ε = 0,10

```
V_alvo / V_atual = 3186 / 2686 = 1,18615
1/ε = 10
(1,18615)^10 = 5,5131

I_alvo = 973.712 × 5,5131 = R$ 5.368.191 / mês
I_incremental = 5.368.191 − 973.712 = R$ 4.394.479 / mês
               = R$ 52.733.752 / ano
```

### 4.6 Relação com o custo marginal (onde o simulador errou)

O custo marginal de produzir uma venda adicional sob C-D é:

```
dI/dV = (1/ε) · (I/V) = (1/ε) · CAC_médio      (5)
```

O simulador calcula algo semanticamente próximo, mas algebricamente distinto:

```
CAC_marginal_sim = CAC_base × (V_alvo/V_atual)^((1−ε)/ε)
```

Isso equivale a avaliar `dI/dV` em `V_alvo` (não em `V_atual`):

```
dI/dV|_{V=V_alvo} = (1/ε) · (I_alvo / V_alvo)
                  = (1/ε) · [I_atual · (V_alvo/V_atual)^(1/ε)] / V_alvo
```

Simplificando com `CAC_atual = I_atual/V_atual`:

```
dI/dV|_{V=V_alvo} = (1/ε) · CAC_atual · (V_alvo/V_atual)^(1/ε − 1)
                  = (1/ε) · CAC_atual · (V_alvo/V_atual)^((1−ε)/ε)
```

Para ε=0,10: `(1/ε)·CAC_atual = 10 × 362 = 3.620`, mas o simulador usa `362 × ratio^9` (sem o fator 1/ε). Isso introduz erro adicional de fator 1/ε = 10, que neste caso subestima o custo marginal em 10×.

Mesmo que o custo marginal estivesse correto, **multiplicar o custo marginal no ponto final pelo delta total de vendas subestima o custo real**, pois o custo cresce ao longo do caminho. O custo real é a integral:

```
ΔI = ∫_{V_atual}^{V_alvo} (dI/dV) dV = I_alvo − I_atual   (idêntico a (4))
```

---

## V. Tabela Comparativa de Investimento Incremental Anual

| Cenário | Fórmula | ε | Inv. Incremental Mensal | Inv. Incremental Anual |
|---------|---------|---|------------------------|------------------------|
| **(a) Linear** | `Δvendas × CAC_atual` | — | R$ 181.255 | **R$ 2.175.060** |
| **(b) Simulador atual (fórmula errada)** | `Δvendas × CAC_base × ratio^((1−ε)/ε)` | 0,10 | R$ 841.272 | **R$ 10.095.264** |
| **(c) Cobb-Douglas correto, ε=0,10** | `I_atual × [(V_alvo/V_atual)^(1/ε) − 1]` | 0,10 | R$ 4.394.479 | **R$ 52.733.752** |
| **(d) Cobb-Douglas correto, ε=M1 (0,178)** | idem | 0,178 | R$ 1.567.863 | **R$ 18.814.353** |
| **(e) Cobb-Douglas correto, ε=M2 (0,197)** | idem | 0,197 | R$ 1.342.491 | **R$ 16.109.897** |

**Premissas comuns:** V_atual=2.686, V_alvo=3.186, I_atual=R$973.712 (abr/22), CAC_atual=R$362,51.

**Relação entre cenários:**
- (b) supera (a) em 4,6× — reflete o custo-marginal crescente, mas a fórmula não está correta.
- (c) supera (b) em 5,2× — a fórmula correta para o mesmo ε exige investimento muito maior.
- (d) e (e) com ε re-estimado ficam entre (b) e (c) — mais plausíveis empiricamente.
- (a) é um piso teórico (assume CAC constante, sem retornos decrescentes).

---

## VI. Recomendação Técnica

### Qual fórmula adotar

**Adotar a fórmula Cobb-Douglas correta:**

```
I_alvo = I_atual × (V_alvo / V_atual)^(1/ε)
I_incremental = I_alvo − I_atual
```

A fórmula atual do simulador (`Δvendas × CAC_marginal`) não tem suporte em microeconomia padrão e subestima o investimento real em ~5× para ε=0,10. Mesmo que fosse correta conceitualmente, mistura custo marginal pontual com volume total incremental — violando o teorema fundamental do cálculo.

### Qual ε adotar

**Recomendação principal: ε = 0,197 (M2)**

Justificativas:
1. M2 é o único modelo com todos os regressores significativos, R² adequado (0,635) e sem multicolinearidade grave.
2. O controle de mercado (`log(Mercado)`) é essencial: dezembro/2021 tem mercado 46% abaixo da média, e sem controle a elasticidade de investimento absorve variação de demanda.
3. O IC 95% de M2 é [0,068; 0,326] — exclui ε=0 com mais folga que M1.

**ε = 0,10 como cenário pessimista (piso):** pode ser mantido como sensibilidade conservadora, com a ressalva explícita de que (a) está abaixo do IC inferior de M2 e (b) a fórmula correta com ε=0,10 implica R$ 52,7M/ano — provavelmente inviável e que levaria a questionar a premissa de escala.

**ε = 0,178 (M1) como cenário intermediário:** mais simples de comunicar, dentro do IC de M2, indica R$ 18,8M/ano.

### Síntese para o tomador de decisão

| Decisão | Recomendação |
|---------|-------------|
| Fórmula do simulador | Substituir por `I_inc = I_atual × [(V_alvo/V_atual)^(1/ε) − 1]` |
| Elasticidade central | **ε = 0,197** (M2, controlado por mercado) → R$ 16,1M/ano |
| Elasticidade pessimista | ε = 0,10 → R$ 52,7M/ano (mas questiona viabilidade da meta via mídia) |
| Estratégia alternativa | Dado o alto custo de aquisição via mídia, recuperar conversão lead→venda (atualmente ~23%) para ~28% seria equivalente a atingir 6% de share sem incremento de investimento |

O investimento incremental mínimo defensável (fórmula correta, ε=M2) é de **R$ 16,1M/ano** — 7,4× o cenário linear e 1,6× o cenário do simulador atual. A diferença principal não é entre modelos de ε, mas entre a fórmula errada e a fórmula correta.
