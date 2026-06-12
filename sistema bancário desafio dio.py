MENU = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

CLIENTE = "Newton Douglas"
AGENCIA = "0001"
NUMERO_CONTA = "00553372-4"
LIMITE_SAQUES = 3
LIMITE_VALOR_SAQUE = 500


def depositar(saldo, extrato):
    try:
        valor = float(input("Informe o valor do depósito: "))
    except ValueError:
        print("Operação falhou! Valor inválido.")
        return saldo, extrato

    if valor <= 0:
        print("Operação falhou! O valor informado é inválido.")
        return saldo, extrato

    saldo += valor
    extrato += f"Depósito:  R$ {valor:>10.2f}\n"
    print(f"Depósito de R$ {valor:.2f} realizado com sucesso!")
    return saldo, extrato


def sacar(saldo, extrato, numero_saques):
    try:
        valor = float(input("Informe o valor do saque: "))
    except ValueError:
        print("Operação falhou! Valor inválido.")
        return saldo, extrato, numero_saques

    if valor <= 0:
        print("Operação falhou! O valor informado é inválido.")
    elif valor > saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
    elif valor > LIMITE_VALOR_SAQUE:
        print(f"Operação falhou! O valor do saque excede o limite de R$ {LIMITE_VALOR_SAQUE:.2f}.")
    elif numero_saques >= LIMITE_SAQUES:
        print("Operação falhou! Número máximo de saques excedido.")
    else:
        saldo -= valor
        extrato += f"Saque:     R$ {valor:>10.2f}\n"
        numero_saques += 1
        print(f"Saque de R$ {valor:.2f} realizado com sucesso!")

    return saldo, extrato, numero_saques


def exibir_extrato(saldo, extrato):
    print("\n=============== EXTRATO ===============")
    print(f"CLIENTE  - {CLIENTE}")
    print(f"AGÊNCIA  - {AGENCIA}   CONTA - {NUMERO_CONTA}")
    print("=======================================")
    print("LANÇAMENTOS")
    print("Não foram realizadas movimentações." if not extrato else extrato, end="")
    print(f"\n---------------------------------------")
    print(f"Saldo:     R$ {saldo:>10.2f}")
    print("=======================================\n")


def main():
    saldo = 0
    extrato = ""
    numero_saques = 0

    while True:
        opcao = input(MENU).strip().lower()

        if opcao == "d":
            saldo, extrato = depositar(saldo, extrato)

        elif opcao == "s":
            saldo, extrato, numero_saques = sacar(saldo, extrato, numero_saques)

        elif opcao == "e":
            exibir_extrato(saldo, extrato)

        elif opcao == "q":
            print("Obrigado por utilizar nossos serviços. Até logo!")
            break

        else:
            print("Operação inválida! Por favor, selecione novamente a operação desejada.")


main()
