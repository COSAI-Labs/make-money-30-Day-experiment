---
title: "Free JSON to YAML Converter API"
published: false
tags: ["api", "json", "yaml", "devops"]
---

## Free JSON to YAML Converter API

Convert between JSON and YAML programmatically. Great for Kubernetes configs, CI/CD, and data transformation.

### Endpoint

```
POST https://toolpipe.dev/api/convert/json-to-yaml
```

### Request Body

```json
{
  "json_data": "{\"name\": \"app\", \"replicas\": 3}"
}
```

Or convert YAML to JSON:

```json
{
  "yaml_data": "name: app\nreplicas: 3"
}
```

### Use Cases

- Kubernetes manifest generation
- CI/CD config transformation
- Data format migration scripts
- API response format conversion

No signup. JSON API. CORS enabled.

**Explore 70+ tools:** [toolpipe.dev](https://toolpipe.dev)
