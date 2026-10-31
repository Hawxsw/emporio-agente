# Violões até R$ 1.000

**O que demonstra:** Consulta ao catálogo com filtro de preço, estoque e categoria.

Conversa real com o agente (`python main.py --debug`). As linhas `[tool]` mostram as ferramentas chamadas.

```text
Você: Quais opções de violões disponíveis custando até R$1000?
  [tool] search_products({'term': '', 'category': 'Violões', 'max_price': 1000.0, 'min_price': 0, 'only_available': True})

Lia: Encontrei 12 violões disponíveis até R$ 1.000. Aqui vão os destaques, do mais barato ao mais caro:

**Nylon (clássicos, ótimos para começar)**
- **Tagima Memphis AC-39 Nylon Natural**: R$ 429,90 (15 em estoque)
- **Rozini RC-104 Nylon Estudante**: R$ 459,90 (10 em estoque)
- **Yamaha C40 Nylon Natural**: R$ 599,90 (12 em estoque)
- **Giannini GN-15 Nylon Cedro Natural**: R$ 689,00 (6 em estoque)
- **Yamaha C70 Nylon Natural**: R$ 849,00 (8 em estoque). Tampo de spruce sólido.

**Aço (folk)**
- **Shelby SN-100 Folk Aço Preto**: R$ 549,00 (5 em estoque)
- **Giannini GF-1R Folk Sunburst**: R$ 579,90 (7 em estoque)
- **Yamaha F310 Aço Natural**: R$ 699,90 (14 em estoque). Um dos mais vendidos para iniciantes e intermediários.
- **Tagima Dallas Tuner Aço Natural**: R$ 749,00 (9 em estoque). Tem afinador integrado.
- **Tagima Woodstock Dreadnought Natural**: R$ 899,00 (11 em estoque). Corpo grande e som potente.

**Com captação elétrica**
- **Shelby SGD-195E Eletroacústico Sunburst**: R$ 799,00 (6 em estoque)

**7 cordas**
- **Tagima TW-7 7 Cordas Aço Natural**: R$ 999,00 (6 em estoque)

Se me disser se você é iniciante, se quer tocar com cordas de nylon ou aço, e se precisa de amplificação, eu indico o melhor para o seu caso.

Você: Qual desses você indica pra quem está começando?

Lia: Pra quem está começando, eu indico o **Yamaha C40 Nylon Natural** (R$ 599,90, 12 em estoque). É um violão clássico com tampo de spruce e fundo/laterais de meranti, com boa projeção sonora. As cordas de nylon são mais macias nos dedos, o que ajuda nas primeiras semanas. A Yamaha também tem boa fama de qualidade e de manter a afinação.

Se o orçamento estiver mais apertado:
- **Rozini RC-104 Nylon Estudante** (R$ 459,90): tampo de spruce e laterais de sapele, bom custo-benefício.
- **Tagima Memphis AC-39 Nylon Natural** (R$ 429,90): o mais barato da lista, leve e confortável.

Se você quer tocar músicas populares, com som mais brilhante, o **Yamaha F310 Aço Natural** (R$ 699,90) é a outra opção forte, mas as cordas de aço costumam doer mais no início.

Quer que eu veja mais detalhes de algum deles?
```
