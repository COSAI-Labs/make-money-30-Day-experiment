# ToolPipe AI Agent - Auth0 Hackathon Submission

## What it does
An AI agent that securely accesses 70+ developer utility APIs through Auth0 Token Vault. Developers interact with the agent to format code, generate QR codes, analyze text, process PDFs, and more, all with enterprise-grade authentication.

## How it works
1. User authenticates via Auth0
2. Auth0 Token Vault securely stores API credentials
3. AI agent receives natural language requests
4. Agent selects appropriate ToolPipe API endpoints
5. Agent executes API calls through Token Vault
6. Results returned to user

## Tech Stack
- Auth0 for authentication + Token Vault
- FastAPI backend (ToolPipe - 70+ endpoints)
- Python AI agent orchestrator
- OpenAPI spec for tool discovery

## API Endpoints Available
70+ endpoints including:
- Text: JSON/XML/YAML/SQL formatting, text summarization, language detection
- Generation: QR codes, UUIDs, passwords, hashes, Lorem Ipsum
- Encoding: Base64, URL encoding, HTML entities, hex conversion
- PDF: Merge, split, compress, watermark, extract text
- Network: DNS lookup, IP info, website status
- And many more at /docs

## Live Demo
https://assessing-scoop-authorities-sheet.trycloudflare.com

## Hackathon
Auth0 "Authorized to Act" Hackathon
Deadline: April 6, 2026
