# Citizen Assist AI

Assistente de terminal, feito em Python, que orienta **jovens no primeiro emprego** com informações de fontes oficiais, mostrando a fonte, a data de verificação e o aviso de limitação, **sem coletar dados pessoais**.

> GS 2026.2 · Pensamento Computacional e Automação com Python · FIAP · Desafio CitizenTech

## Integrantes

| Nome | RM |
|---|---|
| Eduardo Barcelos De Carvalho Braziliano | 573274 |
| Julia Johanson Peniche Dias Da Silva | 572220 |
| Lucas Bomfim Leite | 570420 |

Turma 1 CCPJ

## Público e problema escolhidos

**Público:** jovens (cerca de 16 a 24 anos) que estão arrumando o primeiro emprego.

**Problema:** quem vai trabalhar pela primeira vez precisa descobrir sozinho quais documentos tirar (Carteira de Trabalho Digital, CPF, título de eleitor, alistamento militar), como conferir se a empresa registrou o contrato, quais são seus direitos (FGTS, férias, 13º, seguro-desemprego) e a quem recorrer quando algo dá errado. A informação existe, mas está espalhada, em linguagem técnica e misturada com sites falsos que parecem oficiais.

**Solução:** uma base de 13 orientações em linguagem simples, cada uma com fonte oficial e data de conferência, consultada por pergunta em texto livre (busca com pontuação) ou por navegação em categorias.

## ODS relacionados

- **ODS 8 – Trabalho decente e crescimento econômico:** ajuda o jovem a entrar no mercado de trabalho formal e a conhecer seus direitos.
- **ODS 16 – Paz, justiça e instituições eficazes:** facilita o acesso à informação pública e aos canais oficiais, e alerta contra golpes.

## Como executar

Precisa apenas do Python 3.8 ou mais novo. Não há bibliotecas externas.

```bash
git clone <link-do-repositorio>
cd citizen-assist-ai
python main.py
```

Menu principal:

```
1. Fazer uma pergunta
2. Navegar por categorias
3. Ver indicadores
4. Exportar atendimentos (CSV)
0. Sair
```

Ao sair, o assistente pede uma nota de facilidade de uso (1 a 5), exporta `data/atendimentos.csv` e mostra os indicadores.

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py               # menu principal
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento (+ normalizar)
├── assistente.py         # classe Assistente
└── data/
    ├── base_conhecimento.csv   # a base (13 orientações, 4 categorias)
    ├── historico.csv           # um atendimento por linha (gerado pelo programa)
    ├── atendimentos.csv        # exportação dos atendimentos
    └── notas.csv               # notas de facilidade de uso (gerado pelo programa)
```

`notas.csv` é um arquivo extra criado pela equipe para guardar a nota de 1 a 5 e poder calcular a média entre execuções.

### Classes e composição

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` (e `resumo()`) |
| `BaseConhecimento` | caminho, orientacoes (lista de `Orientacao`), erros | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico, notas | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()` (e auxiliares) |

## Base de conhecimento

Arquivo `data/base_conhecimento.csv`, campos separados por `;` e itens múltiplos separados por `|`:

```
id;categoria;titulo;palavras_chave;resposta;documentos;onde;fonte;verificado_em
```

- 13 orientações, 4 categorias (Documentos, Trabalho, Direitos, Segurança), de 5 a 10 palavras-chave por orientação.
- Toda orientação tem fonte oficial e a data em que a equipe conferiu (`verificado_em`).
- Nenhum campo usa `;` dentro do texto.
- Arquivo ausente, vazio, com cabeçalho errado ou com linhas quebradas **não interrompe** o programa: o assistente avisa e segue funcionando (linhas ruins são ignoradas).

## Regra de pontuação

A pergunta e as palavras-chave são normalizadas (minúsculas, sem acentos, sem pontuação) por `normalizar()`. Depois, cada orientação recebe pontos:

| Regra | Pontos |
|---|---|
| Cada palavra-chave da orientação que aparece na pergunta | +3 |
| Cada palavra da pergunta (4 letras ou mais, sem repetir) que aparece no título | +1 |

| Melhor orientação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas (com 3 pontos ou mais).

**Ajustes da equipe em relação ao enunciado:**

1. A palavra-chave é comparada com espaços nas pontas (`" sus "`), então só vale a palavra inteira.
2. Algumas palavras comuns (como, para, quero, preciso, tirar...) não valem o ponto do título, para que "Como..." não dê pontos à toa. A lista está em `PALAVRAS_IGNORADAS`, em `base_conhecimento.py`.
3. `normalizar()` também remove `º`, `ª`, `-` e `/` (para "13º salário" virar "13 salario" e "seguro-desemprego" virar "seguro desemprego").

## Regras de atendimento

- **Navegação por categorias:** categorias, depois orientações numeradas, com "0 para voltar" em todas as telas.
- **Entradas inválidas:** número fora da faixa, letras, resposta vazia e s/n inválido nunca encerram o programa. Ctrl+C e fim da entrada também são tratados.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos, ou com `@`, é recusada e **não é registrada**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.csv`:

```
data;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;tempo_s
```

- Um **atendimento** começa na primeira pergunta e termina quando a pessoa responde "s" (ajudou) ou volta com 0. Reescrever a pergunta conta como nova **tentativa**.
- O tempo é medido com `time.time()` e `round(time.time() - inicio, 1)`.
- Indicadores calculados a partir de todos os atendimentos salvos (inclusive de execuções anteriores):
  - Resposta encontrada (%)
  - Taxa de acerto: ajudou (%)
  - Tempo médio para encontrar (média dos atendimentos em que havia orientação)
  - Tentativas por atendimento
  - Facilidade de uso (média das notas de 1 a 5)
  - Lista de dúvidas sem solução
- `exportar_csv()` grava `data/atendimentos.csv` com `open()` e `write()`, um registro por linha, separado por `;`.

## Integrações com outras disciplinas

O projeto utiliza arquivos em .csv que foi ensinando como ajustar e trabalhar com esses dados com base na matéria de Soluções em energias renováveis e sustentáveis durante o decorrer do ano letivo.

## Fontes consultadas

Conferidas em **04/11/2026** (as datas estão na coluna `verificado_em` da base):

- Carteira de Trabalho Digital: https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho
- Inscrição no CPF (Receita Federal): https://www.gov.br/pt-br/servicos/inscrever-no-cpf
- Título de eleitor (TSE): https://www.tse.jus.br/comunicacao/noticias/2021/Dezembro/confira-o-passo-a-passo-para-tirar-o-titulo-de-eleitor-pela-internet
- Conta gov.br: https://acesso.gov.br/faq/
- Alistamento militar: https://www.gov.br/pt-br/servicos/alistar-se-no-servico-militar-obrigatorio
- CLT (aprendizagem): https://www.planalto.gov.br/ccivil_03/Decreto-Lei/Del5452.htm
- Orientação trabalhista (158): https://www.gov.br/pt-br/servicos/buscar-orientacao-trabalhista
- Canais de atendimento e denúncia do Ministério do Trabalho (Agência gov): https://agenciagov.ebc.com.br/noticias/202607/saiba-como-acessar-os-canais-de-atendimento-do-ministerio-do-trabalho-e-emprego
- FGTS: https://www.fgts.gov.br/Pages/default.aspx
- Seguro-desemprego (Caixa): https://www.caixa.gov.br/beneficios-trabalhador/seguro-desemprego/Paginas/perguntas-frequentes.aspx
- Constituição Federal, art. 7º (férias e 13º): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm
- Portal gov.br: https://www.gov.br/pt-br

## Teste com usuários

- Pessoas testadas: `3` (idades aproximadas: `18, 19, 23`)
- Atendimentos: `10`

| Indicador | Resultado |
|---|---|
| Resposta encontrada (%) | `100%` |
| Taxa de acerto: ajudou (%) | `90%` |
| Tempo médio para encontrar | `13s` |
| Tentativas por atendimento | `2` |
| Facilidade de uso (1 a 5) | `4` |

**Dúvidas sem solução:**

- `Nenhuma dúvida sem solução foi identificada durante os testes`

**Melhoria feita a partir do teste:**  
 Foram adicionadas certas novas palavras-chave à base de conhecimento para melhorar o reconhecimento de perguntas dos usuários e aumentar a precisão das respostas.

## Limitações

- A busca compara palavras exatas: não entende sinônimos, plurais, erros de digitação nem o sentido da frase (por exemplo, "desempregado" só é entendido se estiver nas palavras-chave).
- A base é pequena (13 orientações) e foca no primeiro emprego.
- As regras e os prazos oficiais mudam. Por isso cada resposta traz a data de verificação e o aviso de que o assistente não é canal oficial. Sempre confira no site oficial.
- O bloqueio de dados pessoais olha apenas `@` e 8 ou mais dígitos. Dados escritos por extenso não são detectados.
- Os indicadores somam todas as execuções salvas em `historico.csv`.

## Vídeo técnico

[Vídeo Youtube](https://youtu.be/Qn3Vjxa2mKc) 
