# Streamlit Troubleshooting

This project is usually run locally with:

```bash
streamlit run app/streamlit_app.py
```

## Stale Labels or Old UI

If the app shows old labels, translation keys, or behavior that has already been fixed, an older Streamlit process may still be running on another port.

On Windows PowerShell, list local Streamlit ports:

```powershell
Get-NetTCPConnection -State Listen |
  Where-Object { $_.LocalPort -ge 8500 -and $_.LocalPort -le 8525 } |
  Select-Object LocalAddress, LocalPort, OwningProcess |
  Sort-Object LocalPort
```

To stop one stale server:

```powershell
Stop-Process -Id <OwningProcess> -Force
```

Then restart the app from the repository root:

```powershell
cd C:\Projects\huntington-research-assistant
streamlit run app/streamlit_app.py
```

## OneDrive and SQLite

Avoid placing the SQLite cache inside a OneDrive-synced folder. The app defaults to a local app-data cache path to reduce sync and file-locking problems.

If needed, set an explicit local cache path:

```powershell
$env:HRA_CACHE_PATH = "C:\Users\$env:USERNAME\AppData\Local\hra\cache.sqlite3"
```

## Provider Connectivity

If Europe PMC, PubMed, or ClinicalTrials.gov requests fail, verify that:

- the machine has internet access;
- no local proxy is intercepting requests;
- `HRA_TRUST_ENV` is only enabled when system proxy settings are intentional;
- the provider service is not temporarily unavailable.

The app should fail gracefully and keep already retrieved local data available where possible.
