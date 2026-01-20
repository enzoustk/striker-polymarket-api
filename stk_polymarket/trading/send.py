from py_clob_client.client import ClobClient
from py_clob_client.exceptions import PolyApiException
from py_clob_client.clob_types import OrderArgs, OrderType

def send_order(
    client: ClobClient,
    price: float,
    size: float,
    side: str, 
    token_id: str,
    order_type: OrderType,
    expiration: int = 0
    ) -> dict | None:
    
    """
    Wrapper para Enviar de fato as ordens ao server da Polymarket
    """
    
    try:
        price = round(float(price), 2)
        size = round(float(size), 2)
        token_id = str(token_id)

        args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
            expiration=expiration
        )

        signed_order = client.create_order(args)
        resp = client.post_order(signed_order, order_type)
        
        if resp and isinstance(resp, dict) and resp.get("success"):
            return resp
        elif resp and hasattr(resp, "success") and resp.success:
            return resp
        else:
            # Rejeição Silenciosa
            return None

    except PolyApiException as e:
        # Extração segura da mensagem de erro
        raw_error = getattr(e, "message", "") or getattr(e, "error_message", "") or str(e)
        error_body = str(raw_error).lower()
        status_code = getattr(e, "status_code", 0)

        # Filtro de Saldo REAL (apenas se a mensagem falar explicitamente de saldo)
        balance_keywords = ["not enough balance", "insufficient funds", "allowance", "insufficient"]
        
        # MUDANÇA AQUI: Só acusa saldo se a mensagem contiver as palavras-chave.
        # Se for apenas 400 genérico, deixa passar para o print de baixo.
        if any(k in error_body for k in balance_keywords):
            print(f"⚠️ Saldo/Allowance insuficiente (Real).") 
            return None

        # Agora vamos ver o erro real!
        print(f"❌ Erro na API [{status_code}]: {raw_error}")
        return None