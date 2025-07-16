#!/bin/bash

# fix_ssl_certificate.sh
# Usage: sudo ./fix_ssl_certificate.sh
#
# This script obtains and installs a Let's Encrypt SSL certificate for cryptomaltese.com
# and configures Docker/Nginx for SSL. It also sets up auto-renewal.
#
# Place this script in the docker/ directory. Run as root on your server.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (edit as needed)
DOMAIN="cryptomaltese.com"
EMAIL="admin@cryptomaltese.com"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CERTS_DIR="$APP_DIR/certs"
DOCKER_DIR="$APP_DIR/docker"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to check DNS resolution
check_dns_resolution() {
    print_status "Checking DNS resolution for $DOMAIN..."
    RESOLVED_IP=""
    if command -v dig >/dev/null 2>&1; then
        RESOLVED_IP=$(dig +short "$DOMAIN" | head -1)
    elif command -v host >/dev/null 2>&1; then
        RESOLVED_IP=$(host "$DOMAIN" | grep "has address" | awk '{print $NF}' | head -1)
    elif command -v nslookup >/dev/null 2>&1; then
        RESOLVED_IP=$(nslookup "$DOMAIN" | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    else
        print_error "No DNS lookup tools available"
        exit 1
    fi
    if [[ -n "$RESOLVED_IP" ]] && [[ "$RESOLVED_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        SERVER_IP=$(curl -4 -s ifconfig.me)
        if [[ "$RESOLVED_IP" == "$SERVER_IP" ]]; then
            print_status "DNS resolution successful: $DOMAIN -> $RESOLVED_IP"
            return 0
        else
            print_warning "DNS resolution mismatch:"
            print_warning "  Domain $DOMAIN resolves to: $RESOLVED_IP"
            print_warning "  Server IP is: $SERVER_IP"
            print_warning "  DNS may not be properly configured or propagated"
            return 1
        fi
    else
        print_error "DNS resolution failed for $DOMAIN"
        print_error "Please configure DNS records before proceeding"
        return 1
    fi
}

# Function to get docker compose command
get_docker_compose_cmd() {
    if command -v docker >/dev/null 2>&1; then
        if docker compose version >/dev/null 2>&1; then
            echo "docker compose"
        elif command -v docker-compose >/dev/null 2>&1; then
            echo "docker-compose"
        else
            print_error "Neither 'docker compose' nor 'docker-compose' is available"
            exit 1
        fi
    else
        print_error "Docker is not installed"
        exit 1
    fi
}

# Function to backup current certificates
backup_current_certificates() {
    print_status "Backing up current certificates..."
    if [[ -f "$CERTS_DIR/fullchain.pem" ]] || [[ -f "$CERTS_DIR/privkey.pem" ]]; then
        BACKUP_DIR="$CERTS_DIR/backup-$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        if [[ -f "$CERTS_DIR/fullchain.pem" ]]; then
            cp "$CERTS_DIR/fullchain.pem" "$BACKUP_DIR/"
        fi
        if [[ -f "$CERTS_DIR/privkey.pem" ]]; then
            cp "$CERTS_DIR/privkey.pem" "$BACKUP_DIR/"
        fi
        print_status "Certificates backed up to: $BACKUP_DIR"
    fi
}

# Function to obtain new SSL certificate
obtain_ssl_certificate() {
    print_status "Obtaining SSL certificate for $DOMAIN..."
    cd "$DOCKER_DIR"
    DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
    $DOCKER_COMPOSE_CMD down
    certbot certonly --standalone \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
    if [[ $? -eq 0 ]]; then
        print_status "SSL certificate obtained successfully"
        return 0
    else
        print_error "Failed to obtain SSL certificate"
        return 1
    fi
}

# Function to install new certificates
install_new_certificates() {
    print_status "Installing new SSL certificates..."
    mkdir -p "$CERTS_DIR"
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$CERTS_DIR/fullchain.pem"
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem "$CERTS_DIR/privkey.pem"
    chmod 644 "$CERTS_DIR/fullchain.pem"
    chmod 600 "$CERTS_DIR/privkey.pem"
    print_status "SSL certificates installed successfully in $CERTS_DIR"
}

# Function to restart services
restart_services() {
    print_status "Restarting services with new certificates..."
    cd "$DOCKER_DIR"
    DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
    $DOCKER_COMPOSE_CMD up -d
    print_status "Waiting for services to start..."
    sleep 10
    if $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
        print_status "Services restarted successfully"
    else
        print_error "Service restart failed"
        $DOCKER_COMPOSE_CMD logs
        exit 1
    fi
}

# Function to setup auto-renewal
setup_auto_renewal() {
    print_status "Setting up SSL certificate auto-renewal..."
    if command -v crontab >/dev/null 2>&1; then
        if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
            (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $CERTS_DIR/fullchain.pem && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $CERTS_DIR/privkey.pem && cd $DOCKER_DIR && $(get_docker_compose_cmd) restart nginx") | crontab -
            print_status "SSL certificate auto-renewal scheduled"
        else
            print_warning "SSL renewal cron job already exists"
        fi
    else
        print_warning "crontab not available, SSL renewal not scheduled"
        print_warning "You can manually renew certificates with: certbot renew"
    fi
}

# Function to test SSL certificate
test_ssl_certificate() {
    print_status "Testing SSL certificate..."
    if command -v openssl >/dev/null 2>&1; then
        echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -subject -dates
    fi
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/api/v1/health")
    if [[ "$HTTP_STATUS" == "200" ]]; then
        print_status "SSL certificate test successful"
        print_status "Health check returned: $HTTP_STATUS"
    else
        print_warning "SSL certificate test returned status: $HTTP_STATUS"
    fi
}

# Function to display final information
display_final_info() {
    echo ""
    echo -e "${GREEN}=== SSL Certificate Fix Complete ===${NC}"
    echo ""
    echo "SSL certificate has been updated for $DOMAIN"
    echo ""
    echo "Service Information:"
    echo "  - API URL: https://$DOMAIN"
    echo "  - Health Check: https://$DOMAIN/api/v1/health"
    echo "  - API Documentation: https://$DOMAIN/docs"
    echo ""
    echo "Certificate Information:"
    echo "  - Certificate: $CERTS_DIR/fullchain.pem"
    echo "  - Private Key: $CERTS_DIR/privkey.pem"
    echo "  - Auto-renewal: Configured"
    echo ""
    echo "Test the certificate:"
    echo "  curl -I https://$DOMAIN/api/v1/health"
    echo ""
}

# Main function
main() {
    check_root
    print_status "Starting SSL certificate fix for $DOMAIN..."
    if ! check_dns_resolution; then
        print_error "DNS resolution failed. Cannot proceed."
        exit 1
    fi
    backup_current_certificates
    if obtain_ssl_certificate; then
        install_new_certificates
        restart_services
        setup_auto_renewal
        test_ssl_certificate
        display_final_info
    else
        print_error "SSL certificate fix failed"
        exit 1
    fi
}

main "$@" 
