# File Presence Check & CloudWatch Audit

Minimal CI that verifies required files **via GitHub API** and logs **successful** runs to CloudWatch.

---

## GitHub Secrets
Repo ► **Settings → Secrets and variables → Actions**. Create:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `LOG_GROUP_NAME_BETA` (e.g., `/org/quality-gate/beta`)
- `LOG_GROUP_NAME_PROD` (e.g., `/org/quality-gate/prod`)

---

## Run the file presence check manually
```bash
python -m pip install --upgrade pip requests
python check_required_files.py
echo $?   # 0 = all present, 1 = missing
```
> The script checks **remote** repo `MLindle/File_Presence_Check_Project@main` (constants at top of the script).

---

## Define custom required files (`.required-files.yml`)
- **One path per line** (plain text, not YAML list). Blank lines OK; spaces trimmed.
- Example:
  ```
  README.md
  .gitignore
  .github/pull_request_template.md
  ```

**Malformed or missing config**
- **Missing** → falls back to defaults: `["README.md", ".gitignore"]`.
- **Malformed** (e.g., YAML `- item`) → treated **verbatim** as a path; likely reported missing (no YAML parsing).

---

## Behavior when required files are missing
- Prints missing paths; exits **1**.
- In CI, the job stops on failure → **no CloudWatch logging** runs.

---

## How the AWS CLI log step works (CI)
After a successful validation (see workflows):
1. Ensure log group exists.
2. Create a stream named with UTC timestamp:
   ```bash
   echo "STREAM_NAME=$(date -u +%Y%m%dT%H%M%SZ)" >> "$GITHUB_ENV"
   ```
3. Join script outputs (`steps.file_check.outputs.missing_files_output` / `required_files_output`) into comma lists.
4. `put-log-events` sends **one message** to the stream.

**Included “enriched” message fields**
```
Workflow=<name>  SHA=<sha>  Actor=<actor>  RunID=<id>  Job=<job>
Repo=<owner/repo>  Branch=<ref_name>  Event=<event>
Missing_Files=<comma list>  Files_Found=<comma list>
```

> The script writes `GITHUB_OUTPUT` keys when available:  
> `required_files_output` (JSON array), `missing_files_output` (JSON array).

---

## Where to find logs (beta & prod)
- AWS Console ► **CloudWatch → Logs → Log groups**.
- **PRs (beta):** `LOG_GROUP_NAME_BETA` secret.  
- **Merges to main (prod):** `LOG_GROUP_NAME_PROD` secret.
- Streams are named by UTC timestamp (`YYYYMMDDTHHMMSSZ`).

---

## Test updated behavior

### Locally
- **Success:** add real paths to `.required-files.yml` that exist in the remote repo → exit `0`.
- **Defaults:** remove the file; ensure `README.md` & `.gitignore` exist remotely.
- **Failure:** include a non-existent path → exit `1`.

### In CI
- **PR →** `.github/workflows/on_pull_request.yml`: runs tests → validation → **beta** logging.
- **Push to `main` →** `.github/workflows/on_merge_request.yml`: runs tests → validation → **prod** logging.

---

## Test suite

### Run locally
```bash
python -m pip install --upgrade pip pytest requests
pytest -q
```

### What it covers (current)
- Script presence.
- Subprocess run expecting **0** when listed files resolve via GitHub API.

### Where to add new tests
- Extend `unit_test.py` or create `tests/`:
  - Defaults vs custom, exit codes.
  - Values written to `GITHUB_OUTPUT` (when set).

### How tests are triggered in CI
- Both workflows include a `tests` job (Python **3.13**) that runs **before** validation & logging on PRs and on pushes to `main`.
