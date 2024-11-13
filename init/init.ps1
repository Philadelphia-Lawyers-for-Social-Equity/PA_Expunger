$HOOK_PATH = "./.git/hooks"
Write-Output "setting up git hooks"
if (-not (Test-Path $HOOK_PATH)) {
    New-Item -ItemType Directory -Path $HOOK_PATH
}
Copy-Item ./init/post-commit.sh -Destination "$HOOK_PATH/post-commit"
Copy-Item ./init/pre-commit.sh -Destination "$HOOK_PATH/pre-commit"
Set-ItemProperty "$HOOK_PATH/post-commit" -Name IsReadOnly -Value $false
Set-ItemProperty "$HOOK_PATH/pre-commit" -Name IsReadOnly -Value $false
attrib +x "$HOOK_PATH/pre-commit"
attrib +x "$HOOK_PATH/post-commit"
Write-Output "setup complete"
