#!/usr/bin/env python3
"""This is a Python script for the Script v2 sensor."""
import json
from kubernetes import client, config

def get_node_count():
    # Carregar a configuração do Kubernetes
    config.load_kube_config()

    # Criar uma instância do cliente da API do Kubernetes
    v1 = client.CoreV1Api()

    # Obter a lista de nodes
    nodes = v1.list_node()

    # Retornar a contagem de nodes
    return len(nodes.items)

if __name__ == "__main__":
    WARNING_LIMIT = 2
    ERROR_LIMIT = 3

    try:
        node_count = get_node_count()

        # Verifica os limites e os status.
        status = "ok"
        # if node_count == WARNING_LIMIT:
        #     status = "warning"
        # elif node_count >= ERROR_LIMIT:
        #     status = "error"

        # Formatar a saída para o PRTG
        result = {
            "version": 2,
            "status": status,
            "message": f"Um total de {node_count} nodes no cluster.",
            "channels": [
                    {
                        "id": 10,
                        "name": "Node Count",
                        "type": "lookup",
                        "value": node_count,
                        "lookup_name": "mmgil.k8s.nodecount.status",
                    }
                ]
            }
        print(json.dumps(result))
    except Exception as e:
        # Em caso de erro, retornar uma mensagem de erro para o PRTG
        result = {
            "version": 2,
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(result))