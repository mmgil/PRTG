import subprocess
import json
import math

# Função para obter os nós
def get_nodes():
    result = subprocess.run(['kubectl', 'get', '--raw', '/api/v1/nodes'], capture_output=True, text=True)
    nodes = json.loads(result.stdout)
    return [node['metadata']['name'] for node in nodes['items']]

# Função para obter os PVCs
def get_pvcs():
    pvcs = []
    for node in get_nodes():
        result = subprocess.run(['kubectl', 'get', '--raw', f'/api/v1/nodes/{node}/proxy/stats/summary'], capture_output=True, text=True)
        data = json.loads(result.stdout)
        for pod in data['pods']:
            if 'volume' in pod:
                for volume in pod['volume']:
                    if 'pvcRef' in volume:
                        pvc = {
                            'namespace': volume['pvcRef']['namespace'],
                            'name': volume['pvcRef']['name'],
                            'capacityBytes': volume['capacityBytes'],
                            'usedBytes': volume['usedBytes'],
                            'availableBytes': volume['availableBytes'],
                            'percentageUsed': math.ceil((volume['usedBytes'] / volume['capacityBytes']) * 100)
                        }
                        pvcs.append(pvc)
    # Remover duplicatas
    unique_pvcs = {f"{pvc['namespace']}-{pvc['name']}": pvc for pvc in pvcs}
    return list(unique_pvcs.values())

# Função principal
def main():
    pvcs = get_pvcs()
    channels = []
    for i, pvc in enumerate(pvcs, start=10):
        channel = {
            "id": i,
            "name": pvc['name'],
            "type": "lookup",
            "value": pvc['percentageUsed'],
            "lookup_name": "mmgil.k8s.pvc.used.space"
        }
        channels.append(channel)
    
    result = {
        "version": 2,
        "status": "ok",
        "message": f"Um total de {len(get_nodes())} nodes no cluster.",
        "channels": channels
    }
    
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
