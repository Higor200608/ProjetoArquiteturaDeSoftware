from abc import ABC, abstractmethod


class Notificador(ABC):
    @abstractmethod
    def enviar_mensagem(self, destino: str, mensagem: str) -> None:
        pass


class ServicoSmsLegado:
    def disparar_sms_legado(self, telefone: str, conteudo: str) -> None:
        print(f"[SMS LEGADO -> {telefone}]: {conteudo}")


class SmsLegadoAdapter(Notificador):
    def __init__(self, servico_legado: ServicoSmsLegado) -> None:
        self._servico_legado = servico_legado

    def enviar_mensagem(self, destino: str, mensagem: str) -> None:
        self._servico_legado.disparar_sms_legado(destino, mensagem)


class ServicoPedido:
    def __init__(self, notificador: Notificador) -> None:
        self._notificador = notificador

    def confirmar_pedido(self, codigo_pedido: str, contato_cliente: str) -> None:
        print(f"Pedido {codigo_pedido} confirmado.")
        self._notificador.enviar_mensagem(
            contato_cliente,
            f"Seu pedido {codigo_pedido} foi confirmado!"
        )


def executar_demo() -> None:
    legado = ServicoSmsLegado()
    adaptador_sms = SmsLegadoAdapter(legado)

    servico_pedido = ServicoPedido(adaptador_sms)
    servico_pedido.confirmar_pedido("PED-1024", "+5545999990000")


if __name__ == "__main__":
    executar_demo()