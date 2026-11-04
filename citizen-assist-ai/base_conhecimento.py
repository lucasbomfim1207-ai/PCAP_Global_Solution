"""Classe BaseConhecimento: lê o CSV, lista categorias e busca a melhor orientação."""

from orientacao import Orientacao

# Cabeçalho esperado na primeira linha do CSV (campos separados por ;)
CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
           "é": "e", "è": "e", "ê": "e", "ë": "e",
           "í": "i", "ì": "i", "î": "i", "ï": "i",
           "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
           "ú": "u", "ù": "u", "û": "u", "ü": "u", "ç": "c"}

# Sinais que viram espaço (inclui º e ª para que "13º" vire "13")
SINAIS = "?!.,;:()[]{}\"'-/\\ºª°"

# Palavras comuns que NÃO valem ponto quando aparecem no título (regra de +1)
PALAVRAS_IGNORADAS = {"como", "para", "qual", "quais", "onde", "quando", "quero",
                      "preciso", "faco", "fazer", "sobre", "minha", "meu", "tenho",
                      "isso", "essa", "esse", "pelo", "pela", "com", "uma", "seu",
                      "sua", "voce", "posso", "pode", "tirar"}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação. Devolve com espaço nas pontas,
    para que " sus " só case com a palavra inteira (e não com "sustento")."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """O conjunto de todas as orientações (composição: lista de Orientacao)."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []   # lista de objetos Orientacao
        self.erros = []         # mensagens sobre problemas ao ler o arquivo

    # ---------------------------------------------------------------- leitura
    def carregar(self):
        """Lê o CSV com open() + for + split(";"). Nunca interrompe o programa:
        arquivo ausente ou linhas inválidas só geram avisos em self.erros.
        Devolve quantas orientações foram carregadas."""
        self.orientacoes = []
        self.erros = []

        try:
            arquivo = open(self.caminho, "r", encoding="utf-8-sig")
        except OSError:
            self.erros.append(f"Arquivo não encontrado ou sem acesso: {self.caminho}")
            return 0

        try:
            with arquivo:
                cabecalho_lido = False
                ids_vistos = []
                for numero, linha in enumerate(arquivo, start=1):
                    linha = linha.strip()
                    if linha == "":
                        continue

                    campos = [c.strip() for c in linha.split(";")]

                    if not cabecalho_lido:
                        if campos != CAMPOS:
                            self.erros.append("Cabeçalho do CSV inválido (linha %d)." % numero)
                            return 0
                        cabecalho_lido = True
                        continue

                    if len(campos) != len(CAMPOS):
                        self.erros.append(f"Linha {numero} ignorada: número de campos incorreto.")
                        continue

                    # cada linha vira um dicionário {campo: valor}
                    registro = dict(zip(CAMPOS, campos))

                    if not registro["id"].isdigit() or registro["id"] in ids_vistos:
                        self.erros.append(f"Linha {numero} ignorada: id inválido ou repetido.")
                        continue

                    palavras = [p.strip() for p in registro["palavras_chave"].split("|") if p.strip()]
                    documentos = [d.strip() for d in registro["documentos"].split("|") if d.strip()]

                    if registro["titulo"] == "" or registro["categoria"] == "" or not palavras:
                        self.erros.append(f"Linha {numero} ignorada: faltam título, categoria ou palavras-chave.")
                        continue

                    ids_vistos.append(registro["id"])
                    self.orientacoes.append(Orientacao(
                        registro["id"], registro["categoria"], registro["titulo"],
                        palavras, registro["resposta"], documentos, registro["onde"],
                        registro["fonte"], registro["verificado_em"]))

                if not cabecalho_lido:
                    self.erros.append("O arquivo da base está vazio.")
        except (OSError, UnicodeDecodeError):
            self.erros.append("Não foi possível ler o arquivo da base (formato inválido).")
            self.orientacoes = []

        return len(self.orientacoes)

    # ------------------------------------------------------------- categorias
    def categorias(self):
        """Lista de categorias, sem repetição, na ordem em que aparecem."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Todas as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    # ------------------------------------------------------------------ busca
    def pontuar(self, pergunta, orientacao):
        """Regras de pontuação:
        +3 para cada palavra-chave da orientação que aparece na pergunta
        +1 para cada palavra da pergunta (4+ letras) que aparece no título."""
        pergunta_norm = normalizar(pergunta)
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            chave = normalizar(palavra_chave)
            if chave.strip() != "" and chave in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo_norm = normalizar(orientacao.titulo)
        contadas = []
        for palavra in pergunta_norm.split():
            if len(palavra) >= 4 and palavra not in PALAVRAS_IGNORADAS and palavra not in contadas:
                contadas.append(palavra)
                if " " + palavra + " " in titulo_norm:
                    pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a
        menor pontuação. Orientações com 0 ponto não entram."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: (-tupla[0], tupla[1].id))
        return resultados
