#!/usr/bin/env python3
"""
Quick verification script to check AI field mapping and storage
Run this after uploading a report to verify all fields are properly stored
"""

import json
import logging
from datetime import datetime
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_report_fields(report_id: int) -> bool:
    """
    Verify that all AI fields are properly stored for a report
    
    Args:
        report_id: ID of the report to verify
    
    Returns:
        True if all fields are properly stored
    """
    try:
        from database import SessionLocal
        from models import LabReport
        from ai_field_validator import AIFieldValidator
        
        db = SessionLocal()
        report = db.query(LabReport).filter(LabReport.id == report_id).first()
        
        if not report:
            logger.error(f"Report {report_id} not found")
            return False
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Verifying Report {report_id}")
        logger.info(f"{'='*60}")
        
        # Check basic fields
        logger.info(f"File: {report.file_name}")
        logger.info(f"Status: {report.ai_analysis_status}")
        logger.info(f"Created: {report.created_at}")
        
        if report.ai_analysis_status == "pending":
            logger.warning("⏳ Report still processing (status=pending)")
            return False
        
        if report.ai_analysis_status == "failed":
            logger.error(f"❌ Report processing failed: {report.ai_analysis_error}")
            return False
        
        # Run comprehensive validation
        validation_result = AIFieldValidator.validate_report_record(report)
        
        logger.info(f"\n{'─'*60}")
        logger.info("Field Validation Results:")
        logger.info(f"{'─'*60}")
        
        # Type validation
        if validation_result['type_validation']['valid']:
            logger.info("✓ Type validation: PASSED")
        else:
            logger.error("✗ Type validation: FAILED")
            for error in validation_result['type_validation']['errors']:
                logger.error(f"  - {error}")
        
        # JSON validation
        if validation_result['json_validation']['valid']:
            logger.info("✓ JSON validation: PASSED")
        else:
            logger.error("✗ JSON validation: FAILED")
            for error in validation_result['json_validation']['errors']:
                logger.error(f"  - {error}")
        
        # Doctor recommendation validation
        if validation_result['doctor_recommendation_validation']['valid']:
            logger.info("✓ Doctor recommendation: PASSED")
        else:
            logger.error(f"✗ Doctor recommendation: {validation_result['doctor_recommendation_validation']['message']}")
        
        # Summary
        logger.info(f"\n{'─'*60}")
        logger.info("Field Summary:")
        logger.info(f"{'─'*60}")
        summary = validation_result['summary']
        logger.info(f"Status: {summary['status']}")
        logger.info(f"Summary present: {'✓' if summary['has_summary'] else '✗'}")
        logger.info(f"Key findings present: {'✓' if summary['has_key_findings'] else '✗'}")
        logger.info(f"Abnormal values present: {'✓' if summary['has_abnormal_values'] else '✗'}")
        logger.info(f"Clinical significance present: {'✓' if summary['has_clinical_significance'] else '✗'}")
        logger.info(f"Doctor recommendation present: {'✓' if summary['has_recommendation'] else '✗'}")
        
        if summary['error_message']:
            logger.error(f"Error message: {summary['error_message']}")
        
        # Detailed field display
        logger.info(f"\n{'─'*60}")
        logger.info("Detailed Field Contents:")
        logger.info(f"{'─'*60}")
        
        if report.ai_summary:
            logger.info(f"\n📝 Summary ({len(report.ai_summary)} chars):")
            logger.info(f"   {report.ai_summary[:200]}..." if len(report.ai_summary) > 200 else f"   {report.ai_summary}")
        
        if report.ai_key_findings:
            try:
                findings = json.loads(report.ai_key_findings)
                logger.info(f"\n🔍 Key Findings ({len(findings)} items):")
                for finding in findings[:5]:  # Show first 5
                    logger.info(f"   - {finding}")
                if len(findings) > 5:
                    logger.info(f"   ... and {len(findings) - 5} more")
            except json.JSONDecodeError as e:
                logger.error(f"   ✗ Invalid JSON: {e}")
        
        if report.ai_abnormal_values:
            try:
                values = json.loads(report.ai_abnormal_values)
                logger.info(f"\n⚠️  Abnormal Values ({len(values)} items):")
                for value in values[:5]:  # Show first 5
                    logger.info(f"   - {value}")
                if len(values) > 5:
                    logger.info(f"   ... and {len(values) - 5} more")
            except json.JSONDecodeError as e:
                logger.error(f"   ✗ Invalid JSON: {e}")
        
        if report.ai_clinical_significance:
            logger.info(f"\n📊 Clinical Significance ({len(report.ai_clinical_significance)} chars):")
            logger.info(f"   {report.ai_clinical_significance[:200]}..." if len(report.ai_clinical_significance) > 200 else f"   {report.ai_clinical_significance}")
        
        if report.ai_doctor_recommendation:
            logger.info(f"\n👨‍⚕️  Doctor Recommendation:")
            logger.info(f"   {report.ai_doctor_recommendation}")
        
        # Final result
        logger.info(f"\n{'='*60}")
        if validation_result['is_valid']:
            logger.info("✅ ALL VALIDATIONS PASSED")
            logger.info(f"{'='*60}\n")
            return True
        else:
            logger.error("❌ VALIDATION ISSUES FOUND")
            logger.error(f"Issues: {', '.join(validation_result['all_errors'])}")
            logger.info(f"{'='*60}\n")
            return False
        
        db.close()
    
    except Exception as e:
        logger.error(f"Error during verification: {e}", exc_info=True)
        return False


def list_all_reports() -> List[Dict]:
    """
    List all reports with their AI analysis status
    
    Returns:
        List of report info dicts
    """
    try:
        from database import SessionLocal
        from models import LabReport
        
        db = SessionLocal()
        reports = db.query(LabReport).all()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"All Lab Reports ({len(reports)} total)")
        logger.info(f"{'='*80}")
        logger.info(f"{'ID':<5} {'Status':<12} {'File':<25} {'Summary':<8} {'Findings':<8} {'Error':<20}")
        logger.info(f"{'-'*80}")
        
        result = []
        for report in reports:
            has_summary = "✓" if report.ai_summary else "✗"
            has_findings = "✓" if report.ai_key_findings else "✗"
            error = (report.ai_analysis_error[:17] + "...") if report.ai_analysis_error and len(report.ai_analysis_error) > 20 else report.ai_analysis_error or ""
            
            logger.info(f"{report.id:<5} {report.ai_analysis_status:<12} {report.file_name:<25} {has_summary:<8} {has_findings:<8} {error:<20}")
            
            result.append({
                'id': report.id,
                'status': report.ai_analysis_status,
                'file': report.file_name,
                'has_summary': bool(report.ai_summary),
                'has_findings': bool(report.ai_key_findings),
                'error': report.ai_analysis_error
            })
        
        logger.info(f"{'='*80}\n")
        db.close()
        return result
    
    except Exception as e:
        logger.error(f"Error listing reports: {e}", exc_info=True)
        return []


def check_pending_reports() -> int:
    """
    Check for reports still in pending status (not yet processed)
    
    Returns:
        Number of pending reports
    """
    try:
        from database import SessionLocal
        from models import LabReport
        
        db = SessionLocal()
        pending = db.query(LabReport).filter(
            LabReport.ai_analysis_status == "pending"
        ).count()
        
        if pending > 0:
            logger.warning(f"⏳ {pending} report(s) still processing...")
        else:
            logger.info("✓ No pending reports")
        
        db.close()
        return pending
    
    except Exception as e:
        logger.error(f"Error checking pending reports: {e}")
        return -1


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python verify_ai_fields.py <report_id>  - Verify specific report")
        print("  python verify_ai_fields.py list         - List all reports")
        print("  python verify_ai_fields.py check        - Check for pending reports")
        print("\nExample:")
        print("  python verify_ai_fields.py 1            - Verify report with ID=1")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_all_reports()
    elif command == "check":
        pending = check_pending_reports()
        sys.exit(0 if pending == 0 else 1)
    else:
        try:
            report_id = int(command)
            is_valid = verify_report_fields(report_id)
            sys.exit(0 if is_valid else 1)
        except ValueError:
            print(f"Invalid report ID: {command}")
            sys.exit(1)
