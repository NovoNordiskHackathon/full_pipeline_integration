### Common Issue: script paths and environment

If you see errors like "Missing conversion script" or failures due to hardcoded absolute paths:

- Ensure you run scripts from the repository root. All scripts resolve their own directory and use local Python files.
- `conversion_run.sh` and `run_extraction.sh` now call `doc_to_pdf.py` and `simpletext_extract.py` from this folder directly, not from external paths.
- Export Adobe credentials before running:

```bash
export PDF_SERVICES_CLIENT_ID=your_client_id
export PDF_SERVICES_CLIENT_SECRET=your_client_secret
```

- Default structured JSON names used by `Structuring_JSON.sh` are `structuredData.json` in each extract folder.

- If `PTD_Gen/PTD Template v.2_Draft (1).xlsx` is missing, the pipeline will stream to `PTD_Gen/PTD_Output.xlsx` instead.

