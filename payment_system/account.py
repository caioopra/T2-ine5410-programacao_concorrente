from dataclasses import dataclass

from utils.currency import Currency
from utils.logger import LOGGER
from globals import banks

from threading import Lock


@dataclass
class Account:
    """
    Uma classe para representar uma conta bancária.
    Se você adicionar novos atributos ou métodos, lembre-se de atualizar essa docstring.

    ...

    Atributos
    ---------
    _id: int
        Identificador da conta bancária.
    _bank_id: int
        Identificador do banco no qual a conta bancária foi criada.
    currency : Currency
        Moeda corrente da conta bancária.
    balance : int
        Saldo da conta bancária.
    overdraft_limit : int
        Limite de cheque especial da conta bancária.
    _lock : Lock
        Lock da conta bancária.

    Métodos
    -------
    info() -> None:
        Printa informações sobre a conta bancária.
    deposit(amount: int) -> None:
        Adiciona o valor `amount` ao saldo da conta bancária.
    withdraw(amount: int) -> None:
        Remove o valor `amount` do saldo da conta bancária.
    lock() -> None:
        Faz acquire no lock da conta
    unlock() -> None:
        Faz release no lock da conta
    """
    def __init__(self, _id, _bank_id, currency, balance=0, overdraft_limit=0):
        self._id = _id
        self._bank_id = _bank_id
        self.currency = currency
        self.balance = balance
        self.overdraft_limit = overdraft_limit
        # @Caio: cada conta possui lock proprio para operações
        self._lock = Lock()

    def info(self) -> None:
        """
        Esse método printa informações gerais sobre a conta bancária.
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES, SE NECESSÁRIAS, NESTE MÉTODO!

        pretty_balance = f"{format(round(self.balance/100), ',d')}.{self.balance%100:02d} {self.currency.name}"
        pretty_overdraft_limit = f"{format(round(self.overdraft_limit/100), ',d')}.{self.overdraft_limit%100:02d} {self.currency.name}"
        LOGGER.info(
            f"Account::{{ _id={self._id}, _bank_id={self._bank_id}, balance={pretty_balance}, overdraft_limit={pretty_overdraft_limit} }}"
        )

    def deposit(self, amount: int) -> bool:
        """
        Esse método deverá adicionar o valor `amount` passado como argumento ao saldo da conta bancária
        (`balance`). Lembre-se que esse método pode ser chamado concorrentemente por múltiplos
        PaymentProcessors, então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        # @Caio: operação já protegida com lock da conta pelo método que a chama
        self.balance += amount

        LOGGER.info(f"deposit({amount}) successful!")
        return True

    def withdraw(self, amount: int) -> bool:
        """
        Esse método deverá retirar o valor `amount` especificado do saldo da conta bancária (`balance`).
        Deverá ser retornado um valor bool indicando se foi possível ou não realizar a retirada.
        Lembre-se que esse método pode ser chamado concorrentemente por múltiplos PaymentProcessors,
        então modifique-o para garantir que não ocorram erros de concorrência!
        """
        # TODO: IMPLEMENTE AS MODIFICAÇÕES NECESSÁRIAS NESTE MÉTODO !

        # se tiver a quantia para retirar
        if self.balance >= amount:
            self.balance -= amount
            LOGGER.info(f"withdraw({amount}) successful!")
            return True
        else:       # se não tiver a quantia, verifica se consegue usar o cheque especial
            overdrafted_amount = abs(self.balance - amount)  # quantidade que precisa do cheque especial
            if self.overdraft_limit >= overdrafted_amount:
                self.balance -= ((amount - overdrafted_amount) + overdrafted_amount * 1.05)
                
                bank = banks[self._bank_id]
                bank.bank_profit_lock.acquire()
                bank.bank_profit += overdrafted_amount * 0.05
                bank.bank_profit_lock.release()
                
                LOGGER.info(f"withdraw({amount}) successful with overdraft!")

                return True
            else:
                LOGGER.warning(f"withdraw({amount}) failed, no balance!")
                return False

    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

# @dataclass
# class CurrencyReserves:
#     """
#     Uma classe de dados para armazenar as reservas do banco, que serão usadas
#     para câmbio e transferências internacionais.
#     OBS: NÃO É PERMITIDO ALTERAR ESSA CLASSE!
#     """

#     USD: Account = Account(_id=1, _bank_id=0, currency=Currency.USD)
#     EUR: Account = Account(_id=2, _bank_id=0, currency=Currency.EUR)
#     GBP: Account = Account(_id=3, _bank_id=0, currency=Currency.GBP)
#     JPY: Account = Account(_id=4, _bank_id=0, currency=Currency.JPY)
#     CHF: Account = Account(_id=5, _bank_id=0, currency=Currency.CHF)
#     BRL: Account = Account(_id=6, _bank_id=0, currency=Currency.BRL)

# classe alterada por cont   a de erro quando usava a com @dataclass
# Erro: todos os bancos tinham a memsa instância do objeto
#       ao fim da simulação, os pritns possuiam os mesmos valores para todos os bancos
class CurrencyReserves:
    """
    Uma classe de dados para armazenar as reservas do banco, que serão usadas
    para câmbio e transferências internacionais.
    OBS: NÃO É PERMITIDO ALTERAR ESSA CLASSE!
    """
    def __init__(self):
        self.USD: Account = Account(_id=1, _bank_id=0, currency=Currency.USD)
        self.EUR: Account = Account(_id=2, _bank_id=0, currency=Currency.EUR)
        self.GBP: Account = Account(_id=3, _bank_id=0, currency=Currency.GBP)
        self.JPY: Account = Account(_id=4, _bank_id=0, currency=Currency.JPY)
        self.CHF: Account = Account(_id=5, _bank_id=0, currency=Currency.CHF)
        self.BRL: Account = Account(_id=6, _bank_id=0, currency=Currency.BRL)