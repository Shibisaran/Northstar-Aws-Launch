# Northstar Store

A responsive Flask e-commerce website with a seeded catalog, shopping bag, checkout form, and order storage.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app run --debug
```

Visit `http://127.0.0.1:5000`. The SQLite database and sample products are created automatically.

## Publish to GitHub

```bash
git init
git add .
git commit -m "Initial ecommerce store"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## Deploy on Ubuntu EC2

1. In the EC2 security group, allow inbound ports **22**, **80**, and **443**. Clone the repository into `/home/ubuntu/northstar-store`.
2. Create the virtual environment, install requirements, and create a production `.env` with a strong `SECRET_KEY` and `PORT=8000`.
3. Copy `deploy/northstar.service` to `/etc/systemd/system/`, update `WorkingDirectory` if needed, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now northstar
sudo systemctl status northstar
```

4. Install Nginx (`sudo apt update && sudo apt install nginx`), copy `deploy/nginx.conf` to `/etc/nginx/sites-available/northstar`, replace both `example.com` values with your domain, enable it, test and reload:

```bash
sudo ln -s /etc/nginx/sites-available/northstar /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Cloudflare DNS and HTTPS

Create two **A** records in Cloudflare: `@` and `www`, both pointing to your EC2 public IPv4 address. Enable the orange-cloud proxy once the site responds over HTTP. Set SSL/TLS mode to **Full (strict)** after installing an origin certificate or Certbot certificate on EC2. Do not use Flexible SSL with this Nginx setup.

This sample checkout records orders but does not charge cards. Add Stripe or another payment provider before accepting real payments.
