# Dados da Planilha: Case-Growth-NovosNegocios.xlsx

Arquivo: `Referencias/Case-Growth-NovosNegocios.xlsx`  
Abas: `Ajudas`, `Dados`

---

## Aba: Ajudas

**Dimensões:** 7 linhas × 2 colunas

### Colunas e tipos

| Coluna      | Tipo   |
|-------------|--------|
| Dado        | object |
| Descrição   | object |

### Dados completos (glossário)

| Dado                            | Descrição |
|---------------------------------|-----------|
| Mercado de Abertura de Empresa  | Pessoas que Abriram uma Empresa durante o intervalo de datas. |
| Usuário                         | Pessoas que acessaram o site pelo menos uma vez durante o intervalo de datas. |
| Novos Usuário                   | Pessoas que acessaram o site pela primeira vez durante o intervalo de datas. |
| Lead                            | Pessoas que no site falaram que gostariam de abrir empresa com Contabilizei. |
| Vendas                          | Pessoas que abriram empresa com a Contabilizei. |
| Investimento                    | Valor total investido em MKT. |
| Market Share                    | Participação de Mercado — % de empresas abertas pela Contabilizei vs o tamanho do Mercado. |

> Nenhuma coluna numérica nesta aba.

---

## Aba: Dados

**Dimensões:** 13 linhas × 7 colunas  
**Período coberto:** abril/2021 – abril/2022

### Colunas e tipos

| Coluna                         | Tipo            |
|--------------------------------|-----------------|
| Mês                            | datetime64[ns]  |
| Mercado de Abertura de Empresa | int64           |
| Usuários                       | int64           |
| Novos usuários                 | int64           |
| Leads                          | int64           |
| Vendas                         | int64           |
| Investimento                   | float64         |

### Amostra — primeiras 10 linhas

| Mês        | Mercado Abertura | Usuários  | Novos Usuários | Leads  | Vendas | Investimento       |
|------------|-----------------|-----------|----------------|--------|--------|--------------------|
| 2021-04-01 | 52.888          | 1.038.285 | 860.141        | 7.392  | 2.190  | R$ 250.407,39      |
| 2021-05-01 | 60.500          | 1.043.004 | 865.406        | 8.075  | 2.326  | R$ 336.276,04      |
| 2021-06-01 | 56.658          | 995.580   | 813.582        | 9.273  | 2.310  | R$ 381.262,39      |
| 2021-07-01 | 56.490          | 1.084.718 | 892.546        | 7.489  | 2.374  | R$ 439.727,67      |
| 2021-08-01 | 60.082          | 1.419.330 | 1.195.234      | 8.921  | 2.488  | R$ 724.186,37      |
| 2021-09-01 | 52.080          | 1.470.623 | 1.231.490      | 8.730  | 2.306  | R$ 620.353,18      |
| 2021-10-01 | 56.637          | 1.380.065 | 1.147.967      | 8.378  | 2.057  | R$ 547.077,52      |
| 2021-11-01 | 51.366          | 1.384.710 | 1.132.634      | 7.855  | 2.030  | R$ 552.239,63      |
| 2021-12-01 | 32.338          | 1.156.736 | 949.588        | 7.645  | 1.906  | R$ 573.339,02      |
| 2022-01-01 | 54.940          | 1.571.792 | 1.333.751      | 12.368 | 2.769  | R$ 899.200,07      |

### Linhas restantes (11–13)

| Mês        | Mercado Abertura | Usuários  | Novos Usuários | Leads  | Vendas | Investimento       |
|------------|-----------------|-----------|----------------|--------|--------|--------------------|
| 2022-02-01 | 49.571          | 1.500.872 | 1.244.169      | 11.118 | 2.574  | R$ 821.752,87      |
| 2022-03-01 | 58.036          | 1.603.261 | 1.376.502      | 11.758 | 2.934  | R$ 942.214,75      |
| 2022-04-01 | 48.602          | 1.501.622 | 1.242.901      | 11.759 | 2.686  | R$ 973.711,54      |

### Estatísticas das colunas numéricas

| Estatística | Mercado Abertura | Usuários    | Novos Usuários | Leads      | Vendas    | Investimento       |
|-------------|-----------------|-------------|----------------|------------|-----------|---------------------|
| count       | 13              | 13          | 13             | 13         | 13        | 13                  |
| min         | 32.338          | 995.580     | 813.582        | 7.392      | 1.906     | R$ 250.407,39       |
| max         | 60.500          | 1.603.261   | 1.376.502      | 12.368     | 2.934     | R$ 973.711,54       |
| média       | 53.091          | 1.319.277   | 1.098.916      | 9.289      | 2.381     | R$ 620.134,49       |
| desvio-pad  | 7.279           | 222.304     | 196.272        | 1.811      | 303       | R$ 237.543,67       |
| p25         | 51.366          | 1.084.718   | 892.546        | 7.855      | 2.190     | R$ 439.727,67       |
| mediana     | 54.940          | 1.384.710   | 1.147.967      | 8.730      | 2.326     | R$ 573.339,02       |
| p75         | 56.658          | 1.500.872   | 1.242.901      | 11.118     | 2.574     | R$ 821.752,87       |

### Observações

- A coluna `Mês` representa sempre o primeiro dia do mês (granularidade mensal).
- `Investimento` é o único campo float; os demais são inteiros.
- O mês de **dezembro/2021** apresenta o menor mercado de abertura (32.338) e o menor volume de vendas (1.906), sugerindo sazonalidade de fim de ano.
- **Market Share** aparece no glossário (aba Ajudas) mas não está presente como coluna na aba Dados — provavelmente é uma métrica derivada a ser calculada (Vendas / Mercado de Abertura de Empresa).
