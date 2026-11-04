"""Classe Assistente: faz o atendimento, guarda o histórico e calcula os indicadores."""

import os
import time

LIMITE_ALTA = 6      # 6 pontos ou mais  -> confiança ALTA
LIMITE_MEDIA = 3     # 3 a 5 pontos      -> confiança MÉDIA
MAX_ALTERNATIVAS = 2

CAMPOS_HISTORICO = ["data", "origem", "pergunta", "id_orientacao",
                    "encontrou", "ajudou", "tentativas", "tempo_s"]


class Assistente:
    """Quem conversa com o cidadão. Tem uma BaseConhecimento (composição)."""

    def __init__(self, nome, base, pasta_dados="data"):
        self.nome = nome
        self.base = base
        self.historico = []   # lista de dicionários, um por atendimento
        self.notas = []       # notas de facilidade de uso (1 a 5)
        self.pasta_dados = pasta_dados
        self.arq_historico = os.path.join(pasta_dados, "historico.csv")
        self.arq_atendimentos = os.path.join(pasta_dados, "atendimentos.csv")
        self.arq_notas = os.path.join(pasta_dados, "notas.csv")
        self.carregar_historico()

    # ------------------------------------------------------- entrada de dados
    def ler(self, mensagem):
        try:
            return input(mensagem).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "0"

    def ler_opcao(self, mensagem, maximo):
        """Pede um número de 0 até 'maximo'. Repete até a entrada ser válida."""
        while True:
            texto = self.ler(mensagem)
            if texto == "":
                print("Atenção: você não digitou nada.")
            elif not texto.isdigit():
                print("Atenção: digite apenas o número da opção.")
            elif int(texto) > maximo:
                print(f"Atenção: escolha um número de 0 a {maximo}.")
            else:
                return int(texto)

    def ler_sn(self, mensagem):
        """Pergunta s/n. Devolve True para 's'. O '0' (voltar) vale como 'n'."""
        while True:
            texto = self.ler(mensagem).lower()
            if texto == "s":
                return True
            if texto in ("n", "0"):
                return False
            print("Atenção: responda apenas com s ou n.")

    # --------------------------------------------------------- regras gerais
    def contem_dado_pessoal(self, texto):
        """Bloqueia e-mail (@) e qualquer texto com 8 ou mais dígitos
        (CPF, telefone, RG...)."""
        digitos = 0
        for caractere in texto:
            if caractere.isdigit():
                digitos += 1
        return "@" in texto or digitos >= 8

    def nivel_confianca(self, pontos):
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None

    def mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        sugestoes = [o.palavras_chave[0] for o in self.base.orientacoes[:6]]
        if sugestoes:
            print("Tente outras palavras, por exemplo: " + ", ".join(sugestoes) + ".")
        categorias = self.base.categorias()
        if categorias:
            print("Ou use a navegação por categorias (opção 2 do menu): "
                  + ", ".join(categorias) + ".")
        print("Aviso: este assistente NÃO é um canal oficial.")

    # --------------------------------------------------- atendimento por texto
    def perguntar(self):
        """Atendimento por pergunta em texto livre. Um atendimento começa na
        primeira pergunta e termina quando a pessoa diz que a dúvida foi
        resolvida (s) ou volta com 0. Reescrever a pergunta conta como tentativa."""
        print("\n--- Pergunte com suas palavras ---")
        print("Não digite CPF, telefone ou e-mail.")

        while True:
            inicio = time.time()
            tentativas = 0
            encontrou = False
            ultima_pergunta = ""
            ultimo_id = ""
            resolvido = False

            while not resolvido:
                texto = self.ler("\nDigite sua dúvida (0 para voltar): ")

                if texto == "0":
                    if tentativas > 0:   # a pessoa desistiu sem resolver
                        self.registrar("pergunta", ultima_pergunta, ultimo_id,
                                       encontrou, False, tentativas,
                                       round(time.time() - inicio, 1))
                    return

                if texto == "":
                    print("Atenção: digite uma pergunta ou 0 para voltar.")
                    continue

                if self.contem_dado_pessoal(texto):
                    # não registra, não busca, não guarda
                    print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                    continue

                tentativas += 1
                ultima_pergunta = texto
                resultados = [r for r in self.base.buscar(texto) if r[0] >= LIMITE_MEDIA]

                if not resultados:
                    self.mostrar_nao_encontrei()
                    continue

                encontrou = True
                pontos, melhor = resultados[0]
                ultimo_id = melhor.id
                print(f"\nConfiança da resposta: {self.nivel_confianca(pontos)} ({pontos} pontos)")
                melhor.exibir()

                alternativas = resultados[1:1 + MAX_ALTERNATIVAS]
                if alternativas:
                    print("\nOutras orientações que podem ajudar:")
                    for pts, alt in alternativas:
                        print(f"  - {alt.resumo()} ({pts} pontos)")

                if self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    resolvido = True
                elif alternativas and self.ler_sn("Quer ver as outras orientações? (s/n): "):
                    for pts, alt in alternativas:
                        print(f"\nConfiança da resposta: {self.nivel_confianca(pts)} ({pts} pontos)")
                        alt.exibir()
                        if self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): "):
                            ultimo_id = alt.id
                            resolvido = True
                            break
                    if not resolvido:
                        print("Tente reescrever a dúvida com outras palavras.")
                else:
                    print("Tente reescrever a dúvida com outras palavras.")

            self.registrar("pergunta", ultima_pergunta, ultimo_id, True, True,
                           tentativas, round(time.time() - inicio, 1))

    # ---------------------------------------------------- navegação por categoria
    def navegar(self):
        """Categorias -> orientações -> orientação, com '0 para voltar' em todas as telas."""
        categorias = self.base.categorias()
        if not categorias:
            print("\nNão há categorias disponíveis (a base de conhecimento está vazia).")
            return

        while True:
            inicio = time.time()
            print("\n=== Categorias ===")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")
            escolha = self.ler_opcao("Escolha uma categoria: ", len(categorias))
            if escolha == 0:
                return

            categoria = categorias[escolha - 1]
            orientacoes = self.base.por_categoria(categoria)

            while True:
                print(f"\n=== {categoria} ===")
                for numero, orientacao in enumerate(orientacoes, start=1):
                    print(f"{numero}. {orientacao.titulo}")
                print("0. Voltar")
                escolha2 = self.ler_opcao("Escolha uma orientação: ", len(orientacoes))
                if escolha2 == 0:
                    break

                orientacao = orientacoes[escolha2 - 1]
                orientacao.exibir()
                ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", f"categoria {categoria} - {orientacao.titulo}",
                               orientacao.id, True, ajudou, 1,
                               round(time.time() - inicio, 1))
                inicio = time.time()

    # --------------------------------------------------------------- histórico
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        """Guarda o atendimento na memória e acrescenta uma linha em data/historico.csv."""
        pergunta = pergunta.replace(";", ",").replace("\n", " ")
        atendimento = {
            "data": time.strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo": tempo,
        }
        self.historico.append(atendimento)

        try:
            novo = not os.path.exists(self.arq_historico) or os.path.getsize(self.arq_historico) == 0
            with open(self.arq_historico, "a", encoding="utf-8") as arquivo:
                if novo:
                    arquivo.write(";".join(CAMPOS_HISTORICO) + "\n")
                arquivo.write(self.linha_csv(atendimento) + "\n")
        except OSError:
            print("Aviso: não foi possível salvar o atendimento em disco.")

    def linha_csv(self, a):
        """Transforma um atendimento (dicionário) em uma linha com campos separados por ;"""
        campos = [a["data"], a["origem"], a["pergunta"], str(a["id_orientacao"]),
                  "sim" if a["encontrou"] else "nao", "sim" if a["ajudou"] else "nao",
                  str(a["tentativas"]), str(a["tempo"])]
        return ";".join(campos)

    def carregar_historico(self):
        """Lê historico.csv e notas.csv de execuções anteriores, se existirem.
        Linhas inválidas são ignoradas, arquivo ausente não é erro."""
        self.historico = []
        self.notas = []

        if os.path.exists(self.arq_historico):
            try:
                with open(self.arq_historico, "r", encoding="utf-8") as arquivo:
                    for linha in arquivo:
                        campos = linha.strip().split(";")
                        if len(campos) != len(CAMPOS_HISTORICO) or campos[0] == "data":
                            continue
                        try:
                            self.historico.append({
                                "data": campos[0], "origem": campos[1], "pergunta": campos[2],
                                "id_orientacao": campos[3],
                                "encontrou": campos[4] == "sim", "ajudou": campos[5] == "sim",
                                "tentativas": int(campos[6]), "tempo": float(campos[7]),
                            })
                        except ValueError:
                            continue
            except (OSError, UnicodeDecodeError):
                print("Aviso: não foi possível ler o histórico anterior. Começando do zero.")

        if os.path.exists(self.arq_notas):
            try:
                with open(self.arq_notas, "r", encoding="utf-8") as arquivo:
                    for linha in arquivo:
                        campos = linha.strip().split(";")
                        if len(campos) == 2 and campos[1].isdigit() and 1 <= int(campos[1]) <= 5:
                            self.notas.append(int(campos[1]))
            except (OSError, UnicodeDecodeError):
                pass

    # -------------------------------------------------------------- indicadores
    def indicadores(self):
        """Calcula os indicadores com todos os atendimentos salvos. Devolve um dicionário."""
        total = len(self.historico)
        encontrados = [a for a in self.historico if a["encontrou"]]
        ajudados = [a for a in self.historico if a["ajudou"]]

        sem_solucao = []
        for a in self.historico:
            if not a["ajudou"] and a["pergunta"] not in sem_solucao:
                sem_solucao.append(a["pergunta"])

        return {
            "total": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1) if total else 0.0,
            "acerto_pct": round(100 * len(ajudados) / total, 1) if total else 0.0,
            "tempo_medio": round(sum(a["tempo"] for a in encontrados) / len(encontrados), 1)
                           if encontrados else 0.0,
            "tentativas_media": round(sum(a["tentativas"] for a in self.historico) / total, 1)
                                if total else 0.0,
            "facilidade": round(sum(self.notas) / len(self.notas), 1) if self.notas else None,
            "sem_solucao": sem_solucao,
        }

    def mostrar_indicadores(self):
        ind = self.indicadores()
        print("\n=== Indicadores (todos os atendimentos salvos) ===")
        print(f"Atendimentos registrados:   {ind['total']}")
        print(f"Resposta encontrada (%):    {ind['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {ind['acerto_pct']}")
        print(f"Tempo médio para encontrar: {ind['tempo_medio']} s")
        print(f"Tentativas por atendimento: {ind['tentativas_media']}")
        if ind["facilidade"] is None:
            print("Facilidade de uso (1 a 5):  ainda sem notas")
        else:
            print(f"Facilidade de uso (1 a 5):  {ind['facilidade']} ({len(self.notas)} nota(s))")
        if ind["sem_solucao"]:
            print("Dúvidas sem solução:")
            for pergunta in ind["sem_solucao"]:
                print(f"  - {pergunta}")
        else:
            print("Dúvidas sem solução:        nenhuma")

    def pedir_nota(self):
        """Ao sair, pede a nota de facilidade de uso (1 a 5). 0 pula."""
        nota = self.ler_opcao("\nDê uma nota de facilidade de uso de 1 a 5 (0 para pular): ", 5)
        if nota == 0:
            return
        self.notas.append(nota)
        try:
            novo = not os.path.exists(self.arq_notas) or os.path.getsize(self.arq_notas) == 0
            with open(self.arq_notas, "a", encoding="utf-8") as arquivo:
                if novo:
                    arquivo.write("data;nota\n")
                arquivo.write(time.strftime("%Y-%m-%d %H:%M:%S") + ";" + str(nota) + "\n")
        except OSError:
            print("Aviso: não foi possível salvar a nota em disco.")

    # ----------------------------------------------------------------- exportação
    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv com open() e write(),
        um registro por linha, campos separados por ponto e vírgula."""
        try:
            with open(self.arq_atendimentos, "w", encoding="utf-8") as arquivo:
                arquivo.write(";".join(CAMPOS_HISTORICO) + "\n")
                for atendimento in self.historico:
                    arquivo.write(self.linha_csv(atendimento) + "\n")
        except OSError:
            print("Aviso: não foi possível exportar o arquivo de atendimentos.")
            return False
        print(f"Atendimentos exportados em: {self.arq_atendimentos}")
        return True
