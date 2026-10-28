"""Execute the complete notebook from a fresh kernel and validate saved outputs."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

folder = Path(__file__).resolve().parent
os.chdir(folder)
for variable, directory in [("MPLCONFIGDIR", "matplotlib"), ("IPYTHONDIR", "ipython")]:
    location = folder / ".local" / directory
    location.mkdir(parents=True, exist_ok=True)
    os.environ[variable] = str(location)
import nbformat
from nbclient import NotebookClient

notebook_path = folder / "movielens_recommender.ipynb"
notebook = nbformat.read(notebook_path, as_version=4)
for cell in notebook.cells:
    if cell.cell_type == "code":
        cell.outputs = []
        cell.execution_count = None

started = time.monotonic()
client = NotebookClient(notebook, timeout=3600, kernel_name="python3", resources={"metadata": {"path": str(folder)}}, allow_errors=False)
def report_cell(cell, cell_index, **kwargs):
    if cell.cell_type == "code":
        print(f"Executing cell {cell_index + 1}/{len(notebook.cells)}", flush=True)
client.on_cell_start = report_cell
client.execute()
nbformat.write(notebook, notebook_path)
code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
assert all(cell.execution_count is not None for cell in code_cells)
assert not any(output.output_type == "error" for cell in code_cells for output in cell.outputs)
evidence_path = folder / "validation.json"
evidence = json.loads(evidence_path.read_text())
evidence["execution"] = {"fresh_kernel": True, "executed_code_cells": len(code_cells), "saved_errors": 0, "wall_seconds": time.monotonic() - started, "notebook_sha256": hashlib.sha256(notebook_path.read_bytes()).hexdigest()}
evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
print(json.dumps({"project": evidence["project"], "execution": evidence["execution"]}, indent=2))
