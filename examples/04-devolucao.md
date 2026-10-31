# Devolução de pedido

**O que demonstra:** Cenário não trivial: o agente pede os dados de identificação, consulta o pedido e cruza com a política de devolução.

Conversa real com o agente (`python main.py --debug`). As linhas `[tool]` mostram as ferramentas chamadas.

```text
Você: Me arrependi da minha compra, posso devolver meu pedido?
  [tool] get_policy({'topic': 'returns'})

Lia: Oi! Sim, a gente consegue ver isso pra você. 😊

Pela nossa política, compras online têm **direito de arrependimento de até 7 dias corridos após o recebimento**, sem precisar justificar. Algumas condições:

- O produto precisa estar na embalagem original, sem sinais de uso, com todos os acessórios e manuais.
- O reembolso é feito na mesma forma de pagamento original em até 10 dias úteis.
- O frete de devolução fica por conta da loja nesse caso.

Pra eu conferir o prazo e o status do seu pedido, me manda por favor:
1. O número do pedido
2. O e-mail usado na compra

Você: pedido 1, email pedro.oliveira@jmail.com
  [tool] get_order({'order_id': 1, 'email': 'pedro.oliveira@jmail.com'})

Lia: Oi, Pedro! Achei o seu pedido 1 (1x Martin D-28 Dreadnought Natural, pago via PIX). Infelizmente, o prazo de arrependimento de 7 dias já passou. Ele foi entregue há cerca de 371 dias, então eu não consigo liberar a devolução por arrependimento.

Algumas coisas que ainda podem ajudar:

- **Defeito de fabricação:** trocas por defeito são possíveis em até 30 dias após a compra. Depois disso, a garantia é acionada direto com o fabricante, e a loja pode intermediar o processo se você pedir.
- **Outras situações:** se for algo específico, como um problema com o produto, a equipe consegue analisar o caso com você.

Se quiser seguir por esse caminho, fala com a nossa equipe pelo WhatsApp/telefone **(67) 3341-4444** ou pelo e-mail **contato@emporiodamusica.com.br** (resposta em até 24 horas úteis).

Tem algum defeito no violão ou quer saber de outra coisa?
```
