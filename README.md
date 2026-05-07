# Thin BI Portal

Lightweight BI portal built on Streamlit + Snowflake. Each dashboard is a folder
under `dashboards/[department]/[dashboard_name]/` with a `config.json` and a
`query.sql`. The app runs the SQL once per dashboard, caches the DataFrame, and
renders Plotly visualizations driven by the JSON config.

## Deployment

Deployed via Streamlit Cloud, auto-deploying from `main`. Snowflake credentials
live in the Streamlit Cloud Secrets UI — see `.streamlit/secrets.toml.example`
for the expected schema.
