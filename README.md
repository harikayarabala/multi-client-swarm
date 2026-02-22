# Multi-Client Docker Swarm Deployment on AWS EC2 (Traefik + Secrets + CI/CD)

## Objective
Design and deploy a scalable multi-client application environment on AWS EC2 using Docker Swarm, supporting:
- Multiple Node.js and Python services
- Client-specific deployments (separate DB strings / client name)
- Horizontal scaling
- Reverse proxy routing (Traefik)
- Basic monitoring/logging (proposal)

---

## What’s Deployed
### Services
- **Client A (Node.js REST API)** → `client-a-node-app`
- **Client B (FastAPI)** → `client-b-python-app`
- **Traefik Reverse Proxy** → routes traffic based on host rules

### Swarm Cluster
- **1 Manager + 1 Worker**
- Services run as replicas across both nodes (high availability)

### Networking
- **Overlay network**: `appnet` (Swarm overlay)

### Secrets (Client-Specific)
Stored securely using Docker Swarm Secrets and mounted at runtime:
- `client_a_db`, `client_a_name`
- `client_b_db`, `client_b_name`

Secrets are available inside containers at:
- `/run/secrets/client_a_db`, `/run/secrets/client_a_name`
- `/run/secrets/client_b_db`, `/run/secrets/client_b_name`

---

## Repository Structure
- `.github/workflows/` → GitHub Actions pipeline (build + push + deploy)
- `client-a-node-app/` → Node app + Dockerfile + .dockerignore
- `client-b-python-app/` → FastAPI app + Dockerfile + .dockerignore
- `swarm/` → `stack.yml` and secret txt files used for secret creation

---

## 1) Containerization
### Node (Multi-Stage Build)
- Uses multi-stage Docker build to reduce image size and keep runtime minimal.
- `.dockerignore` included.

### Python (Slim Image)
- Uses slim base image + installs only requirements.
- `.dockerignore` included.

---

## 2) Swarm Setup (Manager + Worker)
### Initialize Swarm (Manager)
```bash
docker swarm init

##Join Worker Node
docker swarm join --token <TOKEN> <MANAGER_PRIVATE_IP>:2377
**Verify nodes**
docker node ls

**3) Create Secrets**

From swarm/ folder:

docker secret create client_a_db client_a_db.txt
docker secret create client_a_name client_a_name.txt
docker secret create client_b_db client_b_db.txt
docker secret create client_b_name client_b_name.txt

docker secret ls


**4) Deploy the Swarm Stack**

From swarm/ folder:

docker stack deploy -c stack.yml appstack
docker stack services appstack

Deployment config includes:

replicas: 3+

restart_policy: on-failure

update_config: parallelism 1, delay 10s

5) Reverse Proxy Routing (Traefik)

Traefik routes based on Host rules:

client-a.example.com → Node app

client-b.example.com → Python app

**Test routing (from EC2)**
curl -o /dev/null -w "client-a => %{http_code}\n" -H "Host: client-a.example.com" http://127.0.0.1/
curl -o /dev/null -w "client-b => %{http_code}\n" -H "Host: client-b.example.com" http://127.0.0.1/

**Validate API responses (DB values read from secrets)**
curl -s -H "Host: client-a.example.com" http://127.0.0.1/
curl -s -H "Host: client-b.example.com" http://127.0.0.1/

Expected (example):

{"message":"Hello from Client-A","database":"postgres://client-a-db"}
{"message":"Hello from Client-B","database":"postgres://client-b-db"}

**Traefik Dashboard **(optional)
http://<EC2_PUBLIC_IP>:8080


**6) Secrets Proof (Inside Container)**

CID=$(docker ps -q --filter "name=appstack_client-a-node" | head -n 1)
docker exec -it "$CID" sh -lc 'ls -l /run/secrets; echo "----"; cat /run/secrets/client_a_db; echo'

**7) Scaling Scenario**
Manual Scaling
docker service scale appstack_client-a-node=5
docker service ls | egrep "client-a-node|client-b-python|traefik"

**Worker Node Participation Proof**

docker service ps appstack_client-a-node --format "table {{.Name}}\t{{.Node}}\t{{.CurrentState}}"



**8) Rolling Update & Zero Downtime**
Rolling updates are configured via:

update_config.parallelism: 1

update_config.delay: 10s

Swarm rolling updates are configured via:

update_config.parallelism: 1

update_config.delay: 10s

Swarm updates containers one-by-one, keeping the service available.

Example:

docker service update --image <new_image_tag> appstack_client-a-node
How Swarm Ensures Availability

Docker Swarm ensures availability by:

Running multiple replicas across nodes

Automatically rescheduling failed tasks

Performing rolling updates without taking the service down

Service Discovery

Swarm provides internal DNS-based service discovery on overlay networks.
Traefik uses Swarm provider to discover services and load-balance across replicas.

9) CI/CD Pipeline (GitHub Actions)

Pipeline steps:

Checkout code

Build Docker images

Tag images with commit SHA

Push to Docker Hub

SSH into EC2 manager

Deploy/update stack (docker stack deploy)

Bonus idea (design):

Branch-based deploy: dev / stage / prod using separate stack files and secrets.

10) Multi-Client Strategy (20 clients/month) — Design Thinking

Recommended approach:

Shared Swarm cluster, per-client subdomain routing

Naming convention for secrets per client (e.g., client_x_db, client_x_name)

Use node labels + placement constraints for isolation if required

Cost optimization:

pack smaller clients on shared nodes

separate premium clients onto dedicated nodes

autoscale EC2 using ASG based on CPU/memory

11) Monitoring & Logging (Proposal)

Metrics: Prometheus + Grafana (container/node metrics)

Logging: Loki or ELK centralized logging

Add HEALTHCHECK in Dockerfiles + optional Traefik health routing

