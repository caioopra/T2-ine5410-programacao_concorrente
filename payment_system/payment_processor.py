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
                self.bank.queue_semaphore.acquire()
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
            if transaction.origin[1] != transaction.destination[1]:
                with self.bank.nacional_transactions_lock:
                    self.bank.nacional_transactions += 1

                destiny_acc = self.bank.accounts[transaction.destination[1] - 1]

                if transaction.origin[1] > transaction.destination[1]:
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
            # incrementa uma transação internacional nos dois bancos
            with self.bank.internacional_transactions_lock:
                self.bank.internacional_transactions += 1
            with banks[transaction.destination[0]].internacional_transactions_lock:
                banks[transaction.destination[0]].internacional_transactions += 1

            destiny_acc = banks[transaction.destination[0]].accounts[transaction.destination[1] - 1]

            if transaction.origin[0] > transaction.destination[0]:
                destiny_acc.lock()
                origin_acc.lock()
   
            else:
                origin_acc.lock()
                destiny_acc.lock()


            withdraw = origin_acc.withdraw((transaction.amount) * 1.01)  # taxa de 1% sobre o valor para operação internacional
            origin_acc.unlock()

            
            if withdraw:

                amount_after_conversion = transaction.amount * get_exchange_rate(origin_acc.currency, destiny_acc.currency)

                if origin_acc.currency.value == 1:
                    origin = self.bank.reserves.USD
                    
                elif origin_acc.currency.value == 2:
                    origin = self.bank.reserves.EUR

                elif origin_acc.currency.value == 3:
                    origin = self.bank.reserves.GBP

                elif origin_acc.currency.value == 4:
                    origin = self.bank.reserves.JPY
                    
                elif origin_acc.currency.value == 5:
                    origin = self.bank.reserves.CHF

                elif origin_acc.currency.value == 6:
                    origin = self.bank.reserves.BRL

                origin.lock()
                origin.deposit(transaction.amount*1.01)
                origin.unlock()

                if destiny_acc.currency.value == 1:
                    destiny = self.bank.reserves.USD
                    
                elif destiny_acc.currency.value == 2:
                    destiny = self.bank.reserves.EUR

                elif destiny_acc.currency.value == 3:
                    destiny = self.bank.reserves.GBP
                    
                elif destiny_acc.currency.value == 4:
                    destiny = self.bank.reserves.JPY

                elif destiny_acc.currency.value == 5:
                    destiny = self.bank.reserves.CHF

                elif destiny_acc.currency.value == 6:
                    destiny = self.bank.reserves.BRL

                destiny.lock()
                withdraw = destiny.withdraw(amount_after_conversion)
                destiny.unlock()

                if withdraw:
                    destiny_acc.deposit(amount_after_conversion)

            
            destiny_acc.unlock()
            
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
