param(
    [Parameter(Mandatory = $true)]
    [string]$RepoPath,

    [string]$Track = "B",

    [int]$IntervalSeconds = 3600
)

if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
    throw "RepoPath does not exist or is not a directory: $RepoPath"
}

$InitialPrompt = @"
Implement the workflow in @workflow.md and do the research based on the problems in @problems.md and other files in the repository, carry out the implementation, test the solution with screenshots, and update the workflow.md and other files with the progress.
"@

$ResumePrompt = @"
Continue the implementation and research based on the problems in @problems.md and other files in the repository, carry out the implementation, test the solution with screenshots, and update the workflow.md and other files with the progress.
"@

Write-Host "Starting AgentPreflight build monitor — Track $Track — interval ${IntervalSeconds}s"
Write-Host "Repo: $RepoPath"

codex --yolo exec --cd $RepoPath --skip-git-repo-check $InitialPrompt

for ($i = 1; $i -le 5; $i++) {
    Start-Sleep -Seconds $IntervalSeconds
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Resuming Track $Track..."
    codex --yolo exec resume --last $ResumePrompt
}
