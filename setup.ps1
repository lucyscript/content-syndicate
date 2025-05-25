# ContentSyndicate Docker Setup Script
# Run this script to set up the development environment

Write-Host "Setting up ContentSyndicate development environment..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created. Please edit it with your actual API keys and secrets." -ForegroundColor Green
    Write-Host "📝 Open .env file and configure your environment variables before continuing." -ForegroundColor Yellow
    
    # Ask user if they want to continue
    $continue = Read-Host "Have you configured your .env file? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Please configure your .env file and run this script again." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ .env file already exists." -ForegroundColor Green
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running." -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build and start services
Write-Host "Building and starting Docker services..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "   API: http://localhost:8000" -ForegroundColor White
    Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White
    Write-Host "   Database: localhost:5432" -ForegroundColor White
    Write-Host "   Redis: localhost:6379" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Monitor services:" -ForegroundColor Cyan
    Write-Host "   docker-compose logs -f" -ForegroundColor White
    Write-Host "   docker-compose ps" -ForegroundColor White
    Write-Host ""
    Write-Host "🛑 Stop services:" -ForegroundColor Cyan
    Write-Host "   docker-compose down" -ForegroundColor White
} else {
    Write-Host "❌ Failed to start services. Check the logs above." -ForegroundColor Red
    exit 1
}
