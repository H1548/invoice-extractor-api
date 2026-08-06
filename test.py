from app.services.pipeline_service import Pipeline

pipeline = Pipeline()

output = pipeline.process_invoice("invoice_001.png")

adj_output = output["cannonical_output"]



print(adj_output["vendor_name"])