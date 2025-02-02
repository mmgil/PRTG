# Get-LinuxDaemonStatus

# Como Instalar
    
No seu servidor de PRTG, adicione esse Script no seguinte caminho:

```powershell
${env:ProgramFiles(x86)}+"\PRTG Network Monitor\Custom Sensors\EXEXML"
```

Agora, ao adicionar o sensor em algum equipamento, escolha Sensores Customizados \ EXE/Script Avançado

Defina o Nome que você desejar, escolha o script no Combo Box logo abaixo e em parâmetros adicione:

```powershell
-NomeDoComputador %host -NomeDeUsuario "%linuxuser" -Senha "%linuxpassword" -Daemon "sshd", "apache2", "mysql"
```

# REQUISITOS

- Modulo Posh-SSH (Install-Module -Name Posh-SSH -Force)

# Histórico

**Author:** Moises de Matos Gil (moises@mmgil.com.br)

**Date:**   Fevereiro 01, 2025

**Fevereiro 01, 2025 Criado a Primeira Versão desse SCRIPT