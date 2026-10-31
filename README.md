# Empório da Música — Agente de Atendimento

Protótipo de agente de atendimento por texto para a **Empório da Música**, loja fictícia de instrumentos musicais de Campo Grande/MS. A assistente, **Lia**, responde preços, disponibilidade, status de pedido, horários, trocas e pagamentos consultando os dados da loja e o manual de políticas, nunca de memória.

**Resumo:** function calling com 3 ferramentas determinísticas · Claude Haiku 5.5 (Anthropic) · CLI em Python · histórico persistido por sessão · [exemplos de conversa](#exemplos-de-conversa).

Priorizei a confiabilidade das respostas acima da quantidade de funcionalidades: o agente nunca informa preço, estoque, prazo ou regra sem consultar uma ferramenta, e as ferramentas usam filtros determinísticos em vez de deixar o LLM gerar consultas livres.

---

## Como rodar

Pré-requisitos: Python 3.11+ (testado com 3.14) e uma chave da [API da Anthropic](https://console.anthropic.com/).

```bash
git clone https://github.com/Hawxsw/emporio-agente.git
cd emporio-agente
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows  |  source .venv/bin/activate  (Linux/macOS)
pip install -r requirements.txt
cp .env.example .env              # preencha ANTHROPIC_API_KEY
python main.py
```

| Variável / opção | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API (obrigatória) |
| `ANTHROPIC_MODEL` | Modelo usado (padrão `claude-haiku-5-5`) |
| `--session <id>` | ID da conversa, ex.: telefone do cliente. Cada sessão tem seu histórico (padrão `default`) |
| `--debug` | Mostra as ferramentas chamadas e seus argumentos |

No chat: `/novo` reinicia a conversa e `/sair` encerra. O histórico é salvo a cada resposta, então rodar de novo com o mesmo `--session` continua de onde parou.

---

## Arquitetura

```
main.py                CLI: loop de mensagens, comandos, salva o histórico
└── src/agent.py       Loop do agente: chama o modelo, executa ferramentas, repete até a resposta final
    ├── src/prompts.py     Prompt de sistema (persona, quando usar cada ferramenta, regras)
    ├── src/tools.py       Ferramentas que o modelo pode chamar
    │   ├── src/data_loader.py   Carrega e trata os CSVs (pandas)
    │   └── src/policies.py      Extrai o PDF de políticas e divide por seção
    ├── src/history.py     Histórico em JSON (um arquivo por sessão)
    └── src/config.py      Caminhos e variáveis de ambiente
```

| Ferramenta | Quando o agente usa | Fonte |
|---|---|---|
| `search_products` | Preço, estoque, disponibilidade, promoções, sugestões | `products`, `categories`, `promotions` |
| `get_order` | Status, rastreio e itens de um pedido; base para trocas/devoluções | `orders`, `customers`, `order_items` |
| `get_policy` | Endereço, contato, horários, pagamento, trocas, frete, garantia, privacidade | `políticas_da_loja.pdf` |

Perguntas que misturam dados e regras (ex.: *"posso devolver meu pedido?"*) levam o agente a chamar `get_order` **e** `get_policy` e cruzar as informações.

---

## Decisões técnicas

### Abordagem: function calling

O modelo decide qual ferramenta chamar e o Python executa a consulta de forma determinística.

- **Por que não RAG com embeddings?** Os dados operacionais são estruturados: "violões até R$ 1.000 disponíveis" exige filtro numérico e de estoque exato, que um filtro em pandas resolve sem erro. O manual é curto e dividido em 10 seções numeradas, então recuperar a seção inteira pelo tema é determinístico, barato e não corta regras ao meio.
- **Por que não um agente SQL?** Consultas livres sobre a base de clientes abririam espaço para vazamento de dados. Com ferramentas fechadas, cada consulta tem regras explícitas: `get_order` só retorna o pedido se **número e e-mail** baterem (LGPD) e expõe apenas o primeiro nome.
- **Por que não LangChain/LangGraph?** Com três ferramentas e um fluxo linear, um framework traria abstração e dependências sem ganho, e esconderia o que é enviado ao modelo. LangGraph faria sentido com vários agentes ou aprovação humana no meio do fluxo. Também não usei o *tool runner* do SDK (ainda em beta): o loop manual em [`src/agent.py`](src/agent.py) tem poucas linhas e dá controle sobre o histórico salvo e sobre como erros de ferramenta voltam ao modelo (`is_error`). Do SDK aproveitei o `beta_tool`, que gera o schema de cada ferramenta a partir da assinatura e da docstring.

### Modelo: Claude Haiku 5.5

- **Custo:** o modelo mais barato da Anthropic (US$ 0,10 / 1M tokens de entrada, US$ 0,50 / 1M de saída), adequado a atendimento de alto volume.
- **Suficiente para a tarefa:** o trabalho pesado (filtrar, calcular prazos, buscar a regra) fica nas ferramentas; o modelo só escolhe a ferramenta e redige a resposta.
- **Esforço `low` e cache de prompt** para reduzir custo e latência, já que prompt de sistema e ferramentas não mudam durante a conversa.

Nos testes, o Haiku escolheu as ferramentas certas e seguiu as regras do prompt: no pedido de devolução, consultou a política, pediu número e e-mail, cruzou com o pedido e ofereceu a garantia como alternativa quando o prazo de arrependimento já tinha passado; perguntas fora do escopo foram recusadas com educação. Não encontrei caso que exigisse um modelo maior. Se uma avaliação sistemática mostrasse erros, o próximo passo seria testar o Claude Sonnet 5.5, trocando só a variável `ANTHROPIC_MODEL`.

**Por que não Gemini:** comecei no plano gratuito do Gemini, mas ele se mostrou inviável para testar um agente: modelo descontinuado para novos usuários, erros de sobrecarga (503) e limite de 20 requisições por dia. Como cada pergunta com ferramenta consome ao menos 2 chamadas, isso dava cerca de 10 perguntas por dia. A troca de provedor mexeu só em `agent.py`, `history.py` e `config.py`.

### Persistência do histórico

Cada sessão é salva em `history/<sessão>.json` com a conversa **completa**, incluindo chamadas de ferramenta e resultados, para o modelo saber o que já consultou. No atendimento real (WhatsApp) o cliente volta horas depois e continua o assunto.

### Tratamento dos dados

- Produtos unidos às categorias e às **promoções ativas** (`is_active = 1`), com cálculo do preço final; se houver mais de uma promoção ativa, vale a de maior desconto.
- Flag `available` (status `active` **e** estoque > 0): o agente só oferece o que pode ser comprado agora.
- Busca normalizada (minúsculas, sem acentos), e status e formas de pagamento traduzidos para português legível antes de chegar ao modelo.
- PDF extraído com `pypdf`, sem cabeçalhos e rodapés repetidos, dividido nas 10 seções do manual.

### Prompt

O prompt de sistema ([`src/prompts.py`](src/prompts.py)) tem quatro blocos: persona e tom (tirados da seção 7.1 do manual), quando usar cada ferramenta, regras inegociáveis (ex.: "se não veio de uma ferramenta, você não sabe") e data/hora atual, para o agente saber se a loja está aberta. As instruções estão em inglês para manter o padrão do código, que também está em inglês, e as respostas são forçadas para português do Brasil. As docstrings das ferramentas também dizem **quando** cada uma deve ser usada.

---

## Suposições

- **Data de entrega:** os pedidos só têm `estimated_delivery`; para pedidos entregues, ela é usada como data de entrega nos prazos de troca, e o agente é avisado disso.
- **Prazos calculados a partir de hoje:** como os pedidos são de 2025–2026, todo pedido entregue já está fora dos 7 dias de arrependimento. Mantive assim porque é o comportamento correto para a data real, e o caso mostra o agente explicando a regra e oferecendo alternativas.
- **Identificação:** consultar um pedido exige número **e** e-mail; sem autenticação real, é a forma mais simples de não expor dados de terceiros.
- **Produtos não vendáveis:** produtos `discontinued` ou `coming_soon` não são oferecidos, mesmo com estoque (ex.: o baixo Ibanez descontinuado tem 13 unidades).
- **Promoções:** não acumulam entre si nem com o desconto de 5% no PIX.
- **Inconsistências nos dados de origem**, mantidas como estão e tratadas assim:
  - o manual traz dois números de WhatsApp: (67) 3341-4444 na seção 1.2 e (67) 3321-4500 na seção 7. Adotei o da 1.2 (dados oficiais da empresa), fixado no prompt;
  - o e-mail da seção 1.2 tem acento (`empóriodamusica`); usei a versão sem acento da capa;
  - as regras de parcelamento se contradizem (parcela mínima de R$ 100 na tabela, R$ 80 de 4x a 6x na seção 3.1); o agente repassa o texto do manual;
  - alguns totais de pedido não batem com a soma dos itens (ex.: pedido 20) e há um e-mail de cliente duplicado. Isso não afeta as respostas, porque o agente informa o total registrado.

---

## Limitações e próximos passos

**Limitações:**

- Sem avaliação sistemática da qualidade das respostas; a validação foi manual.
- Busca de produtos por palavra-chave: não tolera erros de digitação nem entende sinônimos.
- Histórico cresce sem limite, o que aumenta custo e latência em conversas longas.
- Encaminhamento para humano é só informativo (o agente passa o contato, mas não abre chamado).

**Com mais tempo:**

1. **Avaliação automatizada:** perguntas com respostas esperadas (preço certo, ferramenta certa, recusa fora do escopo) e um LLM como avaliador de tom.
2. **Testes unitários** das ferramentas e do tratamento de dados.
3. **Busca de produtos mais tolerante** (fuzzy matching ou embeddings para pedidos vagos como "algo bom para iniciante").
4. **Integração real:** API + webhook do WhatsApp, banco de dados no lugar dos CSVs e transferência para atendente com resumo do caso.

---

## Uso de assistentes de código

Usei o **Claude Code** (extensão do VS Code) como tutor e revisor, não como gerador automático: pedi que ele lesse o enunciado e os dados e me passasse o código em etapas, com a explicação de cada parte, e eu digitei o código. Ele também testava cada etapa antes de me entregar.

Na prática:

- **Análise inicial:** leitura do enunciado, do manual e dos CSVs, apontando inconsistências nos dados (listadas em [Suposições](#suposições)).
- **Revisão:** traduzi o código para inglês por conta própria; o assistente encontrou e corrigiu os pontos em que a tradução quebrou imports e nomes de colunas.
- **Depuração e provedor:** ajudou a diagnosticar os erros do Gemini (404, 503, 429 e um client fechado pelo garbage collector) e na migração para a Anthropic, mantendo ferramentas, dados e prompt intactos.
- **README:** rascunho e revisão deste documento; as decisões e suposições são minhas.

---

## Exemplos de conversa

Conversas reais rodadas com `--debug`, mostrando as ferramentas chamadas:

| Arquivo | Cenário | O que demonstra |
|---|---|---|
| [`examples/01-violoes-ate-1000.md`](examples/01-violoes-ate-1000.md) | "Quais opções de violões disponíveis custando até R$1000?" | Catálogo com filtro de preço e estoque |
| [`examples/02-endereco.md`](examples/02-endereco.md) | "Qual o endereço da loja?" | Consulta às políticas (endereço e horário) |
| [`examples/03-preco-takamine.md`](examples/03-preco-takamine.md) | "Quanto custa o Takamine GD20?" | Preço do catálogo + regras de parcelamento da política |
| [`examples/04-devolucao.md`](examples/04-devolucao.md) | "Me arrependi da minha compra, posso devolver meu pedido?" | Pedido + política de devolução (não trivial) |
| [`examples/05-fora-do-escopo.md`](examples/05-fora-do-escopo.md) | Acessório e assunto sem relação com a loja | Recusa educada e redirecionamento |
