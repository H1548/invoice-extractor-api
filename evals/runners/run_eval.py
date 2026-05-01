from evals.runners.metrics import EvalMetrics
from app.services.pipeline_service import Pipeline
import glob
import os
from pathlib import Path
import json 
from collections import defaultdict

base_dir = Path(__file__).resolve().parents[2]   # adjust if needed
labelled_dir = base_dir / 'evals'/ 'datasets'/'labelled'

evaluator = EvalMetrics()
pipeline = Pipeline()
results = defaultdict(list)

final_result = defaultdict(list)
invoices = list(labelled_dir.glob('*.png'))
ground_truths = list(labelled_dir.glob('*.json'))



for gt, invoice in zip(ground_truths, invoices):
    print(gt)
    with open(gt, "r", encoding="utf-8") as f:
        gt_schema = json.load(f)
    try:
        predicted_inv = pipeline.process_invoice(invoice)
        predicted_inv = predicted_inv['cannonical_output']
    except Exception as e:
        print(f"FAILED on invoice: {invoice}")
        print(predicted_inv)
        print(e)
        continue
    
    doc_result = evaluator.evaluate_document_level(predicted_inv, gt_schema)

    for field, value in doc_result["field_level"].items():
        results[field].append(value)

    for field, value in doc_result["needs_review"].items():
        results[field].append(value)


print(evaluator.aggregate_results(results))