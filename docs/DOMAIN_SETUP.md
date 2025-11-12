# Domain Setup Guide for Error Reporting

This guide explains how to set up a custom domain for your error reporting backend using Cloudflare Tunnel, which provides free HTTPS access without port forwarding.

## Overview

The error reporting system consists of:
1. **Flask Backend** - Running on your Raspberry Pi (or any server)
2. **Cloudflare Tunnel** - Exposes your local server to the internet with HTTPS
3. **Custom Domain** - Optional but recommended for professional URLs

---

## Step 1: Set Up the Flask Backend

### On Your Raspberry Pi (or Server)

1. **Navigate to the backend folder:**
   ```bash
   cd "HW Helper copy 2/backend"
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the server:**
   ```bash
   source venv/bin/activate
   python error_server.py
   ```

   Or for production with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 error_server:app
   ```

4. **Verify it's running:**
   - Open http://localhost:5000 on your Pi
   - You should see the admin dashboard

---

## Step 2: Install Cloudflare Tunnel

Cloudflare Tunnel (formerly Argo Tunnel) provides free HTTPS access to your local server without opening ports.

### Install cloudflared

**On Raspberry Pi (Debian/Ubuntu):**
```bash
# Download the latest version
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb

# Install
sudo dpkg -i cloudflared-linux-arm64.deb
```

**On macOS:**
```bash
brew install cloudflared
```

**On Windows:**
Download from https://github.com/cloudflare/cloudflared/releases

### Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This will open a browser window. Log in to your Cloudflare account (create a free account if needed).

---

## Step 3: Create and Configure Tunnel

### Create a Tunnel

```bash
cloudflared tunnel create hw-helper-errors
```

This creates a tunnel and generates a credentials file. Note the **Tunnel ID** shown in the output.

### Create Configuration File

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID_HERE
credentials-file: /home/pi/.cloudflared/YOUR_TUNNEL_ID_HERE.json

ingress:
  - hostname: errors.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

Replace:
- `YOUR_TUNNEL_ID_HERE` with your actual tunnel ID
- `errors.yourdomain.com` with your desired subdomain
- `/home/pi/` with your actual home directory path

---

## Step 4: Get a Domain

You have several options for obtaining a domain:

### Option 1: Cloudflare Registrar (Paid, Recommended)

**Pros:** Best integration, no markup pricing, easy DNS management

1. Go to https://dash.cloudflare.com
2. Navigate to **Domain Registration**
3. Search for available domains (typically $8-15/year)
4. Purchase and it's automatically configured with Cloudflare DNS

### Option 2: Free Domains (Freenom, etc.)

**Pros:** Free
**Cons:** Limited availability, may have restrictions

1. Visit https://www.freenom.com
2. Search for available domains (.tk, .ml, .ga, .cf, .gq)
3. Register a free domain (up to 12 months)
4. Add domain to Cloudflare (see Option 3 below)

**Note:** Many free domain providers have been unreliable. Consider a paid domain for production use.

### Option 3: Use Existing Domain

If you already own a domain from GoDaddy, Namecheap, etc.:

1. Log in to Cloudflare Dashboard
2. Click **Add Site**
3. Enter your domain name
4. Follow instructions to change nameservers at your registrar to Cloudflare's nameservers
5. Wait for DNS propagation (can take up to 48 hours)

### Option 4: Use Cloudflare's Auto-Generated Subdomain (Free, Easiest)

Cloudflare provides a free `*.trycloudflare.com` subdomain automatically:

1. Skip the custom domain setup
2. Use the auto-generated URL provided by the tunnel
3. No DNS configuration needed

**Note:** This URL will change if you recreate the tunnel.

---

## Step 5: Configure DNS for Custom Domain

If using a custom domain (Options 1-3 above):

1. **Log in to Cloudflare Dashboard**
2. **Select your domain**
3. **Go to DNS → Records**
4. **Create a CNAME record:**
   - **Type:** CNAME
   - **Name:** errors (or your chosen subdomain)
   - **Target:** YOUR_TUNNEL_ID.cfargotunnel.com
   - **Proxy status:** Proxied (orange cloud)
   - **TTL:** Auto

Example:
```
Type: CNAME
Name: errors
Target: a1b2c3d4-e5f6-7890-abcd-ef1234567890.cfargotunnel.com
Proxy: On (orange cloud)
```

---

## Step 6: Route the Tunnel

Tell Cloudflare to route your domain to the tunnel:

```bash
cloudflared tunnel route dns hw-helper-errors errors.yourdomain.com
```

Replace `errors.yourdomain.com` with your actual domain/subdomain.

---

## Step 7: Run the Tunnel

### Test Run (foreground):

```bash
cloudflared tunnel run hw-helper-errors
```

Visit https://errors.yourdomain.com to verify it's working.

### Run as Service (background):

```bash
cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

To check status:
```bash
sudo systemctl status cloudflared
```

To view logs:
```bash
sudo journalctl -u cloudflared -f
```

---

## Step 8: Update Homework Helper Configuration

1. **Open config.json in the Homework Helper folder**

2. **Update the error_reporting section:**

```json
{
  "api_key": "your-openrouter-key",
  "selected_model": "google/gemini-2.0-flash-exp:free",
  "error_reporting": {
    "enabled": true,
    "endpoint": "https://errors.yourdomain.com/api/report"
  }
}
```

3. **Save the file**

4. **Restart Homework Helper**

---

## Testing the Setup

1. **Test the backend directly:**
   ```bash
   curl https://errors.yourdomain.com/health
   ```

   Should return:
   ```json
   {"status":"healthy","service":"error-reporting-api","timestamp":"..."}
   ```

2. **View the admin dashboard:**
   Open https://errors.yourdomain.com in a browser

3. **Trigger a test error in Homework Helper:**
   - Click "Report Error" button
   - Check the dashboard for the new report

---

## Troubleshooting

### Tunnel won't start
- Check `~/.cloudflared/config.yml` for syntax errors
- Verify tunnel ID matches credentials file
- Ensure Flask server is running on port 5000

### Domain not resolving
- Wait 5-10 minutes for DNS propagation
- Check DNS records in Cloudflare dashboard
- Verify CNAME points to correct tunnel ID

### Error reports not arriving
- Check Flask server logs: `journalctl -u cloudflared -f`
- Verify `config.json` has correct endpoint URL
- Test endpoint with curl: `curl -X POST https://errors.yourdomain.com/api/report -d '{"test":"data"}' -H "Content-Type: application/json"`

### 502 Bad Gateway
- Flask backend is not running
- Start backend: `cd backend && source venv/bin/activate && python error_server.py`

---

## Security Considerations

1. **Rate Limiting:** Consider adding rate limiting to prevent abuse
2. **Authentication:** For production, add API key authentication
3. **HTTPS:** Cloudflare automatically provides HTTPS (DO NOT disable)
4. **Database Backups:** Regularly backup `error_reports.db`

---

## Maintenance

### Update Flask Backend
```bash
cd backend
source venv/bin/activate
pip install --upgrade flask flask-cors
```

### View Error Reports
- Dashboard: https://errors.yourdomain.com
- Database: `sqlite3 backend/error_reports.db`
- Export: `sqlite3 backend/error_reports.db .dump > backup.sql`

### Restart Services
```bash
# Restart tunnel
sudo systemctl restart cloudflared

# Restart Flask (if running as systemd service)
sudo systemctl restart hw-helper-backend
```

---

## Alternative: Quick Setup with Cloudflare Auto-Generated URL

If you want the fastest setup without a custom domain:

1. **Skip Steps 4-6** (domain setup)

2. **Run tunnel in quick mode:**
   ```bash
   cloudflared tunnel --url http://localhost:5000
   ```

3. **Copy the generated URL** (e.g., `https://random-words-1234.trycloudflare.com`)

4. **Update config.json:**
   ```json
   "endpoint": "https://random-words-1234.trycloudflare.com/api/report"
   ```

**Note:** This URL changes each time you restart the tunnel. Good for testing, not recommended for production.

---

## Cost Summary

- **Cloudflare Tunnel:** FREE
- **Cloudflare DNS:** FREE
- **HTTPS Certificate:** FREE (included)
- **Domain Registration:**
  - Cloudflare Registrar: $8-15/year (recommended)
  - Traditional registrars: $10-20/year
  - Free domains (.tk, etc.): FREE (limited availability)
  - Auto-generated subdomain: FREE

**Total Cost:** $0-15/year depending on domain choice

---

## Support

For issues with:
- **Homework Helper:** Report on GitHub issues
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **Flask Backend:** Check logs in `backend/` folder
