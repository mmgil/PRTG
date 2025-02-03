#!/usr/bin/env python3
"""This is a Python script for the Script v2 sensor."""
import json
import subprocess

def get_pvc_usage():
    # Executar o comando kubectl para obter os PVCs e suas métricas de uso
    result = subprocess.run(
        ["kubectl", "get", "pvc", "-A", "-o", "json"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Erro ao executar kubectl: {result.stderr}")

    pvcs = json.loads(result.stdout)
    pvc_usage = []

    for pvc in pvcs['items']:
        namespace = pvc['metadata']['namespace']
        name = pvc['metadata']['name']

        # Executar o comando kubectl describe para obter o pod que está usando o PVC
        result = subprocess.run(
            ["kubectl", "describe", "pvc", name, "-n", namespace],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Erro ao descrever PVC {name}: {result.stderr}")

        # Extrair o nome do pod da saída do comando describe
        used_by_line = next(
            (line for line in result.stdout.splitlines() if "Used By" in line),
            None
        )

        if not used_by_line:
            continue

        pod_name = used_by_line.split(":")[1].strip()

        # Obter o YAML do pod para encontrar o ponto de montagem
        result = subprocess.run(
            ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Erro ao obter YAML do pod {pod_name}: {result.stderr}")

        pod = json.loads(result.stdout)
        volume_name = None

        # Encontrar o nome do volume associado ao PVC
        for volume in pod['spec']['volumes']:
            if 'persistentVolumeClaim' in volume and volume['persistentVolumeClaim']['claimName'] == name:
                volume_name = volume['name']
                break

        if not volume_name:
            continue

        mount_point = None

        # Encontrar o ponto de montagem nos volumeMounts
        for container in pod['spec']['containers']:
            for volume_mount in container['volumeMounts']:
                if volume_mount['name'] == volume_name:
                    mount_point = volume_mount['mountPath']
                    break
            if mount_point:
                break

        if not mount_point:
            continue

        # Executar o comando df dentro do pod para obter a utilização do PVC
        result = subprocess.run(
            ["kubectl", "exec", pod_name, "-n", namespace, "--", "df", "-h", mount_point],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Erro ao executar df no pod {pod_name}: {result.stderr}")

        # Extrair a utilização do PVC da saída do comando df
        df_output = result.stdout.splitlines()
        if len(df_output) < 2:
            continue

        # Combinar linhas quebradas, se necessário
        combined_lines = []
        for i in range(1, len(df_output)):
            if df_output[i].strip() and not df_output[i].startswith("/"):
                combined_lines[-1] += " " + df_output[i].strip()
            else:
                combined_lines.append(df_output[i].strip())

        usage_line = combined_lines[0].split()
        if len(usage_line) < 5:
            raise Exception(f"Formato inesperado da saída do df: {usage_line}")

        used_percentage = usage_line[4].replace('%', '')

        pvc_usage.append({
            "namespace": namespace,
            "name": name,
            "usage_percentage": int(used_percentage)
        })

    return pvc_usage

if __name__ == "__main__":
    try:
        pvc_usage = get_pvc_usage()

        # Formatar a saída para o PRTG
        channels = []
        
        channel_id = 10  # Iniciar o ID do canal

        for pvc in pvc_usage:
            channels.append({
                "id": channel_id,
                "name": f"{pvc['namespace']}/{pvc['name']}",
                "type": "integer",
                "kind": "percent",
                "value": pvc['usage_percentage']
            })

            channel_id += 1  # Incrementar o ID do canal

        result = {
            "version": 2,
            "status": "ok",
            "message": "Uso de espaco dos PVCs no cluster.",
            "channels": channels
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