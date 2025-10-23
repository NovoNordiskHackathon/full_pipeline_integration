import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Project roots
ROOT_DIR = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT_DIR / "Full_pipeline (Copy)"
PTD_GEN_DIR = PIPELINE_DIR / "PTD_Gen"
CONFIG_DIR = PTD_GEN_DIR / "config"
OUTPUT_BASE = ROOT_DIR / "runs"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

# Import pipeline modules without modifying their logic
import sys
sys.path.insert(0, str(PTD_GEN_DIR))

from generate_ptd import run_schedule_grid_pipeline, generate_study_specific_forms_xlsx, replace_sheets_in_template, finalize_formatting  # type: ignore

app = Flask(__name__)
CORS(app)

# In-memory job registry (simple)
JOBS = {}


def _save_uploaded(file_storage, dest_folder: Path, filename: Optional[str] = None) -> Path:
    dest_folder.mkdir(parents=True, exist_ok=True)
    name = filename or file_storage.filename or "upload.bin"
    safe_name = os.path.basename(name)
    dest_path = dest_folder / safe_name
    file_storage.save(dest_path)
    return dest_path


@app.route("/status", methods=["GET"])
def status():
    job_id = request.args.get("job_id")
    if not job_id:
        # Provide a simple health/status payload
        return jsonify({
            "service": "ptd-backend",
            "status": "ok",
            "time": datetime.utcnow().isoformat() + "Z"
        })
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    return jsonify(job)


@app.route("/run_pipeline", methods=["POST"])
def run_pipeline():
    """
    Accepts multipart/form-data with:
      - protocol_json: file (JSON produced by protocol extractor)
      - ecrf_json: file (JSON produced by eCRF extractor)
      - template_xlsx: optional file (Excel template to inject sheets into)
      - mode: optional ("stream" | "surgery" | "default"), defaults to default path
      - fast: optional flag ("true"/"false")
    Returns JSON with job_id and download link when ready (synchronous run for simplicity).
    """
    job_id = str(uuid.uuid4())
    job_dir = OUTPUT_BASE / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    JOBS[job_id] = {
        "id": job_id,
        "state": "running",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    try:
        # Validate inputs
        if "protocol_json" not in request.files or "ecrf_json" not in request.files:
            return jsonify({"error": "protocol_json and ecrf_json files are required"}), 400

        protocol_path = _save_uploaded(request.files["protocol_json"], job_dir, "protocol.json")
        ecrf_path = _save_uploaded(request.files["ecrf_json"], job_dir, "ecrf.json")

        template_file = request.files.get("template_xlsx")
        template_path: Optional[Path] = None
        if template_file:
            template_path = _save_uploaded(template_file, job_dir, template_file.filename)

        # Options
        mode = (request.form.get("mode") or "default").strip().lower()
        fast = (request.form.get("fast") or "false").strip().lower() == "true"
        out_name = request.form.get("out") or "ptd_output.xlsx"
        out_path = job_dir / out_name

        # Run existing pipeline without changing its internal logic
        # 1) Produce schedule grid intermediates or file
        schedule_inputs = run_schedule_grid_pipeline(
            protocol_json=str(protocol_path),
            ecrf_json=str(ecrf_path),
            final_output_xlsx=str(job_dir / "schedule_grid.xlsx"),
            config_dir=str(CONFIG_DIR),
            for_stream=(mode in ("stream", "surgery")),
        )

        # 2) Generate study specific forms (skip only for stream mode)
        if mode != "stream":
            forms_xlsx = generate_study_specific_forms_xlsx(str(ecrf_path))

        # 3) Combine into template according to chosen mode
        if mode == "stream":
            # Stream both sheets into one workbook using XlsxWriter (via generate_ptd)
            # Reuse generate_schedule_grid_stream and rows writer by using the CLI main pieces isn't trivial here;
            # instead stick to the default path when template is provided to guarantee output.
            if not template_path:
                # Fallback: when no template provided, just return the schedule file that was built
                if isinstance(schedule_inputs, dict):
                    # When for_stream=True, a dict is returned; we cannot finalize without template
                    # Return a useful diagnostic and intermediates instead
                    JOBS[job_id]["state"] = "failed"
                    JOBS[job_id]["error"] = "stream mode requires template_xlsx to build final workbook"
                    return jsonify(JOBS[job_id]), 400
            # If a template is provided, choose surgery fast path to keep memory small
            mode = "surgery"

        if mode == "surgery":
            if not template_path:
                return jsonify({"error": "template_xlsx is required for surgery mode"}), 400
            from generate_ptd import prepare_study_specific_forms_rows, surgery_replace_sheets_inplace  # type: ignore
            # schedule_inputs must be dict from for_stream=True
            if not isinstance(schedule_inputs, dict):
                return jsonify({"error": "internal error: expected streaming schedule inputs"}), 500
            rows = prepare_study_specific_forms_rows(
                json_file_path=str(ecrf_path),
                config_path=str(CONFIG_DIR / "config_study_specific_forms.json"),
            )
            final_path = surgery_replace_sheets_inplace(
                template_xlsx=str(template_path),
                schedule_sheet_name="Schedule Grid",
                forms_sheet_name="Study Specific Forms",
                schedule_rows_path=schedule_inputs['visits_xlsx'],
                forms_rows_iter=iter(rows),
            )
            # Save as requested name
            Path(final_path).rename(out_path)
        else:
            # default path: replace sheets in a provided template
            if not template_path:
                return jsonify({"error": "template_xlsx is required when not using stream mode"}), 400
            final_path = replace_sheets_in_template(
                template_xlsx=str(template_path),
                schedule_xlsx=(schedule_inputs if isinstance(schedule_inputs, str) else str(job_dir / "schedule_grid.xlsx")),
                forms_xlsx=forms_xlsx,  # type: ignore[name-defined]
                out_xlsx=str(out_path),
                fast=fast,
            )
            if not fast:
                finalize_formatting(final_path)

        JOBS[job_id].update({
            "state": "completed",
            "output": str(out_path.relative_to(ROOT_DIR)),
            "download_url": f"/download?job_id={job_id}",
        })
        return jsonify(JOBS[job_id])

    except Exception as exc:  # noqa: BLE001 wide catch for API surface
        JOBS[job_id]["state"] = "failed"
        JOBS[job_id]["error"] = str(exc)
        return jsonify(JOBS[job_id]), 500


@app.route("/download", methods=["GET"])
def download():
    job_id = request.args.get("job_id")
    if not job_id or job_id not in JOBS:
        return jsonify({"error": "job not found"}), 404
    job = JOBS[job_id]
    if job.get("state") != "completed":
        return jsonify({"error": "job not completed"}), 400
    output_rel = job.get("output")
    if not output_rel:
        return jsonify({"error": "output missing"}), 404
    output_path = ROOT_DIR / output_rel
    if not output_path.exists():
        return jsonify({"error": "file missing"}), 404
    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
