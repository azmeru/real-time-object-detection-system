# AWS Deployment Guide

## Architecture

```
Internet → CloudFront → S3 (Frontend)
                ↓
         EC2 GPU Instance (Backend API)
                ↓
           RDS PostgreSQL
```

---

## 1. Backend — EC2 GPU Instance

### Launch instance

- AMI: **Deep Learning AMI GPU PyTorch 2.x (Ubuntu 22.04)**
- Instance type: `g4dn.xlarge` (NVIDIA T4, 16GB VRAM, ~$0.53/hr)
- Storage: 100 GB gp3
- Security group:
  - Inbound: TCP 8000 (from CloudFront/ALB), TCP 22 (your IP only)
  - Outbound: all

### Deploy

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker + NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list \
  | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Clone repo
git clone https://github.com/YOUR_USERNAME/real-time-object-detection.git
cd real-time-object-detection

# Set environment
cp backend/.env.example backend/.env
# Edit DATABASE_URL to point at RDS instance

# Launch with GPU profile
docker compose --profile gpu up -d backend-gpu db
```

### Environment variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@<RDS_ENDPOINT>:5432/detection_db
YOLO_MODEL=yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.25
OPENVINO_DEVICE=CPU
DEBUG=false
```

---

## 2. Database — Amazon RDS PostgreSQL

- Engine: PostgreSQL 16
- Instance: `db.t3.micro` (free tier) or `db.t3.small` for production
- Enable Multi-AZ for production
- Security group: allow TCP 5432 from EC2 security group only

---

## 3. Frontend — S3 + CloudFront

### Build

```bash
cd frontend
npm ci
VITE_API_BASE_URL=https://api.yourdomain.com npm run build
```

### Upload to S3

```bash
aws s3 mb s3://object-detection-frontend
aws s3 sync dist/ s3://object-detection-frontend --delete
aws s3 website s3://object-detection-frontend \
  --index-document index.html --error-document index.html
```

### CloudFront distribution

1. Create distribution → Origin: S3 bucket website endpoint
2. Add a second origin for the API: `https://api.yourdomain.com`
3. Behavior: `/api/*` → forward to API origin; `/*` → S3 origin
4. Enable HTTPS (ACM certificate)
5. Default root object: `index.html`

---

## 4. HTTPS with ACM

```bash
# Request certificate (us-east-1 for CloudFront)
aws acm request-certificate \
  --domain-name yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# For the EC2 API endpoint, use Nginx + Certbot:
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

Nginx reverse-proxy config (`/etc/nginx/sites-available/api`):

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 50M;
    }
}
```

---

## 5. Cost estimate (light usage)

| Service | Config | Monthly |
|---|---|---|
| EC2 g4dn.xlarge | On-demand, 8h/day | ~$130 |
| RDS db.t3.micro | Single-AZ | ~$15 |
| S3 + CloudFront | <10 GB transfer | <$2 |
| **Total** | | **~$150/mo** |

Use a **Spot instance** for the EC2 to cut costs by up to 70%.

---

## 6. One-command local startup

```bash
# CPU only
docker compose up -d

# With GPU
docker compose --profile gpu up -d

# Access
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```
