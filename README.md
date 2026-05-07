# Thin BI Portal

A high-performance, headless BI tool. Dashboards are defined as code
(`config.json` + `query.sql`) in a directory tree, executed once against
Snowflake per dashboard load, then sliced in pandas for instant filtering
and per-viz aggregation.

## Status

**Step 1: connection test.** Verify Snowflake key-pair auth works before
building the engine.

## Local setup

```bash
# 1. Create and activate a venv
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your secrets file from the template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Then edit .streamlit/secrets.toml and paste your private key.

# 4. Run the app
streamlit run app.py
```

Click the **Test Snowflake connection** button. You should see a row with
your Snowflake version, user, role, and warehouse.

## Project layout

```
thin-bi/
├── .streamlit/
│   ├── secrets.toml              ← gitignored, your local creds
│   └── secrets.toml.example      ← template
├── dashboards/                   ← (empty — populated in step 3)
├── engine/
│   ├── __init__.py
│   └── snowflake_client.py       ← key-pair auth + query runner
├── app.py                        ← connection test for step 1
├── requirements.txt
└── .gitignore
```
