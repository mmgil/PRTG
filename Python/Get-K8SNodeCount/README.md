# Get-K8SNodeCount

Esse script tem o objetivo de obter os dados essenciais de desempenho e disponibilidade dos nodes em um cluster de Kubernetes.

# Requisitos

- **Python**
- Certifique-se de que você tem o **kubectl** configurado e funcionando no servidor onde o script será executado.
- Instale a **biblioteca** kubernetes para Python: pip install kubernetes
- This sensor requires that you store the script file on the probe system. In a cluster, copy the file to every cluster node.
-- You must store the script file in the \Custom Sensors\scripts subfolder of the PRTG program directory of the probe system on Windows systems or in the /opt/paessler/share/scripts directory of the probe system on Linux systems.

# Como habilitar esse script no PRTG

No seu servidor de PRTG, adicione esse Script no seguinte caminho:

**Local Probe Windows**
```powershell
${env:ProgramFiles(x86)}+"\PRTG Network Monitor\Custom Sensors\EXEXML"
```

**multi-platform probe**
```bash
/opt/paessler/share/scripts/
```

# Histórico

**Author:** Moises de Matos Gil (moises@mmgil.com.br)

**Date:**   Março 31, 2025

**Janeiro, 2025 -** Criação do script.