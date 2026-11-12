param (
    [string]$TargetUrl = "http://localhost:5000",
    [int]$Concurrency = 20,
    [int]$DurationSeconds = 120
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Starting Load Generator for HPA Testing (PowerShell)" -ForegroundColor Cyan
Write-Host "Target URL:       $TargetUrl" -ForegroundColor Yellow
Write-Host "Concurrency:      $Concurrency parallel runspaces" -ForegroundColor Yellow
Write-Host "Duration:         $DurationSeconds seconds" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

$ScriptBlock = {
    param($url, $endTime)
    $client = New-Object System.Net.Http.HttpClient
    while ([DateTime]::UtcNow -lt $endTime) {
        try {
            $response = $client.GetAsync($url).GetAwaiter().GetResult()
            $null = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        } catch {
        }
    }
    $client.Dispose()
}

$EndTime = [DateTime]::UtcNow.AddSeconds($DurationSeconds)
$Runspaces = @()

for ($i = 0; $i -lt $Concurrency; $i++) {
    $PowerShell = [PowerShell]::Create()
    $null = $PowerShell.AddScript($ScriptBlock).AddArgument($TargetUrl).AddArgument($EndTime)
    $AsyncResult = $PowerShell.BeginInvoke()
    $Runspaces += [PSCustomObject]@{
        PowerShell = $PowerShell
        AsyncResult = $AsyncResult
    }
}

Write-Host "Load generation running... please wait." -ForegroundColor Yellow
foreach ($rs in $Runspaces) {
    $null = $rs.PowerShell.EndInvoke($rs.AsyncResult)
    $rs.PowerShell.Dispose()
}

Write-Host "Load test finished!" -ForegroundColor Green
