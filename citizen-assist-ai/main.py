"""Citizen Assist AI - assistente de orientação ao cidadão (terminal).

Público: jovens no primeiro emprego.
Execução: python main.py
"""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA, "data")
CAMINHO_BASE = os.path.join(PASTA_DADOS, "base_conhecimento.csv")


def mostrar_menu():
    print("\n===== MENU =====")
    print("1. Fazer uma pergunta")
    print("2. Navegar por categorias")
    print("3. Ver indicadores")
    print("4. Exportar atendimentos (CSV)")
    print("0. Sair")


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    total = base.carregar()          # usa open(), for e split() para ler a base

    assistente = Assistente("Citizen Assist AI", base, PASTA_DADOS)

    print("=" * 56)
    print(f" {assistente.nome} - orientação para jovens no primeiro emprego")
    print("=" * 56)
    print("Este assistente NÃO é um canal oficial e NÃO coleta dados pessoais.")
    print("Nunca digite CPF, telefone ou e-mail.")

    if total == 0:
        print("\nAtenção: a base de conhecimento não foi carregada.")
    else:
        print(f"\nBase carregada: {total} orientações em {len(base.categorias())} categorias.")
    for erro in base.erros:
        print(f"Aviso: {erro}")

    while True:
        mostrar_menu()
        opcao = assistente.ler_opcao("Escolha uma opção: ", 4)

        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.mostrar_indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        else:
            break

    assistente.pedir_nota()
    assistente.exportar_csv()
    assistente.mostrar_indicadores()
    print("\nObrigado por usar o Citizen Assist AI. Até a próxima!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma encerrado.")
