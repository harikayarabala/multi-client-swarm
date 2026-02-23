                    +----------------------+
                    |    Users / Browser   |
                    +----------+-----------+
                               |
                          HTTP/HTTPS
                               |
                    +----------v-----------+
                    |   Traefik (Ingress)  |
                    |  Host-based routing  |
                    +----+------------+----+
                         |            |
             client-a.*  |            |  client-b.*
                         |            |
           +-------------v--+     +---v--------------+
           | Client-A Node   |     | Client-B FastAPI |
           | replicas: 3     |     | replicas: 3      |
           +-----------------+     +------------------+

           # Multi-Client Docker Swarm on AWS EC2 (Traefik + Prometheus + Grafana + Loki)

This repo demonstrates a **multi-client** deployment on **AWS EC2** using **Docker Swarm**, supporting:
- Multiple services (Node.js + FastAPI)
- Client-specific routing via **Traefik**
- Horizontal scaling (replicas)
- Basic monitoring (**Prometheus + Node Exporter + cAdvisor + Grafana**)
- Centralized logging (**Loki + Promtail + Grafana**)

---

## ✅ What’s deployed

### Client Apps
- **Client-A**: Node.js REST API  
  Route: `client-a.<your-domain>` → Node service
- **Client-B**: Python FastAPI  
  Route: `client-b.<your-domain>` → FastAPI service

Each client has:
- Separate env variables
- Separate DB connection string (example values)

### Reverse Proxy
- **Traefik** (routes & load-balances across replicas)

### Monitoring
- Prometheus targets:
  - `prometheus`
  - `node-exporter`
  - `cadvisor`
- Grafana dashboards (Node Exporter + cAdvisor)

### Logging
- Loki + Promtail (container logs visible in Grafana Explore)

---

## 🧱 Architecture (high level)

Users → Traefik (80/443) → Swarm services (replicas)  
Monitoring: Prometheus scrapes node-exporter + cAdvisor  
Logging: Promtail → Loki → Grafana Explore

---

## 📌 Prerequisites

### On AWS
- 1 Manager + 1 Worker EC2 (Ubuntu recommended)
- Security Group open:
  - `22` (SSH)
  - `80` (HTTP)
  - `443` (HTTPS)
  - `8080` (Traefik dashboard - optional)
  - `9090` (Prometheus - optional)
  - `3000` (Grafana - optional)

### On both nodes
- Docker installed
- Swarm initialized

---

## 🚀 Setup Docker Swarm

### 1) On Manager
```bash
docker swarm init


##🌐 DNS / Domain Setup

Create DNS A records pointing to your EC2 public IP:

client-a.<your-domain> → <EC2_PUBLIC_IP>

client-b.<your-domain> → <EC2_PUBLIC_IP>

Example:

client-a.harikayarabaladevops.in

client-b.harikayarabaladevops.in


📦 Deploy the Stack

On the manager node:
git clone https://github.com/harikayarabala/multi-client-swarm.git
cd multi-client-swarm
docker stack deploy -c stack.yml appstack

Check services:
docker service ls
docker stack ps appstack

✅ Validate Routing (Client Apps)
Option 1: Using domains in browser

http(s)://client-a.<your-domain>

http(s)://client-b.<your-domain>

Expected JSON like:
{"message":"Hello from Client-A","database":"postgres://client-a-db"}
{"message":"Hello from Client-B","database":"postgres://client-b-db"}

Option 2: Using curl with Host header (best for testing)
curl -i http://<EC2_PUBLIC_IP>/ -H "Host: client-a.<your-domain>"
curl -i http://<EC2_PUBLIC_IP>/ -H "Host: client-b.<your-domain>"

Scaling (replicas)

Scale Client-A:

docker service scale appstack_client-a-node=3

Scale Client-B:

docker service scale appstack_client-b-python=3

Verify:

docker service ps appstack_client-a-node
docker service ps appstack_client-b-python
🔁 Rolling Update (Zero downtime)

Update image (example):

docker service update \
  --image <your-image>:<new-tag> \
  --update-parallelism 1 \
  --update-delay 10s \
  appstack_client-a-node

Swarm ensures availability by:

Updating replicas gradually (parallelism=1)

Keeping old replicas running until new ones are healthy

Rescheduling tasks on failure


Monitoring
Prometheus

Targets page:

http://<EC2_PUBLIC_IP>:9090/targets

Grafana

http://<EC2_PUBLIC_IP>:3000

Check dashboards:

Node Exporter Full

cAdvisor / Container metrics

🧾 Logging (Loki)

Grafana → Explore → Loki

Example query:

{job="docker"}

You should see container logs for services like:

traefik

promtail

loki

client-a / client-b apps


🧰 Useful Commands

Service logs:

docker service logs -f appstack_client-a-node
docker service logs -f appstack_client-b-python

Traefik dashboard:

http://<EC2_PUBLIC_IP>:8080/dashboard#/

List networks:

docker network ls

Cleanup

Remove stack:

docker stack rm appstack

(Optional) leave swarm:

docker swarm leave --force

🧠 Notes / Multi-client expansion plan

If 20 new clients onboard monthly:

Use shared swarm cluster + templated service definitions

Naming convention: client-<id>-app

Keep client-specific secrets in Docker secrets

Use node labels + placement constraints for heavy clients

Use CI/CD tagging strategy: app:<commit-sha> per release
Evidence (Screenshots)

## 📎 Evidence (Screenshots)

### Prometheus Targets
![Prometheus](evidence/prometheus-targets.png)

### Grafana Logs
![Grafana Logs](evidence/grafana-logs.png)

### Node Exporter Dashboard
![Node Exporter](evidence/node-exporter-dashboard.png)

### cAdvisor Dashboard
![cAdvisor](evidence/cadvisor-dashboard.png)

### Traefik Dashboard
![Traefik](evidence/traefik-dashboard.png)

### Client-A Response
![Client-A](evidence/client-a-output.png)

### Client-B Response
![Client-B](evidence/client-b-output.png)
