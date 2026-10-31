# Preço do Takamine GD20

**O que demonstra:** Consulta de preço e disponibilidade de um produto específico.

Conversa real com o agente (`python main.py --debug`). As linhas `[tool]` mostram as ferramentas chamadas.

```text
Você: Quanto custa o Takamine GD20?
  [tool] search_products({'term': 'takamine gd20', 'category': '', 'max_price': 0, 'min_price': 0, 'only_available': False})

Lia: Oi! O Takamine GD20 Dreadnought Natural está disponível aqui na loja por **R$ 2.199,00**, com 5 unidades em estoque.

Ele tem tampo de cedro sólido, fundo e laterais em sapele, braço em mogno, cordas de aço e escala de 650mm. É um violão muito bom para fingerstyle, com timbre quente e definido.

Quer saber sobre formas de pagamento ou parcelamento?

Você: Dá pra parcelar?
  [tool] get_policy({'topic': 'payment'})

Lia: Sim! No cartão de crédito dá para parcelar em até **12x sem juros**, com parcela mínima de R$ 100,00.

Para o GD20 de R$ 2.199,00, por exemplo:
- **12x de R$ 183,25** no cartão
- Ou à vista no **PIX**, com 5% de desconto (cerca de **R$ 2.089,05**)

Também aceitamos débito e boleto à vista. Quer que eu te ajude com mais alguma coisa?
```
