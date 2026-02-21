"""
PDF processing module for extracting text and generating AI-powered summaries
Uses PDF-to-image conversion with Gemini vision as primary analysis method
"""
import logging
from typing import Optional, Dict, List
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF processing including text extraction and page-to-image conversion
    """
    
    @staticmethod
    def convert_pdf_to_images(file_path: str, max_pages: int = 10) -> List:
        """
        Convert PDF pages to PIL Images using PyMuPDF
        
        Args:
            file_path: Path to PDF file
            max_pages: Maximum number of pages to convert (default 10)
        
        Returns:
            List of PIL Image objects (one per page)
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io
            
            if not Path(file_path).exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            doc = fitz.open(file_path)
            images = []
            total_pages = len(doc)
            pages_to_convert = min(total_pages, max_pages)
            
            # Use lower DPI for large documents to keep payload manageable
            dpi = 150 if total_pages > 5 else 200
            
            for page_num in range(pages_to_convert):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
                logger.info(f"Converted page {page_num + 1}/{pages_to_convert} to image ({dpi} DPI)")
            
            if total_pages > max_pages:
                logger.warning(f"PDF has {total_pages} pages, only converting first {max_pages}")
            
            doc.close()
            
            if not images:
                raise ValueError("No pages could be converted from the PDF")
            
            logger.info(f"✓ Converted {len(images)} PDF pages to images")
            return images
        
        except ImportError:
            logger.error("PyMuPDF (fitz) library not installed. Install with: pip install PyMuPDF")
            raise
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise ValueError(f"Failed to convert PDF to images: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file (fallback method)
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text from PDF
        
        Raises:
            ValueError: If PDF cannot be processed
        """
        try:
            from PyPDF2 import PdfReader
            
            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # Extract text from PDF
            pdf_reader = PdfReader(file_path)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            logger.info(f"✓ Successfully extracted text from PDF ({len(text)} characters)")
            return text
        
        except ImportError:
            logger.error("PyPDF2 library not installed")
            raise
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf_binary(file_content: bytes) -> str:
        """
        Extract text from PDF file content (bytes)
        
        Args:
            file_content: PDF file content as bytes
        
        Returns:
            Extracted text from PDF
        
        Raises:
            ValueError: If PDF cannot be processed
        """
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            # Create BytesIO object from file content
            pdf_file = BytesIO(file_content)
            
            # Extract text from PDF
            pdf_reader = PdfReader(pdf_file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            logger.info(f"✓ Successfully extracted text from PDF ({len(text)} characters)")
            return text
        
        except ImportError:
            logger.error("PyPDF2 library not installed")
            raise
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")


class AIReportAnalyzer:
    """
    Uses Genkit to analyze lab reports and generate summaries with recommendations
    """
    
    def __init__(self):
        """Initialize the analyzer with Genkit manager"""
        self.genkit = None
        self._initialize_genkit()
    
    def _initialize_genkit(self):
        """Initialize Genkit manager"""
        try:
            from genkit_config import get_genkit_manager
            self.genkit = get_genkit_manager()
            logger.info("✓ AI analyzer initialized with Google AI")
        except Exception as e:
            logger.error(f"Failed to initialize AI analyzer: {e}")
            raise
    
    async def analyze_report(
        self,
        pdf_text: str = None,
        images: list = None,
        test_type: str = "laboratory",
        patient_name: Optional[str] = None
    ) -> Dict:
        """
        Analyze lab report using AI. Prefers image-based analysis, falls back to text.
        
        Args:
            pdf_text: Extracted text from PDF (fallback)
            images: List of PIL Image objects from PDF pages (preferred)
            test_type: Type of medical test
            patient_name: Optional patient name for context
        
        Returns:
            Dictionary containing analysis results
        """
        if not self.genkit:
            raise RuntimeError("AI analyzer not initialized")
        
        try:
            if images:
                # Primary: Use image-based analysis with Gemini vision
                logger.info(f"Using image-based analysis with {len(images)} page(s)")
                analysis = await self.genkit.generate_report_analysis_from_images(
                    images=images,
                    test_type=test_type
                )
            elif pdf_text:
                # Fallback: Use text-based analysis
                logger.info("Using text-based analysis (fallback)")
                max_chars = 8000
                if len(pdf_text) > max_chars:
                    logger.warning(f"PDF text truncated from {len(pdf_text)} to {max_chars} characters")
                    pdf_text = pdf_text[:max_chars] + "\n[... Text truncated for processing ...]"
                
                analysis = await self.genkit.generate_report_analysis(
                    pdf_text=pdf_text,
                    test_type=test_type
                )
            else:
                raise ValueError("Either images or pdf_text must be provided")
            
            # Ensure doctor recommendation is present
            if not analysis.get("doctor_recommendation"):
                analysis["doctor_recommendation"] = (
                    "Patient should visit their doctor for proper interpretation and guidance of these lab results."
                )
            
            logger.info("✓ Report analysis completed successfully")
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing report: {e}")
            raise
    
    async def generate_simple_summary(self, pdf_text: str) -> str:
        """
        Generate a simple text summary of the report
        
        Args:
            pdf_text: Extracted text from PDF
        
        Returns:
            Generated summary string
        """
        if not self.genkit:
            raise RuntimeError("AI analyzer not initialized")
        
        try:
            summary = await self.genkit.generate_summary(pdf_text)
            
            # Append doctor recommendation if not present
            if "doctor" not in summary.lower():
                summary += "\n\n**Recommendation**: Please visit your doctor for proper interpretation and guidance regarding these results."
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise


# Async wrapper for synchronous usage in FastAPI
class ReportProcessor:
    """
    Main processor that coordinates PDF extraction and AI analysis
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.ai_analyzer = AIReportAnalyzer()
    
    async def process_pdf_report(
        self,
        file_path: str,
        test_type: str = "laboratory",
        patient_name: Optional[str] = None
    ) -> Dict:
        """
        Complete pipeline: Convert PDF to images and generate AI analysis.
        Falls back to text extraction if image conversion fails.
        
        Args:
            file_path: Path to saved PDF file
            test_type: Type of medical test
            patient_name: Optional patient name
        
        Returns:
            Complete analysis result
        """
        try:
            # Primary: Convert PDF pages to images for vision analysis
            images = None
            pdf_text = None
            try:
                images = self.pdf_processor.convert_pdf_to_images(file_path)
                logger.info(f"Converted PDF to {len(images)} images for vision analysis")
            except Exception as img_err:
                logger.warning(f"Image conversion failed, falling back to text extraction: {img_err}")
                # Fallback: Extract text
                pdf_text = self.pdf_processor.extract_text_from_pdf(file_path)
            
            # Analyze with AI
            analysis = await self.ai_analyzer.analyze_report(
                pdf_text=pdf_text,
                images=images,
                test_type=test_type,
                patient_name=patient_name
            )
            
            pages = len(images) if images else (pdf_text.count("--- Page") if pdf_text else 0)
            
            return {
                "status": "success",
                "analysis": analysis,
                "method": "vision" if images else "text",
                "pages_processed": pages
            }
        
        except Exception as e:
            logger.error(f"Error processing PDF report: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process PDF report"
            }
    
    async def process_pdf_binary(
        self,
        file_content: bytes,
        test_type: str = "laboratory",
        patient_name: Optional[str] = None
    ) -> Dict:
        """
        Process PDF from binary content (useful for in-memory processing)
        
        Args:
            file_content: PDF file content as bytes
            test_type: Type of medical test
            patient_name: Optional patient name
        
        Returns:
            Complete analysis result
        """
        try:
            # Extract text from PDF bytes
            pdf_text = self.pdf_processor.extract_text_from_pdf_binary(file_content)
            
            # Analyze with AI
            analysis = await self.ai_analyzer.analyze_report(
                pdf_text=pdf_text,
                test_type=test_type,
                patient_name=patient_name
            )
            
            return {
                "status": "success",
                "analysis": analysis,
                "pdf_text_length": len(pdf_text),
                "pages_processed": pdf_text.count("--- Page")
            }
        
        except Exception as e:
            logger.error(f"Error processing PDF binary: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process PDF report"
            }


# Singleton instance for use across the app
_processor_instance: Optional[ReportProcessor] = None


def get_report_processor() -> ReportProcessor:
    """
    Get or create singleton instance of ReportProcessor
    
    Returns:
        ReportProcessor instance
    """
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = ReportProcessor()
    return _processor_instance

