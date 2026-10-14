# Deploy FREE-GPT: Neon (Postgres) + Render (Web Service)
# Rode na raiz do projeto: .\scripts\deploy-render.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "`n=== 1/4 Neon skills ===" -ForegroundColor Cyan
npx neon skills -y

Write-Host "`n=== 2/4 Neon: crie o banco (console) ===" -ForegroundColor Cyan
Write-Host @"
  1. Abra https://console.neon.tech e crie um projeto (ex.: lumina-chat)
  2. Copie a connection string (postgres://...)
  3. Guarde como DATABASE_URL no Render (passo 4)
"@

Write-Host "`n=== 3/4 GitHub: envie o codigo ===" -ForegroundColor Cyan
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Host "  GitHub CLI (gh) nao encontrado. Instale: winget install GitHub.cli"
  Write-Host "  Depois: gh auth login"
  Write-Host "  gh repo create lumina-chat --public --source=. --remote=origin --push"
} else {
  $remote = git remote get-url origin 2>$null
  if (-not $remote) {
    Write-Host "  Criando repo e fazendo push..."
    gh repo create lumina-chat --public --source=. --remote=origin --push
  } else {
    Write-Host "  Remote: $remote"
    git push -u origin main
  }
}

Write-Host "`n=== 4/4 Render ===" -ForegroundColor Cyan
Write-Host @"
  1. https://dashboard.render.com -> New -> Blueprint
  2. Conecte o repositorio GitHub deste projeto
  3. Em Environment, confira:
       OPENROUTER_API_KEY = (sua chave)
       DATABASE_URL       = (Neon)
       SECRET_KEY         = (gerada ou aleatoria longa)
  4. Deploy. URL final: https://lumina-chat.onrender.com (ou nome escolhido)
  5. Teste: /health e login na home
"@

Write-Host "`nPronto. Siga os passos acima se algum comando pedir login no navegador.`n" -ForegroundColor Green
