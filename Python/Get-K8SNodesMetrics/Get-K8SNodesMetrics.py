#!/usr/bin/env python3
import json
from kubernetes import client, config

def get_node_metrics():
    # Carregar a configuração do Kubernetes
    config.load_kube_config()

    # Criar instâncias dos clientes da API do Kubernetes
    v1 = client.CoreV1Api()
    metrics = client.CustomObjectsApi()

    # Obter a lista de nodes
    nodes = v1.list_node().items

    node_data = []

    for node in nodes:
        node_name = node.metadata.name

        # Obter a capacidade total de CPU do nó
        cpu_capacity = node.status.capacity['cpu']
        cpu_capacity_millicores = int(cpu_capacity) * 1000  # Converter cores para milicores

        # Obter a capacidade total de memória do nó
        memory_capacity = node.status.capacity['memory']
        memory_capacity_bytes = int(memory_capacity[:-2]) * 1024  # Converter Ki para bytes

        # Obter métricas de uso de CPU e memória
        metrics_data = metrics.get_cluster_custom_object(
            "metrics.k8s.io", "v1beta1", "nodes", node_name
        )

        cpu_usage_nanocores = int(metrics_data['usage']['cpu'][:-1])  # Remover o 'n' e converter para inteiro
        cpu_usage_millicores = cpu_usage_nanocores / 1_000_000  # Converter nanocores para milicores

        # Calcular a porcentagem de uso de CPU
        cpu_usage_percentage = (cpu_usage_millicores / cpu_capacity_millicores) * 100
        cpu_usage_percentage = round(cpu_usage_percentage, 2)  # Formatar para dois números significativos

        memory_usage_bytes = int(metrics_data['usage']['memory'][:-2]) * 1024  # Converter Ki para bytes

        # Calcular a porcentagem de uso de memória
        memory_usage_percentage = (memory_usage_bytes / memory_capacity_bytes) * 100
        memory_usage_percentage = round(memory_usage_percentage, 2)  # Formatar para dois números significativos

        # Adicionar dados ao node_data
        node_data.append({
            "node_name": node_name,
            "cpu_usage_percentage": cpu_usage_percentage,
            "memory_usage_percentage": memory_usage_percentage,
        })

    return node_data

if __name__ == "__main__":
    try:
        node_data = get_node_metrics()
        # Formatar a saída para o PRTG
        result = {
            "version": 2,
            "status": "ok",
            "message": "Node metrics retrieved successfully",
            "channels": []
        }

        channel_id = 10  # Iniciar o ID do canal

        for node in node_data:
            result["channels"].append({
                "id": channel_id,
                "name": f"{node['node_name']} - (CPU Usage)",
                "type": "float",
                "kind": "percent_cpu",
                "value": node["cpu_usage_percentage"]
            })
            
            channel_id += 1  # Incrementar o ID do canal

            result["channels"].append({
                "id": channel_id,
                "name": f"{node['node_name']} - (Memory Usage)",
                "type": "float",
                "kind": "percent",
                "value": node["memory_usage_percentage"]
            })
            
            channel_id += 1  # Incrementar o ID do canal para o próximo node

        print(json.dumps(result))
    except Exception as e:
        # Em caso de erro, retornar uma mensagem de erro para o PRTG
        result = {
            "version": 2,
            "status": "error",
            "message": "Node metrics retrieved with error.",
            "channels": []
        }
        print(json.dumps(result))