"""
Configurable Genkit setup with Google AI integration
Handles LLM configuration and model initialization
"""
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuration for different LLM providers
class LLMConfig:
    """Base configuration for LLM providers"""
    def __init__(self, provider: str, **kwargs):
        self.provider = provider
        self.config = kwargs


class GoogleAIConfig(LLMConfig):
    """Google AI configuration"""
    def __init__(self, api_key: str):
        super().__init__(
            provider="google",
            api_key=api_key
        )
        self.api_key = api_key


# COMMENTED OUT - Ollama configuration
# class OllamaConfig(LLMConfig):
#     """Ollama configuration for local LLM"""
#     def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama2"):
#         super().__init__(
#             provider="ollama",
#             base_url=base_url,
#             model_name=model_name
#         )
#         self.base_url = base_url
#         self.model_name = model_name


class GenkitManager:
    """
    Manages Genkit initialization and model interactions
    Supports configurable LLM providers
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize Genkit manager with specified configuration
        
        Args:
            config: LLMConfig instance (GoogleAIConfig, OllamaConfig, etc.)
        """
        self.config = config
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the LLM based on configuration"""
        if self.config.provider == "google":
            self._initialize_google_ai()
        # COMMENTED OUT - Ollama initialization
        # elif self.config.provider == "ollama":
        #     self._initialize_ollama()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def _initialize_google_ai(self):
        """Initialize Google AI with Genkit"""
        try:
            import google.generativeai as genai
            from google.generativeai import GenerativeModel
            
            genai.configure(api_key=self.config.api_key)
            
            # Initialize the model
            self.model = GenerativeModel('gemini-2.0-flash')
            logger.info("✓ Google AI initialized successfully with gemini-2.0-flash")
        except ImportError as e:
            logger.error(f"Google AI library not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google AI: {e}")
            raise
    
    # COMMENTED OUT - Ollama initialization
    # def _initialize_ollama(self):
    #     """Initialize Ollama LLM"""
    #     try:
    #         import ollama
    #         
    #         # Test connection
    #         response = ollama.list()
    #         logger.info(f"✓ Ollama initialized successfully at {self.config.base_url}")
    #         logger.info(f"Available models: {response}")
    #     except ImportError as e:
    #         logger.error(f"Ollama library not installed: {e}")
    #         raise
    #     except Exception as e:
    #         logger.error(f"Failed to connect to Ollama: {e}")
    #         raise
    
    async def generate_summary(self, text: str, context: Optional[dict] = None) -> str:
        """
        Generate summary of medical report text
        
        Args:
            text: The report text to summarize
            context: Optional context dict (e.g., patient info, test type)
        
        Returns:
            Generated summary string
        """
        if not self.model:
            raise RuntimeError("LLM model not initialized")
        
        prompt = self._build_summary_prompt(text, context)
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            logger.info("✓ Summary generated successfully")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def _build_summary_prompt(self, text: str, context: Optional[dict] = None) -> str:
        """
        Build the prompt for summary generation
        
        Args:
            text: Report text
            context: Optional context information
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a medical report analyzer. Please analyze the following lab report and provide:

1. **SUMMARY**: A concise summary of the key findings and results (2-3 sentences max)
2. **KEY FINDINGS**: 3-4 bullet points of the most important results
3. **ABNORMAL VALUES**: List any values outside normal range
4. **CLINICAL SIGNIFICANCE**: Brief explanation of what these results mean
5. **RECOMMENDATION**: Always include a recommendation that the patient should visit their doctor for proper interpretation and guidance

---
LAB REPORT:
{text}
---

Please provide a clear, professional analysis suitable for a patient to understand."""
        
        return prompt
    
    async def generate_report_analysis_from_images(self, images: list, test_type: str = "lab") -> dict:
        """
        Generate comprehensive analysis of lab report from page images.
        Returns all analysis data including criticality in a single AI call.
        
        Args:
            images: List of PIL Image objects (one per page)
            test_type: Type of test (lab, pathology, etc.)
        
        Returns:
            Dictionary with analysis results including criticality
        """
        if not self.model:
            raise RuntimeError("LLM model not initialized")
        
        analysis_prompt = f"""You are an expert medical report analyzer. Analyze this {test_type} report images and provide ALL of the following structured output in a SINGLE response.

Provide analysis in this exact format (use | as delimiter):

SUMMARY|Your concise summary here
KEY_FINDINGS|Finding 1 | Finding 2 | Finding 3
ABNORMAL_VALUES|Value 1 (abnormal) | Value 2 (abnormal)
CLINICAL_SIGNIFICANCE|What these results indicate
CRITICALITY|critical OR medium OR low
DOCTOR_RECOMMENDATION|Patient should visit their doctor to discuss these results and receive professional medical guidance

For CRITICALITY, assess the overall urgency of the results:
- "critical" = Life-threatening or severely abnormal values requiring immediate medical attention
- "medium" = Moderately abnormal values that need medical follow-up soon
- "low" = Normal or mildly abnormal values with no immediate concern

Remember to ALWAYS recommend that the patient visits a doctor for proper interpretation.
Return ALL fields above in a SINGLE response."""
        
        try:
            # Build content list: prompt + all page images
            content = [analysis_prompt] + images
            response = self.model.generate_content(content)
            analysis_text = response.text
            
            # Parse the response
            result = self._parse_analysis_response(analysis_text)
            logger.info("✓ Report analysis generated successfully from images")
            return result
        except Exception as e:
            logger.error(f"Error generating report analysis from images: {e}")
            raise

    async def generate_report_analysis(self, pdf_text: str, test_type: str = "lab") -> dict:
        """
        Generate comprehensive analysis of lab report from text (fallback)
        
        Args:
            pdf_text: Extracted text from PDF
            test_type: Type of test (lab, pathology, etc.)
        
        Returns:
            Dictionary with analysis results
        """
        if not self.model:
            raise RuntimeError("LLM model not initialized")
        
        analysis_prompt = f"""You are an expert medical report analyzer. Analyze this {test_type} report and provide ALL of the following structured output in a SINGLE response.

LAB REPORT TEXT:
{pdf_text}

Provide analysis in this exact format (use | as delimiter):

SUMMARY|Your concise summary here
KEY_FINDINGS|Finding 1 | Finding 2 | Finding 3
ABNORMAL_VALUES|Value 1 (abnormal) | Value 2 (abnormal)
CLINICAL_SIGNIFICANCE|What these results indicate
CRITICALITY|critical OR medium OR low
DOCTOR_RECOMMENDATION|Patient should visit their doctor to discuss these results and receive professional medical guidance

For CRITICALITY, assess the overall urgency of the results:
- "critical" = Life-threatening or severely abnormal values requiring immediate medical attention
- "medium" = Moderately abnormal values that need medical follow-up soon
- "low" = Normal or mildly abnormal values with no immediate concern

Remember to ALWAYS recommend that the patient visits a doctor for proper interpretation.
Return ALL fields above in a SINGLE response."""
        
        try:
            response = self.model.generate_content(analysis_prompt)
            analysis_text = response.text
            
            # Parse the response
            result = self._parse_analysis_response(analysis_text)
            logger.info("✓ Report analysis generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating report analysis: {e}")
            raise
    
    def _parse_analysis_response(self, response_text: str) -> dict:
        """
        Parse the structured response from the model
        
        Args:
            response_text: Model response text
        
        Returns:
            Parsed analysis dictionary
        """
        analysis = {
            "summary": "",
            "key_findings": [],
            "abnormal_values": [],
            "clinical_significance": "",
            "criticality": "low",
            "doctor_recommendation": "Patient should visit their doctor for proper interpretation and guidance of these lab results."
        }
        
        try:
            lines = response_text.split('\n')
            for line in lines:
                if '|' in line:
                    parts = line.split('|')
                    key = parts[0].strip().lower()
                    value = '|'.join(parts[1:]).strip() if len(parts) > 1 else ""
                    
                    if key == "summary":
                        analysis["summary"] = value
                    elif key == "key_findings":
                        analysis["key_findings"] = [f.strip() for f in value.split('|') if f.strip()]
                    elif key == "abnormal_values":
                        analysis["abnormal_values"] = [v.strip() for v in value.split('|') if v.strip()]
                    elif key == "clinical_significance":
                        analysis["clinical_significance"] = value
                    elif key == "criticality":
                        criticality_val = value.strip().lower()
                        if criticality_val in ("critical", "medium", "low"):
                            analysis["criticality"] = criticality_val
                        else:
                            logger.warning(f"Unknown criticality value: {criticality_val}, defaulting to 'low'")
                            analysis["criticality"] = "low"
                    elif key == "doctor_recommendation":
                        analysis["doctor_recommendation"] = value if value else analysis["doctor_recommendation"]
        except Exception as e:
            logger.warning(f"Could not parse structured response, returning raw text: {e}")
            analysis["summary"] = response_text
        
        # Ensure doctor recommendation is always present
        if not analysis["doctor_recommendation"]:
            analysis["doctor_recommendation"] = "Patient should visit their doctor for proper interpretation and guidance of these lab results."
        
        return analysis


def get_genkit_manager() -> GenkitManager:
    """
    Factory function to create configured Genkit manager
    
    Returns:
        Initialized GenkitManager instance
    """
    api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Google AI API key not configured. "
            "Set GOOGLE_AI_API_KEY or GENAI_API_KEY environment variable"
        )
    
    config = GoogleAIConfig(api_key=api_key)
    return GenkitManager(config)


# Example usage for testing
# COMMENTED OUT - Ollama example
# def get_genkit_manager_ollama() -> GenkitManager:
#     """
#     Factory function to create Ollama-based Genkit manager
#     Uncomment when Ollama is desired
#     
#     Returns:
#         Initialized GenkitManager instance with Ollama
#     """
#     base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#     model_name = os.getenv("OLLAMA_MODEL", "llama2")
#     config = OllamaConfig(base_url=base_url, model_name=model_name)
#     return GenkitManager(config)

