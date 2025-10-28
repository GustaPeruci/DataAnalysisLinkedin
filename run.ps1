# Script para executar a aplicação de análise de perfis do LinkedIn

Write-Host "🚀 Iniciando aplicação de Análise de Perfis do LinkedIn..." -ForegroundColor Cyan
Write-Host ""

# Verificar se o Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Por favor, instale o Python primeiro." -ForegroundColor Red
    exit 1
}

# Verificar se as dependências estão instaladas
Write-Host ""
Write-Host "📦 Verificando dependências..." -ForegroundColor Yellow

$packages = @("streamlit", "pandas", "scikit-learn", "plotly")
$needsInstall = $false

foreach ($package in $packages) {
    $installed = pip show $package 2>$null
    if ($installed) {
        Write-Host "  ✓ $package instalado" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $package não instalado" -ForegroundColor Red
        $needsInstall = $true
    }
}

# Instalar dependências se necessário
if ($needsInstall) {
    Write-Host ""
    Write-Host "📥 Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependências instaladas com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao instalar dependências." -ForegroundColor Red
        exit 1
    }
}

# Executar a aplicação
Write-Host ""
Write-Host "🌐 Iniciando servidor Streamlit..." -ForegroundColor Cyan
Write-Host "   A aplicação abrirá no navegador em: http://localhost:8501" -ForegroundColor Gray
Write-Host ""
Write-Host "   Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

streamlit run app.py
