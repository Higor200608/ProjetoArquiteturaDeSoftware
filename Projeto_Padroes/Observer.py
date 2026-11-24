from abc import ABC, abstractmethod


class ObservadorPedido(ABC):
    @abstractmethod
    def ao_mudar_status(self, codigo_pedido: str, novo_status: str) -> None:
        pass


class Pedido:
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        self.status = "PENDENTE"
        self._observadores: list[ObservadorPedido] = []

    def inscrever(self, observador: ObservadorPedido) -> None:
        self._observadores.append(observador)

    def remover(self, observador: ObservadorPedido) -> None:
        self._observadores.remove(observador)

    def atualizar_status(self, novo_status: str) -> None:
        self.status = novo_status
        self._notificar_observadores()

    def _notificar_observadores(self) -> None:
        for observador in self._observadores:
            observador.ao_mudar_status(self.codigo, self.status)


class EstoqueObserver(ObservadorPedido):
    def ao_mudar_status(self, codigo_pedido: str, novo_status: str) -> None:
        if novo_status == "PAGO":
            print(f"[ESTOQUE] Reservando itens do pedido {codigo_pedido}")


class AuditoriaObserver(ObservadorPedido):
    def ao_mudar_status(self, codigo_pedido: str, novo_status: str) -> None:
        print(f"[AUDITORIA] Pedido {codigo_pedido} mudou para status: {novo_status}")


def executar_demo() -> None:
    pedido = Pedido("PED-2048")
    pedido.inscrever(EstoqueObserver())
    pedido.inscrever(AuditoriaObserver())

    pedido.atualizar_status("PAGO")


if __name__ == "__main__":
    executar_demo()