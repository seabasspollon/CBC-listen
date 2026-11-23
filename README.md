# CBC Listen

A simple, high-contrast CBC listening page with four large choices:
- CBC Radio One Vancouver (690 AM / 88.1 FM)
- Quirks & Quarks
- White Coat, Black Art
- Ideas

## How podcast updates work

GitHub Actions retrieves the newest playable episode from CBC's public RSS feeds every six hours and writes the result to `latest.json`. The listening page reads that small JSON file. Safari no longer needs to fetch CBC RSS feeds directly or use third-party CORS proxy services.

You can also refresh episodes manually from the **Actions** tab by running **Refresh CBC podcast episodes**.

## Publish with GitHub Pages

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Choose branch **main** and folder **/(root)**, then Save.
4. Wait for GitHub Pages to publish. The site address will be shown on that page.

## First-time setup

After the workflow file is committed, open **Actions → Refresh CBC podcast episodes → Run workflow** once. When the run completes successfully, it will create `latest.json`. The workflow will then refresh it every six hours.

No passwords, API keys, or private credentials are needed.
