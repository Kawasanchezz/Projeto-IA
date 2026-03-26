# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Para que serve na Credix |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores, ou seja, dar continuidade ao atendimento de forma mais eficiente. |
| `perfil_investidor.json` | JSON | Personalizar explicações sobre as dívidas e nessecidades de aprendizado do cliente. |
| `produtos_financeiros.json` | JSON | Conhecer os produtos disponiveis para que elas possam ser ensinado ao cliente. |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente e usar essas informações de forma didática. |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Os dados foram ajustados para representar cenários mais próximos da realidade, incluindo diferentes perfis de clientes, variedade de transações e exemplos de produtos financeiros. Além disso, foram organizados para facilitar a leitura e interpretação pelo sistema, melhorando a qualidade das respostas geradas.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos nos formatos CSV e JSON são carregados no início da execução do sistema. Após o carregamento, os dados são estruturados e armazenados em memória para acesso rápido durante as interações.

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados são utilizados de forma dinâmica. O sistema consulta apenas as informações relevantes para cada interação e as inclui no contexto do prompt,
evitando excesso de informação e garantindo respostas mais precisas e eficientes.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```text

Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado
- Idade: 32 anos
- Saldo disponível: R$ 5.000
- Renda mensal: R$ 3.500

Resumo Financeiro:
- Média de gastos mensais: R$ 2.800
- Categoria com maior gasto: Alimentação
- Possui dívidas: Não

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
- 05/11: Transporte - R$ 120
- 07/11: Restaurante - R$ 90

Produtos utilizados:
- Conta corrente
- Cartão de crédito
- Poupança

Objetivos do cliente:
- Organizar melhor os gastos
- Começar a investir com segurança

Contexto de atendimento:
- Última interação: Pergunta sobre controle de gastos
- Preferência: Explicações simples e diretas

```
