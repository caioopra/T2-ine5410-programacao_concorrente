import time
from threading import Thread

from globals import *
from payment_system.bank import Bank
from utils.transaction import Transaction, TransactionStatus
from utils.logger import LOGGER
from utils.currency import get_exchange_rate


class PaymentProcessor(Thread):
    """
    Uma classe para representar um processador de pagamentos de um banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        IdentificadPaymor do processador de pagamentos.
    bank: Bank
        Banco sob o qual o processador de pagamentos operará.

    Métodos
    -------
    run():
        Inicia thread to PaymentProcessor
    process_transaction(transaction: Transaction) -> TransactionStatus:
        Processa uma transação bancária.
    """

    def __init__(self, _id: int, bank: Bank):
        Thread.__init__(self)
        self._id = _id
        self.bank = bank

    def run(self):
        """
        Esse método deve buscar Transactions na fila de transações do banco e processá-las
        utilizando o método self.process_transaction(self, transaction: Transaction).
        Ele não deve ser finalizado prematuramente (antes do banco realmente fechar).
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !

        LOGGER.info(
            f"Inicializado o PaymentProcessor {self._id} do Banco {self.bank._id}!"
        )
        queue = banks[self.bank._id].transaction_queue

        # @Caio: enquanto o banco está operando, processador de operações, executa
        while self.bank.operating:
            try:
                transaction = queue.pop(0)
                #LOGGER.info(f"Transaction_queue do Banco {self.bank._id}: {queue}")
                LOGGER.info(f"{self.bank._id} ") # TODO: trocar de volta o print
            except Exception as err:
                LOGGER.error(f"Falha em PaymentProcessor.run(): {err}")
            else:
                self.process_transaction(transaction)
            # time.sleep(3 * time_unit)  # Remova esse sleep após implementar sua solução!

        LOGGER.info(
            f"O PaymentProcessor {self._id} do banco {self.bank._id} foi finalizado."
        )

    def process_transaction(self, transaction: Transaction) -> TransactionStatus:
        """
        Esse método deverá processar as transações bancárias do banco ao qual foi designado.
        Caso a transferência seja realizada para um banco diferente (em moeda diferente), a
        lógica para transações internacionais detalhada no enunciado (README.md) deverá ser
        aplicada.
        Ela deve retornar o status da transacão processada.
        """
        # TODO: IMPLEMENTE/MODIFIQUE O CÓDIGO NECESSÁRIO ABAIXO !
        # @Caio
        # 0 = banco; 1 = conta
        
        # se for operação com o mesmo banco (nacional) 
        origin_acc = self.bank.accounts[transaction.origin[1] - 1]

        if transaction.origin[0] == transaction.destination[0]:

            destiny_acc = self.bank.accounts[transaction.destination[1] - 1]
            if transaction.origin[1]._id > transaction.destination[1]._id:
                destiny_acc.lock()
                origin_acc.lock()
            else:
                origin_acc.lock()
                destiny_acc.lock()
            
            withdraw = origin_acc.withdraw(transaction.amount)
            origin_acc.unlock()
            
            if withdraw:
                destiny_acc.deposit(transaction.amount)
                
                transaction.set_status(TransactionStatus.SUCCESSFUL)
            else:
                transaction.set_status(TransactionStatus.FAILED)
            destiny_acc.unlock()
        # operação internacional
            
        else:
            destiny_acc = self.bank.accounts[transaction.destination[1] - 1]
            if transaction.origin[0]._id > transaction.destination[0]._id:
                destiny_acc.lock()
                origin_acc.lock()
            else:
                origin_acc.lock()
                destiny_acc.lock()
            
            withdraw = origin_acc.withdraw((transaction.amount) * 1.01)  # taxa de 1% sobre o valor para operação internacional
            origin_acc.unlock()

            if withdraw:
                amount_after_conversion = transaction.amount*get_exchange_rate(origin_acc.currency,destiny_acc.currency)

                if destiny_acc.currency == 1:
                    self.bank.reserves.USD.lock()
                    self.bank.reserves.USD.deposit(amount_after_conversion * 1.01)
                    withdraw = self.bank.reserves.USD.withdraw(amount_after_conversion)
                    self.bank.reserves.USD.unlock()
                    
                elif destiny_acc.currency == 2:
                    self.bank.reserves.EUR.lock()
                    self.bank.reserves.EUR.deposit(amount_after_conversion * 1.01)
                    withdraw = self.bank.reserves.EUR.withdraw(amount_after_conversion)
                    self.bank.reserves.EUR.unlock()
                   
                elif destiny_acc.currency == 3:
                    self.bank.reserves.GBP.lock()
                    self.bank.reserves.GBP.deposit(amount_after_conversion * 1.01)
                    withdraw = self.bank.reserves.GBP.withdraw(amount_after_conversion)
                    self.bank.reserves.GBP.unlock()
                    
                elif destiny_acc.currency == 4:
                    self.bank.reserves.JPY.lock()
                    self.bank.reserves.JPY.deposit(amount_after_conversion * 1.01)
                    withdraw = self.bank.reserves.JPY.withdraw(amount_after_conversion)
                    self.bank.reserves.JPY.unlock()
                    
                elif destiny_acc.currency == 5:
                    self.bank.reserves.CHF.lock()
                    self.bank.reserves.CHF.deposit(amount_after_conversion * 1.01)
                    withdraw = self.bank.reserves.CHF.withdraw(amount_after_conversion)
                    self.bank.reserves.CHF.unlock()

                elif destiny_acc.currency == 6:
                    self.bank.reserves.BRL.lock()
                    self.bank.reserves.BRL.deposit(amount_after_conversion * 1.01)
                    withdraw = self.bank.reserves.BRL.withdraw(amount_after_conversion)
                    self.bank.reserves.BRL.unlock()
                
                if withdraw:
                    destiny_acc.deposit(amount_after_conversion)
                    destiny_acc.unlock()
            
            # TODO: implementar transção internacional
            """
            conta_origem -> banco_conta_origem -> conta_destino
                -> trancar conta de destino antes de mexer nela?
            """
            

        LOGGER.info(
            f"PaymentProcessor {self._id} do Banco {self.bank._id} iniciando processamento da Transaction {transaction._id}!"
        )

        # NÃO REMOVA ESSE SLEEP!
        # Ele simula uma latência de processamento para a transação.
        time.sleep(3 * time_unit)

        transaction.set_status(TransactionStatus.SUCCESSFUL)
        return transaction.status
