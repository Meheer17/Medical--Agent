"""
Validator to ensure all AI analysis fields are properly stored and retrieved
"""
import json
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AIFieldValidator:
    """Validates AI analysis field mapping and storage"""
    
    # Required AI fields
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
        """
        Validate that all AI fields have correct types
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for field_name, expected_type in AIFieldValidator.REQUIRED_AI_FIELDS.items():
            if field_name not in report_dict:
                errors.append(f"Missing field: {field_name}")
                continue
            
            value = report_dict.get(field_name)
            if isinstance(expected_type, tuple):
                # Allow multiple types
                if value is not None and not isinstance(value, expected_type):
                    errors.append(f"Field {field_name} has wrong type. Expected {expected_type}, got {type(value)}")
            else:
                if value is not None and not isinstance(value, expected_type):
                    errors.append(f"Field {field_name} has wrong type. Expected {expected_type}, got {type(value)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_json_fields(report_dict: Dict) -> Tuple[bool, list]:
        """
        Validate that JSON fields are properly formatted
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
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
        """
        Validate that doctor recommendation includes visit advice
        
        Returns:
            Tuple of (is_valid, message)
        """
        recommendation = report_dict.get('ai_doctor_recommendation', '')
        
        if not recommendation:
            return False, "Doctor recommendation is empty"
        
        if "doctor" not in recommendation.lower() and "visit" not in recommendation.lower():
            return False, "Doctor recommendation should mention visiting a doctor"
        
        return True, "Doctor recommendation contains appropriate visit advice"
    
    @staticmethod
    def validate_report_record(db_report) -> Dict:
        """
        Comprehensive validation of a LabReport database record
        
        Args:
            db_report: LabReport model instance
        
        Returns:
            Dictionary with validation results
        """
        report_dict = {
            'ai_summary': db_report.ai_summary,
            'ai_key_findings': db_report.ai_key_findings,
            'ai_abnormal_values': db_report.ai_abnormal_values,
            'ai_clinical_significance': db_report.ai_clinical_significance,
            'ai_criticality': db_report.ai_criticality,
            'ai_doctor_recommendation': db_report.ai_doctor_recommendation,
            'ai_analysis_status': db_report.ai_analysis_status,
            'ai_analysis_error': db_report.ai_analysis_error
        }
        
        # Run validations
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
                'status': db_report.ai_analysis_status,
                'has_summary': bool(db_report.ai_summary),
                'has_key_findings': bool(db_report.ai_key_findings),
                'has_abnormal_values': bool(db_report.ai_abnormal_values),
                'has_clinical_significance': bool(db_report.ai_clinical_significance),
                'criticality': db_report.ai_criticality,
                'has_recommendation': bool(db_report.ai_doctor_recommendation),
                'error_message': db_report.ai_analysis_error
            }
        }
        
        return result
    
    @staticmethod
    def log_validation_result(report_id: int, validation_result: Dict) -> None:
        """
        Log validation results with appropriate level
        
        Args:
            report_id: ID of the report
            validation_result: Result from validate_report_record
        """
        if validation_result['is_valid']:
            logger.info(f"✓ Report {report_id} validation passed")
        else:
            logger.warning(f"✗ Report {report_id} validation failed")
            for error in validation_result['all_errors']:
                logger.warning(f"  - {error}")
        
        # Log summary
        summary = validation_result['summary']
        logger.debug(f"Report {report_id} summary: {summary}")


def validate_and_ensure_fields(db_report) -> bool:
    """
    Validate a report and log results
    
    Returns:
        True if valid, False otherwise
    """
    validation_result = AIFieldValidator.validate_report_record(db_report)
    AIFieldValidator.log_validation_result(db_report.id, validation_result)
    return validation_result['is_valid']
