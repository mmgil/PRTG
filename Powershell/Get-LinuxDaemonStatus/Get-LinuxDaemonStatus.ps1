<#
.SYNOPSIS
    .SCRIPT PARA OBTER UM SERVIÇO ESPECÍFICO NO SYSTEMD DO LINUX.
.DESCRIPTION
    .SCRIPT PARA OBTER UM SERVIÇO ESPECÍFICO NO SYSTEMD DO LINUX.
    .REQUISITOS: Instalar o modulo de SSHSessions no PRTG Network Monitor Install-Module -Name Posh-SSH
.PARAMETER NomeDoComputador
    .Digite o nome FQDN do computador (certifique-se que esse nome resolva a partir do host que executa o script) ou então o endereço IP (tenha certeza queo host que executa o script tem acesso à esse computador destino)
.PARAMETER NomeDeUsuario
    .Nome de Usuario que tem acesso administrativo no computador destino
.PARAMETER Senha
    .A Senha do usuário acima. Para manter o sigilo dessas informações usamos as variaveis do PRTG Network Monitor conforme exemplos a seguir
.EXAMPLE
    C:\PS>& '.\Get-LinuxDaemonStatus.ps1' -NomeDoComputador %host -NomeDeUsuario "%linuxuser" -Senha "%linuxpassword" -Daemon "sshd", "apache2", "mysql"
    
.NOTES
    Author: Moises de Matos Gil (moises@mmgil.com.br)
    Date:   Fevereiro 01, 2025

    Fevereiro 01, 2025 - Criado a Primeira Versão desse SCRIPT
#>

param(
    # PARAMETROS
    [Parameter( Mandatory = $True, ValueFromPipeline = $True, position = 0, HelpMessage = "Digite o nome do Computador" )]
    [string]$NomeDoComputador,
    [Parameter( Mandatory = $True, ValueFromPipeline = $True, position = 1, HelpMessage = "Digite o nome do Daemon a ser pesquisado" )]
    [string[]]$Daemon,
    [Parameter( Mandatory = $True, ValueFromPipeline = $True, position = 2, HelpMessage = "Digite o Nome de Usuario" )]
    [string]$NomeDeUsuario,
    [Parameter( Mandatory = $True, ValueFromPipeline = $True, position = 3, HelpMessage = "Digite a Senha" )]
    [string]$Senha
)

# VALIDANDO REQUISITOS
$SSHSessionsModule = Get-Module -Name Posh-SSH -ListAvailable

if ([string]::IsNullOrEmpty($SSHSessionsModule)) {
    Install-Module -Name Posh-SSH -Force
} else {
    Import-Module -Name Posh-SSH -Force
}

#######################################
function New-GenerateCredentials() {
    # Generate Credentials Object first
    $SecPasswd = ConvertTo-SecureString $Senha -AsPlainText -Force
    $Credentials = New-Object System.Management.Automation.PSCredential ($NomeDeUsuario, $SecPasswd)
    return $Credentials
}

$Credentials = (New-GenerateCredentials);

# ABRINDO UMA SESSÃO SSH
$SSHSession = New-SSHSession -ComputerName $NomeDoComputador -Credential $Credentials -AcceptKey

# OBTER INFORMAÇÕES ATRAVES DE SSH REMOTAMENTE
## DAEMON STATUS
$DaemonStatus = @()

$Daemon | ForEach-Object {
    $SSHCommand = Invoke-SSHCommand -SessionId $SSHSession.SessionId -Command "systemctl status $_"

    $tempDaemonStatus = New-Object -Type PSObject
    
    $tempDaemonStatus = [PSCustomObject] @{
        Daemon  = $_
        Status  = (([string]($SSHCommand.Output | Select-String -Pattern "Active")).TrimStart() -split " ")[1]
        Memory  = (([string]($SSHCommand.Output | Select-String -Pattern "Memory")).TrimStart() -split " ")[1] -replace "[a-zA-Z]"
        Unidade = (([string]($SSHCommand.Output | Select-String -Pattern "Memory")).TrimStart() -split " ")[1][-1]
    }
    
    $DaemonStatus += $tempDaemonStatus

    $SSHCommand = $null ## LIMPANDO A VARIAVEL PARA O PROXIMO CURSOR
    $tempDaemonStatus = $null ## LIMPANDO A VARIAVEL PARA O PROXIMO CURSOR
}

# REMOVENDO A SESSÃO SSH
Remove-SSHSession -SessionId $SSHSession.SessionId | Out-Null

#### TRATANDO RESULTADOS E GERANDO TEMPLATE DO XML PARA O PRTG INTERPRETAR
@"
<prtg>
    <text>Custom Sensor Linux Daemon Status (moises@mmgil.com.br)</text>
"@

$DaemonStatus | ForEach-Object {
    $Channel = $_.Daemon
    $Status = if($_.Status -eq "active") { 1 } else { 2 }

@"
    <result>
        <channel>$Channel</channel>
        <value>$Status</value>
        <valuelookup>prtg.standardlookups.activeinactive.stateactiveok</valuelookup>
    </result>
"@

    $Channel = $null ## LIMPANDO A VARIAVEL PARA O PROXIMO CURSOR
    $Status = $null ## LIMPANDO A VARIAVEL PARA O PROXIMO CURSOR

}

@"
</prtg>
"@