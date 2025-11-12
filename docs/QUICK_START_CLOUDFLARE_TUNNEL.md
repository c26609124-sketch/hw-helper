# Quick Start: Cloudflare Tunnel with Custom Domain

This is a simplified, step-by-step guide to get your Raspberry Pi accessible via a custom domain using Cloudflare Tunnel.

---

## What You'll Get

- **Your Flask API accessible at**: `https://errors.yourdomain.com`
- **Free HTTPS certificate** (automatic)
- **No port forwarding needed**
- **Works behind any firewall/NAT**

---

## Prerequisites

- Raspberry Pi with internet connection
- SSH access to your Pi
- A domain name (see options below)

---

## Part 1: Get a Domain (Choose One Option)

### Option A: Free Auto-Generated Subdomain (Fastest, No Domain Needed)

**Best for**: Testing, quick setup

Skip to Part 2 and use the auto-generated URL that Cloudflare provides.

**Pros**: Instant, no cost, no configuration
**Cons**: URL changes if you recreate the tunnel

---

### Option B: Buy a Domain from Cloudflare (Recommended)

**Best for**: Production use, professional URLs

**Cost**: $8-15/year

1. **Go to Cloudflare Dashboard**: https://dash.cloudflare.com
2. **Click "Domain Registration"** in left sidebar
3. **Search for your desired domain**: e.g., `myhelper.com`
4. **Purchase the domain**
5. **Done!** Domain is automatically configured with Cloudflare DNS

**Example domains available:**
- `.com` - $9.77/year
- `.net` - $11.16/year
- `.org` - $10.18/year
- `.app` - $14.88/year

---

### Option C: Use Existing Domain (Transfer DNS to Cloudflare)

**Best for**: If you already own a domain from GoDaddy, Namecheap, etc.

1. **Go to Cloudflare Dashboard**: https://dash.cloudflare.com
2. **Click "Add a Site"**
3. **Enter your domain name**: e.g., `yourdomain.com`
4. **Select Free plan**
5. **Cloudflare will scan your DNS records**
6. **Click Continue**
7. **Cloudflare shows you 2 nameservers** (e.g., `kate.ns.cloudflare.com` and `tim.ns.cloudflare.com`)
8. **Log in to your domain registrar** (GoDaddy, Namecheap, etc.)
9. **Find "Nameservers" or "DNS Settings"**
10. **Replace existing nameservers** with Cloudflare's nameservers
11. **Wait 5-60 minutes** for DNS propagation
12. **Return to Cloudflare** - it will confirm when active

---

## Part 2: Install Cloudflare Tunnel on Raspberry Pi

SSH into your Raspberry Pi and run these commands:

### Step 1: Download cloudflared

```bash
# For Raspberry Pi (ARM64)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb

# Install
sudo dpkg -i cloudflared-linux-arm64.deb

# Verify installation
cloudflared --version
```

If you get an error about architecture, try the ARM version:
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm.deb
sudo dpkg -i cloudflared-linux-arm.deb
```

### Step 2: Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

**What happens:**
1. A URL will appear in the terminal
2. Copy and paste it into a browser (on your computer, not the Pi)
3. Log in to Cloudflare
4. Select your domain (if you have multiple)
5. Click "Authorize"
6. Return to the Pi terminal - you'll see "Successfully authenticated"

A credentials file is now saved at: `~/.cloudflared/cert.pem`

---

## Part 3: Create the Tunnel

### Step 1: Create a Tunnel

```bash
cloudflared tunnel create hw-helper-errors
```

**Output will show:**
```
Created tunnel hw-helper-errors with id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**IMPORTANT**: Copy the tunnel ID (the long string with dashes). You'll need it in the next step.

### Step 2: Create Configuration File

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Paste this configuration (replace `YOUR_TUNNEL_ID` and `YOUR_DOMAIN`):

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/pi/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: errors.YOUR_DOMAIN.com
    service: http://localhost:5000
  - service: http_status:404
```

**Example with actual values:**
```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: /home/pi/.cloudflared/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json

ingress:
  - hostname: errors.myhelper.com
    service: http://localhost:5000
  - service: http_status:404
```

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

---

## Part 4: Configure DNS (Skip if Using Auto-Generated URL)

If you're using Option A (auto-generated subdomain), **skip to Part 5**.

If you're using a custom domain (Option B or C):

### Method 1: Automatic DNS Route (Easiest)

```bash
cloudflared tunnel route dns hw-helper-errors errors.yourdomain.com
```

Replace `errors.yourdomain.com` with your actual subdomain.

**Example:**
```bash
cloudflared tunnel route dns hw-helper-errors errors.myhelper.com
```

**Output:**
```
Added CNAME record errors.myhelper.com which will route to tunnel a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Method 2: Manual DNS Setup (If automatic fails)

1. **Go to Cloudflare Dashboard**: https://dash.cloudflare.com
2. **Select your domain**
3. **Go to DNS → Records**
4. **Click "Add record"**
5. **Fill in:**
   - **Type**: `CNAME`
   - **Name**: `errors` (or whatever subdomain you want)
   - **Target**: `YOUR_TUNNEL_ID.cfargotunnel.com`
   - **Proxy status**: Enabled (orange cloud)
   - **TTL**: Auto
6. **Click Save**

**Example:**
```
Type: CNAME
Name: errors
Target: a1b2c3d4-e5f6-7890-abcd-ef1234567890.cfargotunnel.com
Proxy: ✅ Proxied
```

---

## Part 5: Start Your Flask Backend

Make sure your error reporting server is running:

```bash
cd ~/Downloads/HW\ Helper\ copy\ 2/backend
source venv/bin/activate
python error_server.py
```

**Expected output:**
```
============================================================
Error Reporting API Server
============================================================
Database: /home/pi/.../backend/error_reports.db
Uploads: /home/pi/.../backend/uploads

Endpoints:
  POST /api/report          - Receive error reports
  GET  /api/reports         - List all reports
  GET  /api/reports/<id>    - Get report details
  GET  /                    - Admin dashboard
  GET  /health              - Health check

Starting server on http://0.0.0.0:5000
============================================================
```

**Keep this terminal open** (the Flask server needs to stay running).

---

## Part 6: Start the Tunnel

Open a **NEW SSH session** to your Pi (keep Flask running in the other one).

### Test Run (Foreground)

```bash
cloudflared tunnel run hw-helper-errors
```

**Expected output:**
```
2025-11-12T... INF Starting tunnel tunnelID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
2025-11-12T... INF Connection registered connIndex=0 location=ATL
2025-11-12T... INF Updated to new configuration
```

**If using auto-generated URL**, you'll see:
```
+--------------------------------------------------------------------------------------------+
|  Your free tunnel has started! Visit it at:                                              |
|  https://random-words-1234.trycloudflare.com                                             |
+--------------------------------------------------------------------------------------------+
```

**Copy this URL!** You'll use it in config.json.

**Leave this running** and test your setup (see Part 7).

---

## Part 7: Test Your Setup

### If Using Custom Domain:

Open a browser and go to:
```
https://errors.yourdomain.com
```

You should see the **Error Reports Dashboard**.

### If Using Auto-Generated URL:

Open a browser and go to the URL shown in the tunnel output:
```
https://random-words-1234.trycloudflare.com
```

### Test the Health Endpoint:

```bash
curl https://errors.yourdomain.com/health
```

**Expected response:**
```json
{"status":"healthy","service":"error-reporting-api","timestamp":"2025-11-12T..."}
```

### If It's Not Working:

**Check these:**
1. Flask is running on port 5000 ✅
2. Tunnel is running ✅
3. DNS has propagated (wait 5-10 minutes) ⏳
4. No typos in config.yml ✅

**View tunnel logs:**
```bash
cloudflared tunnel info hw-helper-errors
```

---

## Part 8: Run Tunnel as Background Service (Permanent Setup)

Once everything works, make the tunnel start automatically:

### Step 1: Install as Service

```bash
sudo cloudflared service install
```

### Step 2: Start the Service

```bash
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### Step 3: Check Status

```bash
sudo systemctl status cloudflared
```

**Expected output:**
```
● cloudflared.service - cloudflared
   Loaded: loaded (/etc/systemd/system/cloudflared.service; enabled)
   Active: active (running) since ...
```

### Step 4: View Logs

```bash
sudo journalctl -u cloudflared -f
```

Press `Ctrl+C` to exit logs.

**Now the tunnel will:**
- ✅ Start automatically when Pi boots
- ✅ Restart if it crashes
- ✅ Run in background

---

## Part 9: Make Flask Backend Auto-Start (Optional)

Create a systemd service for Flask:

### Step 1: Create Service File

```bash
sudo nano /etc/systemd/system/hw-helper-backend.service
```

Paste this content (update paths if needed):

```ini
[Unit]
Description=HW Helper Error Reporting Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Downloads/HW Helper copy 2/backend
Environment="PATH=/home/pi/Downloads/HW Helper copy 2/backend/venv/bin"
ExecStart=/home/pi/Downloads/HW Helper copy 2/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 error_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Save and exit**: `Ctrl+X`, `Y`, `Enter`

### Step 2: Install Gunicorn

```bash
cd ~/Downloads/HW\ Helper\ copy\ 2/backend
source venv/bin/activate
pip install gunicorn
```

### Step 3: Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl start hw-helper-backend
sudo systemctl enable hw-helper-backend
```

### Step 4: Check Status

```bash
sudo systemctl status hw-helper-backend
```

**Now Flask will also auto-start on boot!**

---

## Part 10: Update Homework Helper Config

On your **main computer** (where you run Homework Helper):

1. **Open**: `HW Helper copy 2/config.json`

2. **Update the endpoint:**

**If using custom domain:**
```json
{
  "api_key": "your-key-here",
  "selected_model": "google/gemini-2.0-flash-exp:free",
  "error_reporting": {
    "enabled": true,
    "endpoint": "https://errors.yourdomain.com/api/report"
  }
}
```

**If using auto-generated URL:**
```json
{
  "api_key": "your-key-here",
  "selected_model": "google/gemini-2.0-flash-exp:free",
  "error_reporting": {
    "enabled": true,
    "endpoint": "https://random-words-1234.trycloudflare.com/api/report"
  }
}
```

3. **Save the file**

4. **Restart Homework Helper**

---

## Testing End-to-End

1. **Run Homework Helper**
2. **Click "Report Error" button**
3. **Check your Pi's dashboard**: `https://errors.yourdomain.com`
4. **You should see the new error report!**

---

## Troubleshooting

### "502 Bad Gateway"
**Problem**: Flask backend not running

**Solution**:
```bash
sudo systemctl status hw-helper-backend
sudo systemctl start hw-helper-backend
```

### "Can't reach this page" / DNS not resolving
**Problem**: DNS not configured or not propagated

**Solution**:
- Wait 10 more minutes
- Check DNS record in Cloudflare dashboard
- Try `nslookup errors.yourdomain.com`

### Tunnel won't start
**Problem**: Config file error

**Solution**:
```bash
cat ~/.cloudflared/config.yml
# Check for typos, verify tunnel ID matches
cloudflared tunnel info hw-helper-errors
```

### "Authentication failed"
**Problem**: Not logged in to Cloudflare

**Solution**:
```bash
cloudflared tunnel login
```

### Error reports not arriving
**Problem**: Wrong endpoint in config.json

**Solution**:
- Test endpoint: `curl -X POST https://errors.yourdomain.com/api/report -d '{"test":"data"}' -H "Content-Type: application/json"`
- Check Flask logs: `sudo journalctl -u hw-helper-backend -f`

---

## Summary of What's Running

| Service | Location | URL | Auto-Start |
|---------|----------|-----|------------|
| Flask Backend | Raspberry Pi port 5000 | http://localhost:5000 | ✅ (if configured) |
| Cloudflare Tunnel | Raspberry Pi | - | ✅ (if configured) |
| Public Dashboard | Internet | https://errors.yourdomain.com | - |
| Error Reporting API | Internet | https://errors.yourdomain.com/api/report | - |

---

## Commands Reference

### Check Status
```bash
# Tunnel status
sudo systemctl status cloudflared

# Flask status
sudo systemctl status hw-helper-backend

# View Flask logs
sudo journalctl -u hw-helper-backend -f

# View tunnel logs
sudo journalctl -u cloudflared -f
```

### Restart Services
```bash
# Restart tunnel
sudo systemctl restart cloudflared

# Restart Flask
sudo systemctl restart hw-helper-backend
```

### Stop Services
```bash
# Stop tunnel
sudo systemctl stop cloudflared

# Stop Flask
sudo systemctl stop hw-helper-backend
```

---

## Cost Breakdown

- **Cloudflare Tunnel**: FREE ✅
- **HTTPS Certificate**: FREE (auto-included) ✅
- **Bandwidth**: FREE (unlimited) ✅
- **Custom Domain**:
  - Auto-generated: FREE ✅
  - Cloudflare Registrar: $8-15/year 💰
  - Existing domain: Whatever you already pay 💰

**Recommended**: Start with auto-generated URL (free), then upgrade to custom domain later if needed.

---

## Next Steps

1. ✅ Follow this guide to set up tunnel
2. ✅ Test error reporting
3. ✅ Monitor dashboard for incoming reports
4. 📊 Optionally set up database backups
5. 🔒 Optionally add authentication to admin dashboard

You're all set! Your Raspberry Pi is now accessible worldwide with HTTPS. 🎉
