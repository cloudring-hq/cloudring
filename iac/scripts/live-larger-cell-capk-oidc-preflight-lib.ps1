function New-Check {
    param([string]$Name, [string]$Status, [string]$Message, $Data = $null)
    return [ordered]@{
        name = $Name
        status = $Status
        message = $Message
        data = $Data
    }
}

function Invoke-ProcessWithTimeout {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds
    )
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $quotedArgs = @($Arguments | ForEach-Object {
        if ($_ -match '[\s"]') {
            '"' + ($_.Replace('\', '\\').Replace('"', '\"')) + '"'
        } else {
            $_
        }
    })
    $psi.Arguments = ($quotedArgs -join " ")
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $outTask = $process.StandardOutput.ReadToEndAsync()
    $errTask = $process.StandardError.ReadToEndAsync()
    $exited = $process.WaitForExit($TimeoutSeconds * 1000)
    if (-not $exited) {
        try { $process.Kill($true) } catch { try { $process.Kill() } catch {} }
        return [ordered]@{
            exitCode = $null
            timedOut = $true
            stdout = ""
            stderr = "Process timed out after ${TimeoutSeconds}s"
            command = "$FilePath $($Arguments -join ' ')"
        }
    }
    $process.WaitForExit()
    return [ordered]@{
        exitCode = $process.ExitCode
        timedOut = $false
        stdout = $outTask.Result
        stderr = $errTask.Result
        command = "$FilePath $($Arguments -join ' ')"
    }
}

function Invoke-SshKubectlJson {
    param([Parameter(Mandatory = $true)][string]$KubectlArgs)
    $remote = "timeout ${TimeoutSeconds}s sudo -n k3s kubectl $KubectlArgs -o json"
    $args = @(
        "-i", $SshKey,
        "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=$KnownHosts",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=$TimeoutSeconds",
        "$SshUser@$SshHost",
        $remote
    )
    $result = Invoke-ProcessWithTimeout "ssh.exe" $args ($TimeoutSeconds + 5)
    if ($result.exitCode -ne 0 -or $result.timedOut) {
        return [ordered]@{ ok = $false; result = $result; json = $null }
    }
    try {
        return [ordered]@{ ok = $true; result = $result; json = ($result.stdout | ConvertFrom-Json) }
    } catch {
        return [ordered]@{ ok = $false; result = $result; json = $null; parseError = $_.Exception.Message }
    }
}

function Read-EnvSetting {
    param($Container, [string]$Name)
    foreach ($env in @($Container.env)) {
        if ($env.name -eq $Name) {
            $valueFrom = $null
            if ($env.valueFrom) {
                $parts = New-Object System.Collections.Generic.List[string]
                if ($env.valueFrom.secretKeyRef) {
                    $parts.Add(("secret:{0}/{1}" -f $env.valueFrom.secretKeyRef.name, $env.valueFrom.secretKeyRef.key))
                }
                if ($env.valueFrom.configMapKeyRef) {
                    $parts.Add(("configMap:{0}/{1}" -f $env.valueFrom.configMapKeyRef.name, $env.valueFrom.configMapKeyRef.key))
                }
                if ($env.valueFrom.fieldRef) {
                    $parts.Add(("field:{0}" -f $env.valueFrom.fieldRef.fieldPath))
                }
                if ($env.valueFrom.resourceFieldRef) {
                    $parts.Add(("resource:{0}" -f $env.valueFrom.resourceFieldRef.resource))
                }
                $valueFrom = ($parts.ToArray() -join ",")
            }
            return [ordered]@{
                present = $true
                value = $env.value
                valueFrom = $valueFrom
                secretName = $(if ($env.valueFrom.secretKeyRef) { $env.valueFrom.secretKeyRef.name } else { $null })
                secretKey = $(if ($env.valueFrom.secretKeyRef) { $env.valueFrom.secretKeyRef.key } else { $null })
                configMapName = $(if ($env.valueFrom.configMapKeyRef) { $env.valueFrom.configMapKeyRef.name } else { $null })
                configMapKey = $(if ($env.valueFrom.configMapKeyRef) { $env.valueFrom.configMapKeyRef.key } else { $null })
            }
        }
    }
    return [ordered]@{
        present = $false
        value = $null
        valueFrom = $null
        secretName = $null
        secretKey = $null
        configMapName = $null
        configMapKey = $null
    }
}

function Resolve-EnvSetting {
    param([Parameter(Mandatory = $true)]$Setting, [Parameter(Mandatory = $true)][string]$Namespace)
    $resolved = $Setting.value
    $resolvedFrom = "literal"
    $resolveError = $null

    if ($Setting.secretName -and $Setting.secretKey) {
        $secret = Invoke-SshKubectlJson ("get secret -n {0} {1}" -f $Namespace, $Setting.secretName)
        if ($secret.ok -and $secret.json.data -and $secret.json.data.PSObject.Properties.Name -contains $Setting.secretKey) {
            try {
                $bytes = [System.Convert]::FromBase64String($secret.json.data.($Setting.secretKey))
                $resolved = [System.Text.Encoding]::UTF8.GetString($bytes)
                $resolvedFrom = $Setting.valueFrom
            } catch {
                $resolved = $null
                $resolveError = $_.Exception.Message
            }
        } else {
            $resolved = $null
            $resolvedFrom = $Setting.valueFrom
            $resolveError = "secret key could not be resolved"
        }
    } elseif ($Setting.configMapName -and $Setting.configMapKey) {
        $configMap = Invoke-SshKubectlJson ("get configmap -n {0} {1}" -f $Namespace, $Setting.configMapName)
        if ($configMap.ok -and $configMap.json.data -and $configMap.json.data.PSObject.Properties.Name -contains $Setting.configMapKey) {
            $resolved = $configMap.json.data.($Setting.configMapKey)
            $resolvedFrom = $Setting.valueFrom
        } else {
            $resolved = $null
            $resolvedFrom = $Setting.valueFrom
            $resolveError = "configmap key could not be resolved"
        }
    } elseif ($Setting.valueFrom) {
        $resolved = $null
        $resolvedFrom = $Setting.valueFrom
        $resolveError = "unsupported valueFrom source"
    }

    return [ordered]@{
        present = $Setting.present
        value = $Setting.value
        valueFrom = $Setting.valueFrom
        resolvedValue = $resolved
        resolvedFrom = $resolvedFrom
        resolveError = $resolveError
    }
}

function Convert-ToIntOrZero {
    param($Value)
    if ($null -eq $Value -or $Value -eq "") { return 0 }
    return [int]$Value
}
