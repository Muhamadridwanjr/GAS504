#!/bin/bash
# Expand Let's Encrypt cert to cover all subdomains
# Run this AFTER all subdomain server blocks are serving port 80

set -e

DOMAIN="gasstrategyai.xyz"
SUBDOMAINS="app.${DOMAIN} api.${DOMAIN} admin.${DOMAIN} docs.${DOMAIN} blog.${DOMAIN} pricing.${DOMAIN}"

echo "=== Expanding SSL cert for all subdomains ==="
echo "Domains: ${DOMAIN} ${SUBDOMAINS}"

# Build -d flags
D_FLAGS="-d ${DOMAIN} -d www.${DOMAIN}"
for sub in ${SUBDOMAINS}; do
    D_FLAGS="${D_FLAGS} -d ${sub}"
done

# Run certbot expand via docker
docker run --rm \
    -v "/root/gasstrategyai/certbot/conf:/etc/letsencrypt" \
    -v "/root/gasstrategyai/certbot/www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@${DOMAIN} \
    --agree-tos \
    --no-eff-email \
    --expand \
    ${D_FLAGS}

echo "=== Done! Reload nginx ==="
docker exec nginx-proxy nginx -s reload
echo "=== Cert expanded and nginx reloaded ==="
