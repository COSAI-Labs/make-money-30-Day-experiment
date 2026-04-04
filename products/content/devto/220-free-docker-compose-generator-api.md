---
title: "Free Docker Compose Generator API"
published: false
tags: ["docker", "api", "devops", "webdev"]
---

## Free Docker Compose Generator API

Generate docker-compose.yml configurations via a simple API call.

### Endpoint

```
POST https://toolpipe.dev/api/generate/docker-compose
```

### Example

```bash
curl -X POST https://toolpipe.dev/api/generate/docker-compose \
  -H "Content-Type: application/json" \
  -d '{"services": ["postgres", "redis", "nginx"]}'
```

### Supported Services

- Databases: PostgreSQL, MySQL, MongoDB, Redis
- Web servers: Nginx, Traefik, Caddy
- Message queues: RabbitMQ, Kafka
- Monitoring: Prometheus, Grafana

No signup required. Part of 240+ free tools at [toolpipe.dev](https://toolpipe.dev).
