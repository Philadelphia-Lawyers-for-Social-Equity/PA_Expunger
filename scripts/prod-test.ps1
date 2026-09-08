#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Convenience wrapper script for running docker-compose commands against the
    production-like test environment (compose.prod-test.yaml).

.DESCRIPTION
    All arguments passed to this script will be forwarded to the
    'docker compose' command.

.EXAMPLE
    # Starts the services in detached mode after building
    .\scripts\prod-test.ps1 up --build -d

.EXAMPLE
    # Stops the services and removes volumes
    .\scripts\prod-test.ps1 down -v
#>

[CmdletBinding()]
param(
    # This attribute tells PowerShell to collect all arguments that haven't been
    # matched to a declared parameter and store them in the $PassthruArgs array.
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$PassthruArgs
)

docker compose -f compose.prod-test.yaml $PassthruArgs
