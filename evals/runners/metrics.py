from decimal import Decimal
class EvalMetrics():
    def decimal_match(self, pred, gt, tolerance=Decimal("0.01")):
        
        if pred is None and gt is None: 
            return True
        elif pred is None or gt is None: 
            return False
        else: 
            return abs(Decimal(pred) - Decimal(gt)) <= tolerance
    
    def normalize_string(self, value):
        if value is None:
            return None
        return " ".join(value.strip().lower().split())

    def string_match(self, pred, gt):
        return self.normalize_string(pred) == self.normalize_string(gt)
    
    def date_match(self, pred, gt):
        if pred is None and gt is None:
            return True
        if pred is None or gt is None:
            return False
        return str(pred) == str(gt)

    def evaluate_top_level_fields(self,pred,gt):
        
        return {
            'vendor_name': self.string_match(pred.get('vendor_name'), gt.get('vendor_name')),
            'invoice_number': self.string_match(pred.get('invoice_number'), gt.get('invoice_number')),
            'invoice_date': self.date_match(pred.get('invoice_date'), gt.get('invoice_date')),
            'due_date': self.date_match(pred.get('due_date'), gt.get('due_date')),
            'total_amount': self.decimal_match(pred.get('total_amount'), gt.get('total_amount')),
            'sub_total': self.decimal_match(pred.get('sub_total'), gt.get('sub_total')),
            'tax_amount': self.decimal_match(pred.get('tax_amount'), gt.get('tax_amount')),
            'shipping_amount': self.decimal_match(pred.get('shipping_amount'), gt.get('shipping_amount')),
            'currency': self.string_match(pred.get('currency'), gt.get('currency')),
            'purchase_order_number': self.string_match(pred.get('purchase_order_number'), gt.get('purchase_order_number')),
            'bank_payment_details': self.string_match(pred.get('bank_payment_details'), gt.get('bank_payment_details')),
        }
    
    def evaluate_line_items(self, pred_items, gt_items):

        result = {
            "lineItems_counts_match": len(pred_items) == len(gt_items),
            "line_items_accuracy": None
            }

        temp_list = []

        for pred_item, gt_item in zip(pred_items, gt_items):
            temp_list.append(self.string_match(pred_item.get("description"), gt_item.get("description")))
            temp_list.append(self.decimal_match(pred_item.get("quantity"), gt_item.get("quantity")))
            temp_list.append(self.decimal_match(pred_item.get("unit_price"), gt_item.get("unit_price")))
            temp_list.append(self.decimal_match(pred_item.get("amount"), gt_item.get("amount")))

        if temp_list:
            result["line_items_accuracy"] = sum(temp_list) / len(temp_list)
        else:
            result["line_items_accuracy"] = 1.0 if len(pred_items) == len(gt_items) == 0 else 0.0

        return result
    def evaluate_review_flag(self, pred,gt):
        return {
            "needs_review": True if pred == gt else False
        }
    
    def evaluate_document_level(self, pred, gt):
        
        CRITICAL_FIELDS = [
        "vendor_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "total_amount",
        "currency"
        ]
        
        gt_values = gt["canonical_schema"]
        field_results = self.evaluate_top_level_fields(pred, gt_values)

        pred_items = pred.get("line_items",[])
        gt_items = gt_values.get("line_items",[])

        line_item_results = self.evaluate_line_items(pred_items, gt_items)

        combined_results = {**field_results, **line_item_results}

        review_score = self.evaluate_review_flag(pred['needs_review'], gt["should_review"])

        critical_success = all(field_results[field] for field in CRITICAL_FIELDS)
        success = all(value for key, value in combined_results.items() if key != "line_items_accuracy") and (
        combined_results["line_items_accuracy"] == 1.0
        )


        return {
            "field_level": combined_results, 
            "critical_fields": critical_success, 
            "success": success, 
            "needs_review": review_score
        }
    
    def aggregate_results(self,results): 
        aggregated = {}

        for field, values in results.items():
            if values: 
                aggregated[field] = sum(values) / len(values)
            else: 
                aggregated[field] = None
        
        return aggregated

        