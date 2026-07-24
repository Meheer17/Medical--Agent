"""
Validator to ensure all AI analysis fields are properly stored and retrieved
"""
import json
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class AIFieldValidator:
    """Validates AI analysis field mapping and storage"""
    
    REQUIRED_AI_FIELDS = {
        'ai_summary': str,
        'ai_key_findings': str,  # Should be JSON
        'ai_abnormal_values': str,  # Should be JSON
        'ai_clinical_significance': str,
        'ai_criticality': (str, type(None)),  # critical, medium, low
        'ai_doctor_recommendation': str,
        'ai_analysis_status': str,
        'ai_analysis_error': (str, type(None))
    }
    
    @staticmethod
    def validate_field_types(report_dict: Dict) -> Tuple[bool, list]:
        errors = []
        for field_name, expected_type in AIFieldValidator.REQUIRED_AI_FIELDS.items():
            if field_name not in report_dict:
                errors.append(f"Missing field: {field_name}")
                continue
            
            value = report_dict.get(field_name)
            if isinstance(expected_type, tuple):
                if value is not None and not isinstance(value, expected_type):
                    errors.append(f"Field {field_name} has wrong type. Expected {expected_type}, got {type(value)}")
            else:
                if value is not None and not isinstance(value, expected_type):
                    errors.append(f"Field {field_name} has wrong type. Expected {expected_type}, got {type(value)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_json_fields(report_dict: Dict) -> Tuple[bool, list]:
        errors = []
        json_fields = ['ai_key_findings', 'ai_abnormal_values']
        
        for field_name in json_fields:
            value = report_dict.get(field_name)
            if value and isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if not isinstance(parsed, list):
                        errors.append(f"Field {field_name} JSON should be an array, got {type(parsed)}")
                except json.JSONDecodeError:
                    errors.append(f"Field {field_name} is not valid JSON: {value[:100]}")
            elif value is None:
                logger.warning(f"Field {field_name} is None (expected for pending status)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_doctor_recommendation(report_dict: Dict) -> Tuple[bool, str]:
        recommendation = report_dict.get('ai_doctor_recommendation', '')
        if not recommendation:
            return False, "Doctor recommendation is empty"
        if "doctor" not in recommendation.lower() and "visit" not in recommendation.lower():
            return False, "Doctor recommendation should mention visiting a doctor"
        return True, "Doctor recommendation contains appropriate visit advice"
    
    @staticmethod
    def _get_val(obj, key):
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    @staticmethod
    def validate_report_record(db_report) -> Dict:
        get = lambda k: AIFieldValidator._get_val(db_report, k)
        report_dict = {
            'ai_summary': get('ai_summary'),
            'ai_key_findings': get('ai_key_findings'),
            'ai_abnormal_values': get('ai_abnormal_values'),
            'ai_clinical_significance': get('ai_clinical_significance'),
            'ai_criticality': get('ai_criticality'),
            'ai_doctor_recommendation': get('ai_doctor_recommendation'),
            'ai_analysis_status': get('ai_analysis_status'),
            'ai_analysis_error': get('ai_analysis_error')
        }
        
        type_valid, type_errors = AIFieldValidator.validate_field_types(report_dict)
        json_valid, json_errors = AIFieldValidator.validate_json_fields(report_dict)
        rec_valid, rec_message = AIFieldValidator.validate_doctor_recommendation(report_dict)
        
        all_errors = type_errors + json_errors
        
        result = {
            'is_valid': type_valid and json_valid and rec_valid,
            'type_validation': {'valid': type_valid, 'errors': type_errors},
            'json_validation': {'valid': json_valid, 'errors': json_errors},
            'doctor_recommendation_validation': {'valid': rec_valid, 'message': rec_message},
            'all_errors': all_errors,
            'summary': {
                'status': get('ai_analysis_status'),
                'has_summary': bool(get('ai_summary')),
                'has_key_findings': bool(get('ai_key_findings')),
                'has_abnormal_values': bool(get('ai_abnormal_values')),
                'has_clinical_significance': bool(get('ai_clinical_significance')),
                'criticality': get('ai_criticality'),
                'has_recommendation': bool(get('ai_doctor_recommendation')),
                'error_message': get('ai_analysis_error')
            }
        }
        
        return result

    @staticmethod
    def log_validation_result(report_id: int, validation_result: Dict) -> None:
        if validation_result['is_valid']:
            logger.info(f"✓ Report {report_id} validation passed")
        else:
            logger.warning(f"✗ Report {report_id} validation failed")
            for error in validation_result['all_errors']:
                logger.warning(f"  - {error}")

def validate_and_ensure_fields(db_report) -> bool:
    validation_result = AIFieldValidator.validate_report_record(db_report)
    report_id = AIFieldValidator._get_val(db_report, 'id')
    AIFieldValidator.log_validation_result(report_id, validation_result)
    return validation_result['is_valid']
