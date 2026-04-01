# DevAgent: AI-Powered Developer Assistant with Secure Tool Access

An AI agent that securely accesses developer tools and APIs on behalf of authenticated users, using Auth0 Token Vault for credential management.

## What It Does

DevAgent is an AI-powered developer assistant that can:
- Format and validate JSON, YAML, XML
- Generate QR codes, UUIDs, passwords
- Process PDFs (merge, split, compress)
- Analyze code quality and SEO
- Look up DNS records and WHOIS data
- Access GitHub repos on behalf of the user (via Auth0 Token Vault)

## How It Uses Auth0 Token Vault

1. **User signs in** via Auth0 with GitHub/Google SSO
2. **Token Vault stores** the OAuth tokens securely
3. **AI agent requests** a scoped token when it needs to access GitHub
4. **Token Vault exchanges** the stored token for a fresh access token
5. **Agent uses** the token to read repos, create issues, etc.
6. **Tokens are rotated** automatically by Token Vault

This means the AI agent never sees or stores raw credentials. Auth0 Token Vault handles all token lifecycle management.

## Architecture

```
User -> Auth0 Login -> Token Vault (stores GitHub/Google tokens)
                           |
                    AI Agent (Claude/GPT)
                           |
              +------------+------------+
              |                         |
         ToolPipe API              GitHub API
       (70+ dev tools)          (via Token Vault)
```

## Tech Stack

- **Frontend**: Next.js with Auth0 SDK
- **AI Agent**: Vercel AI SDK with tool calling
- **Auth**: Auth0 Universal Login + Token Vault
- **Tools**: ToolPipe API (70+ endpoints)
- **Hosting**: Vercel

## Setup

```bash
npm install
cp .env.example .env.local
# Add your Auth0 credentials
npm run dev
```

## Environment Variables

```
AUTH0_SECRET=
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
AUTH0_TOKEN_VAULT_CONNECTION=github
TOOLPIPE_API_URL=https://assessing-scoop-authorities-sheet.trycloudflare.com
```

## Built for the "Authorized to Act" Auth0 Hackathon

This project demonstrates how Auth0 Token Vault enables AI agents to securely access third-party APIs on behalf of users without handling raw credentials.
