# Hindsight Cloud connection test

This is an isolated integration spike. It does not freeze the final LotLens backend stack.

## 1. Local setup (Windows PowerShell)

From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements-hindsight.txt
Copy-Item .env.example .env
notepad .env
```

In the local `.env`, set:
- `HINDSIGHT_API_KEY` to your secret key (never commit it).
- `HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io`.
- `HINDSIGHT_BANK_ID` to the exact bank ID shown in Hindsight Cloud (we expect `lotlens-dev` if you created it with that ID).

`.env` is gitignored. Do not paste the API key into chat, GitHub issues, source files, or screenshots.

## 2. Test an existing bank

```powershell
py tools/hindsight_smoke_test.py
```

This performs a Recall request and confirms the API key and bank are usable. An empty bank can return zero memories.

## 3. If the bank does not exist

Create it using the SDK:

```powershell
py tools/hindsight_smoke_test.py --create-bank
```

Do not use this flag if the bank already exists.

## 4. Seed the synthetic proof-of-concept data

```powershell
py tools/hindsight_smoke_test.py --seed-demo
```

This retains two synthetic cases: one with a QA-verified effective corrective action and one with an ineffective action and unconfirmed cause. Retaining data may incur usage charges.

Then run Recall again:

```powershell
py tools/hindsight_smoke_test.py
```

## 5. Optional Reflect test

```powershell
py tools/hindsight_smoke_test.py --reflect
```

Reflect is an AI reasoning operation and may incur usage charges. Run it only after checking the account's balance/usage.

## Troubleshooting

- 401: API key is invalid, revoked, or copied incorrectly.
- 402: account has insufficient credits for the operation.
- 404: bank ID does not exist or is misspelled.
- Network/timeout: verify the endpoint shown on Hindsight Cloud's Connect page.

Official SDK guide: https://docs.hindsight.vectorize.io/enterprise/python-sdk/
Cloud connection guide: https://docs.hindsight.vectorize.io/cloud/api-integration/
