# PowerShell Makefile equivalent for Bhanjyang Cooperative
# Usage: .\make.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Bhanjyang Cooperative Django Project" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Development:" -ForegroundColor Green
    Write-Host "    dev              Start development server"
    Write-Host "    shell            Start Django shell"
    Write-Host "    superuser        Create superuser"
    Write-Host ""
    Write-Host "  Database:" -ForegroundColor Green
    Write-Host "    migrate          Run database migrations"
    Write-Host "    makemigrations   Create new migrations"
    Write-Host ""
    Write-Host "  Static Files:" -ForegroundColor Green
    Write-Host "    build-css        Build CSS assets"
    Write-Host "    collectstatic    Collect static files"
    Write-Host ""
    Write-Host "  Testing:" -ForegroundColor Green
    Write-Host "    test             Run tests"
    Write-Host ""
    Write-Host "  Setup:" -ForegroundColor Green
    Write-Host "    install          Install production dependencies"
    Write-Host "    dev-install      Install development dependencies"
    Write-Host ""
    Write-Host "  Other:" -ForegroundColor Green
    Write-Host "    help             Show this help message"
    Write-Host ""
}

function Start-Dev {
    Write-Host "Starting development server..." -ForegroundColor Green
    python manage.py runserver
}

function Start-Shell {
    Write-Host "Starting Django shell..." -ForegroundColor Green
    python manage.py shell
}

function New-Superuser {
    Write-Host "Creating superuser..." -ForegroundColor Green
    python manage.py createsuperuser
}

function Invoke-Migrate {
    Write-Host "Running migrations..." -ForegroundColor Green
    python manage.py migrate
}

function New-Migrations {
    Write-Host "Creating migrations..." -ForegroundColor Green
    python manage.py makemigrations
}

function Build-CSS {
    Write-Host "Building CSS assets..." -ForegroundColor Green
    npm run build
}

function Collect-Static {
    Write-Host "Collecting static files..." -ForegroundColor Green
    python manage.py collectstatic --noinput
}

function Invoke-Test {
    Write-Host "Running tests..." -ForegroundColor Green
    python manage.py test
}

function Install-Dependencies {
    Write-Host "Installing production dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Write-Host "Installing development dependencies..." -ForegroundColor Green
    pip install -r requirements-dev.txt
    npm install
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        pre-commit install
    }
}

# Main command router
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "dev" { Start-Dev }
    "shell" { Start-Shell }
    "superuser" { New-Superuser }
    "migrate" { Invoke-Migrate }
    "makemigrations" { New-Migrations }
    "build-css" { Build-CSS }
    "collectstatic" { Collect-Static }
    "test" { Invoke-Test }
    "install" { Install-Dependencies }
    "dev-install" { Install-DevDependencies }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}

