from tkinter import Menu


class Conta:
    cliente = "Newton Nascimento"
    agencia = "001"
    conta =  "0553372-4"
    saldo = 0

def menu (self):
    print("-" * 30)
    print(f'MENU DE ENTRADA' )
    print( '-' * 30)
    print( "Opções" )
    print( '1 - Extrato')
    print( '2 - Depósito')
    print( '3 - Saque')
    print( '4 - Sair')
    opção = input("Digite a opção desejada: ")
    if opção == "1":
        proprio.extrato ()
    elif opção == "2":
        valor = float(input("Digite a opção desejada: "))
        proprio.depositar (valor)
    elif opção == "4":
        exit()
        

def depositar( self, valor):

def sacar(self, valor):

def extrato(self, ultimo = 0):
