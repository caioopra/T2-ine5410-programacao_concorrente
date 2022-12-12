from typing import Tuple

from payment_system.account import Account, CurrencyReserves
from utils.transaction import Transaction
from utils.currency import Currency
from utils.logger import LOGGER

from threading import Lock, Semaphore

class Bank:
    """
    Uma classe para representar um Banco.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id : int
        Identificador do banco.
    currency : Currency
        Moeda corrente das contas bancárias do banco.
    reserves : CurrencyReserves
        Dataclass de contas bancárias contendo as reservas internas do banco.
    operating : bool
        Booleano que indica se o banco está em funcionamento ou não.
    accounts : List[Account]
        Lista contendo as contas bancárias dos clientes do banco.
    transaction_queue : Queue[Transaction]
        Fila FIFO contendo as transações bancárias pendentes que ainda serão processadas.
    payment_processors : List[PaymentProcessor]
        Lista dos PaymentProcessors do banco
    nacional_transactions : int
        Quantidade de transações nacionais realizadas pelo banco
    nacional_transactions_lock : Lock()
        Lock para proteção do contador de transações nacionais
    internacional_transactions : int
        Quantidade de transações internacionais realizadas pelo banco
    internacional_transactions_loc: Lock
        Lock para proteção do contador de transações internacionais
    bank_profit : float
        Lucro obtido pelo banco
    bank_profit_lock = Lock()
        Lock para proteção da variável com lucro do banco

    Métodos
    -------
    new_account(balance: int = 0, overdraft_limit: int = 0) -> None:
        Cria uma nova conta bancária (Account) no banco.
    new_transfer(origin: Tuple[int, int], destination: Tuple[int, int], amount: int, currency: Currency) -> None:
        Cria uma nova transação bancária.
    info() -> None:
        Printa informações e estatísticas sobre o funcionamento do banco.

    """

    def __init__(self, _id: int, currency: Currency):
        self._id = _id
        self.currency = currency
        self.reserves = CurrencyReserves()
        self.operating = False
        self.accounts = []
        self.transaction_queue = []
        self.payment_processors = []
        
        # dados para prints ao final da execução
        self.nacional_transactions = 0
        self.internacional_transactions = 0
        self.bank_profit = 0
        
        self.nacional_transactions_lock = Lock()
        self.internacional_transactions_lock = Lock()
        self.bank_profit_lock = Lock()
        self.queue_semaphore = Semaphore()
        

    def new_account(self, balance: int = 0, overdraft_limit: int = 0) -> None:
        """
        Esse método deverá criar uma nova conta bancária (Account) no banco com determinado
        saldo (balance) e limite de cheque especial (overdraft_limit).
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        # Gera _id para a nova Account (1a conta de usuários: id = 7)
        acc_id = len(self.accounts) + 1

        # Cria instância da classe Account
        acc = Account(
            _id=acc_id,
            _bank_id=self._id,
            currency=self.currency,
            balance=balance,
            overdraft_limit=overdraft_limit,
        )

        # Adiciona a Account criada na lista de contas do banco
        self.accounts.append(acc)

    def info(self) -> None:
        """
        Essa função deverá printar os seguintes dados utilizando o LOGGER fornecido:
        1. Saldo de cada moeda nas reservas internas do banco
        2. Número de transferências nacionais e internacionais realizadas
        3. Número de contas bancárias registradas no banco
        4. Saldo total de todas as contas bancárias (dos clientes) registradas no banco
        5. Lucro do banco: taxas de câmbio acumuladas + juros de cheque especial acumulados
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!
        print("---" * 30)
        LOGGER.info(f"Estatísticas do Banco Nacional {self._id}:\n")
        
        LOGGER.info(" - Saldo de cada moeda nas reservas:")
        LOGGER.info(f"   > USD = {self.reserves.USD.balance}")
        LOGGER.info(f"   > EUR = {self.reserves.EUR.balance}")
        LOGGER.info(f"   > GBP = {self.reserves.GBP.balance}")
        LOGGER.info(f"   > JPY = {self.reserves.JPY.balance}")
        LOGGER.info(f"   > CHF = {self.reserves.CHF.balance}")
        LOGGER.info(f"   > BRL = {self.reserves.BRL.balance}\n")
        
        LOGGER.info(f" - Número de transferências nacionais: {self.nacional_transactions}\n")
        
        LOGGER.info(f" - Número de transferências internacionais: {self.internacional_transactions}\n")
        
        LOGGER.info(f" - Número de contas bancárias no banco: {len(self.accounts)}\n")
        
        LOGGER.info(f" - Saldo total das contas no banco:")
        for conta in self.accounts:
            LOGGER.info(f"   > Conta {conta._id}: {conta.balance}")
        LOGGER.info("\n")
        
        LOGGER.info(f"Lucro do banco: {self.bank_profit}\n")

