"""Classe Orientacao: uma informação da base (um registro do CSV)."""


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    AVISO = "este assistente NÃO é um canal oficial."

    def __init__(self, identificador, categoria, titulo, palavras_chave,
                 resposta, documentos, onde, fonte, verificado_em):
        self.id = int(identificador)
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave   # lista de textos
        self.resposta = resposta
        self.documentos = documentos           # lista de textos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def resumo(self):
        """Uma linha curta, usada na lista de alternativas e nos menus."""
        return f"{self.titulo}  [{self.categoria}]"

    def exibir(self):
        """Mostra a orientação completa, com fonte, data e aviso."""
        print(f"\n>> {self.resumo()}")
        print(self.resposta)
        print("Documentos necessários:")
        if self.documentos:
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("  - Nenhum documento informado")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {self.AVISO}")
