# Endereço e horário da loja

**O que demonstra:** Consulta às políticas da loja (informações gerais e horário).

Conversa real com o agente (`python main.py --debug`). As linhas `[tool]` mostram as ferramentas chamadas.

```text
Você: Qual o endereço da loja?
  [tool] get_policy({'topic': 'about'})

Lia: Nossa loja fica na Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333.

Se precisar, o WhatsApp/telefone é (67) 3341-4444. Posso ajudar com mais alguma coisa?

Você: E que horas vocês abrem no sábado?
  [tool] get_policy({'topic': 'hours'})

Lia: No sábado a loja atende das 9h às 13h. Hoje é sábado, 31/10, às 11h35, então ainda estamos abertos até as 13h.
```
