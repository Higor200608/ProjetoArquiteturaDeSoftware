from abc import ABC, abstractmethod


class ProcessadorPagamento(ABC):
    @abstractmethod
    def pagar(self, valor: float) -> bool:
        pass


class PagamentoPix(ProcessadorPagamento):
    def pagar(self, valor: float) -> bool:
        print(f"Gerando QR Code PIX no valor de R$ {valor:.2f}")
        return True


class PagamentoCartaoCredito(ProcessadorPagamento):
    def pagar(self, valor: float) -> bool:
        print(f"Autorizando transação no cartão de crédito no valor de R$ {valor:.2f}")
        return True


class PagamentoCartaoDebito(ProcessadorPagamento):
    def pagar(self, valor: float) -> bool:
        print(f"Autorizando transação no cartão de débito no valor de R$ {valor:.2f}")
        return True


class PagamentoBoleto(ProcessadorPagamento):
    def pagar(self, valor: float) -> bool:
        print(f"Gerando boleto bancário no valor de R$ {valor:.2f}")
        return True


class CriadorPagamento(ABC):
    @abstractmethod
    def criar_processador(self) -> ProcessadorPagamento:
        pass


class CriadorPagamentoPix(CriadorPagamento):
    def criar_processador(self) -> ProcessadorPagamento:
        return PagamentoPix()


class CriadorPagamentoCartao(CriadorPagamento):
    def criar_processador(self) -> ProcessadorPagamento:
        return PagamentoCartaoCredito()


class CriadorPagamentoDebito(CriadorPagamento):
    def criar_processador(self) -> ProcessadorPagamento:
        return PagamentoCartaoDebito()


class CriadorPagamentoBoleto(CriadorPagamento):
    def criar_processador(self) -> ProcessadorPagamento:
        return PagamentoBoleto()


class CheckoutService:
    def __init__(self, criador: CriadorPagamento) -> None:
        self._criador = criador

    def finalizar_compra(self, valor: float) -> bool:
        processador = self._criador.criar_processador()
        aprovado = processador.pagar(valor)
        status = "APROVADO" if aprovado else "RECUSADO"
        print(f"Status do pagamento: {status}")
        return aprovado


def executar_demo() -> None:
    checkout_pix = CheckoutService(CriadorPagamentoPix())
    checkout_pix.finalizar_compra(150.00)

    checkout_cartao = CheckoutService(CriadorPagamentoCartao())
    checkout_cartao.finalizar_compra(320.50)


if __name__ == "__main__":
    executar_demo()