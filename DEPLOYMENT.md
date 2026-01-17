# Public Hosting & Deployment Guide

To take **AgriDecision-TN** from your local computer to a public URL (e.g., `www.agridecision.tn`), follow this 4-step roadmap.

## 1. Prerequisites (External Setup)
Before configuring the code, you need two things:
*   **A Domain Name**: Buy one from providers like Namecheap, GoDaddy, or OVH (e.g., `.tn` domains).
*   **A VPS (Virtual Private Server)**: Get a Linux server (Ubuntu recommended) from DigitalOcean, AWS, or similar.
*   **Point the Domain**: In your domain settings, set an **A Record** pointing to your VPS IP address.

## 2. Server Preparation
On your new VPS, install the "Engine":
```bash
# Update and install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
```

## 3. Deployment Steps (Using current project)
Once you have the server, you will use the **Production Files** I've already created for you:

1.  **Build the Frontend**: Run `npm run build` in your local `frontend` folder. This creates the `dist` folder.
2.  **Transfer Files**: Copy the project files (including `backend/`, `nginx.conf`, and `docker-compose.prod.yml`) to the server.
3.  **Set Environment Variables**: Create a `.env` file on the server with your production keys (OpenAI, Weather, JWT Secret).
4.  **Launch**:
    ```bash
    docker-compose -f docker-compose.prod.yml up -d --build
    ```

## 4. Activating Security (SSL/HTTPS)
I have configured **Nginx** to handle SSL. To specifically activate the free "Let's Encrypt" certificate:
1.  On the server, install Certbot: `sudo apt install certbot -y`.
2.  Run the certificate generator:
    ```bash
    sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
    ```
3.  Point your `nginx.conf` to the generated keys (standard location is `/etc/letsencrypt/live/...`).

---

### 💡 Why this approach?
*   **Docker Containerization**: Your app will run exactly the same on the server as it does on your machine.
*   **Gunicorn**: I've configured the production backend to use Gunicorn for high traffic and stability.
*   **Nginx**: Acts as a shield, handling the website's speed and security.

**Once you have a VPS and a Domain, I can help you with the specific commands to connect them!**
