"""Ponte entre o HTML e as classes dos padrões. Só biblioteca padrão: sem pip install."""
import io
import json
import webbrowser
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import Adapter
import Factor_Criacional as Fabrica
import Observer

PASTA = Path(__file__).parent
PORTA = 8000

# ---- estado do Observer (fica na memória enquanto o servidor roda) ----
OBSERVADORES = {"estoque": Observer.EstoqueObserver(), "auditoria": Observer.AuditoriaObserver()}
ESTADO = {"pedido": None, "ativos": set()}


def capturar(funcao):
    """Executa a função e devolve (resultado, linhas que iriam para o terminal)."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        resultado = funcao()
    texto = buffer.getvalue()
    print(texto, end="")  # continua aparecendo no terminal também
    return resultado, [l for l in texto.splitlines() if l.strip()]


def estado_pedido():
    p = ESTADO["pedido"]
    return {"codigo": p.codigo if p else None, "status": p.status if p else None,
            "observadores": {n: n in ESTADO["ativos"] for n in OBSERVADORES}}


# ---- rotas ----
def pagamento(d):
    valor = float(d["valor"])
    if valor <= 0:
        raise ValueError("O valor precisa ser maior que zero.")
    criadores = {
        "pix": Fabrica.CriadorPagamentoPix,
        "cartao": Fabrica.CriadorPagamentoCartao,
        "debito": Fabrica.CriadorPagamentoDebito,
        "boleto": Fabrica.CriadorPagamentoBoleto,
    }
    criador = criadores.get(d["metodo"])
    if not criador:
        raise ValueError("Selecione uma forma de pagamento válida.")
    checkout = Fabrica.CheckoutService(criador())
    aprovado, log = capturar(lambda: checkout.finalizar_compra(valor))
    return {"aprovado": aprovado, "log": log}


def notificar(d):
    if not d["telefone"].strip():
        raise ValueError("Informe o telefone do cliente.")
    servico = Adapter.ServicoPedido(Adapter.SmsLegadoAdapter(Adapter.ServicoSmsLegado()))
    _, log = capturar(lambda: servico.confirmar_pedido(d["codigo"], d["telefone"]))
    return {"log": log}


def criar_pedido(d):
    if not d["codigo"].strip():
        raise ValueError("Informe o código do pedido.")
    pedido = Observer.Pedido(d["codigo"].strip())
    ESTADO["pedido"], ESTADO["ativos"] = pedido, set()
    for nome, obs in OBSERVADORES.items():
        pedido.inscrever(obs)
        ESTADO["ativos"].add(nome)
    return {"pedido": estado_pedido(), "log": []}


def mudar_status(d):
    pedido = ESTADO["pedido"]
    if not pedido:
        raise ValueError("Crie um pedido primeiro.")
    _, log = capturar(lambda: pedido.atualizar_status(d["status"]))
    return {"pedido": estado_pedido(), "log": log}


def alternar_observador(d):
    pedido, nome = ESTADO["pedido"], d["nome"]
    if not pedido:
        raise ValueError("Crie um pedido primeiro.")
    if d["ativo"] and nome not in ESTADO["ativos"]:
        pedido.inscrever(OBSERVADORES[nome]); ESTADO["ativos"].add(nome)
    elif not d["ativo"] and nome in ESTADO["ativos"]:
        pedido.remover(OBSERVADORES[nome]); ESTADO["ativos"].discard(nome)
    return {"pedido": estado_pedido(), "log": []}


ROTAS_POST = {"/api/pagamento": pagamento, "/api/notificar": notificar,
              "/api/pedido/criar": criar_pedido, "/api/pedido/status": mudar_status,
              "/api/pedido/observador": alternar_observador}
ARQUIVOS = {"/": ("index.html", "text/html"), "/style.css": ("style.css", "text/css")}


class Handler(BaseHTTPRequestHandler):
    def _enviar(self, codigo, corpo, tipo):
        self.send_response(codigo)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path == "/api/pedido":
            return self._enviar(200, json.dumps(estado_pedido()).encode(), "application/json")
        if self.path in ARQUIVOS:
            nome, tipo = ARQUIVOS[self.path]
            return self._enviar(200, (PASTA / nome).read_bytes(), tipo)
        self._enviar(404, b"Nao encontrado", "text/plain")

    def do_POST(self):
        rota = ROTAS_POST.get(self.path)
        if not rota:
            return self._enviar(404, b"{}", "application/json")
        try:
            dados = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            resposta, codigo = rota(dados), 200
        except (ValueError, KeyError) as erro:
            resposta, codigo = {"erro": str(erro)}, 400
        self._enviar(codigo, json.dumps(resposta).encode(), "application/json")

    def log_message(self, *args):  # silencia o log HTTP para não poluir o terminal
        pass


if __name__ == "__main__":
    # HTTPServer (uma requisição por vez) evita conflito na captura do stdout
    servidor = HTTPServer(("127.0.0.1", PORTA), Handler)
    print(f"Interface em http://127.0.0.1:{PORTA}  (Ctrl+C para parar)")
    webbrowser.open(f"http://127.0.0.1:{PORTA}")
    servidor.serve_forever()
