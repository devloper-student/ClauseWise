import os
import json
import re
from typing import List, Dict, Any
import spacy
import streamlit as st
import requests

class AIEngine:
    """AI Engine for legal document analysis using IBM Granite and spaCy"""
    
    def __init__(self):
        # Initialize IBM Granite via direct API access
        self.granite_api_url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
        self.granite_api_key = os.getenv("WATSONX_API_KEY")
        self.granite_project_id = os.getenv("WATSONX_PROJECT_ID", "default-project")
        self.model_id = "ibm/granite-3-8b-instruct"
        
        # Load spaCy model (download if not available)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            st.error("spaCy English model not found. Please install it with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract individual clauses from legal document text
        
        Args:
            text: Raw document text
            
        Returns:
            List of dictionaries containing clause information
        """
        if not self.nlp:
            return self._simple_clause_extraction(text)
        
        clauses = []
        
        # Split text into sentences using spaCy
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
        
        # Group sentences into logical clauses based on legal patterns
        current_clause = ""
        clause_id = 1
        
        for sentence in sentences:
            # Check if this sentence starts a new clause
            if self._is_clause_start(sentence):
                if current_clause.strip():
                    clauses.append({
                        'id': clause_id,
                        'text': current_clause.strip(),
                        'start_sentence': sentence[:100] + "..." if len(sentence) > 100 else sentence
                    })
                    clause_id += 1
                current_clause = sentence
            else:
                current_clause += " " + sentence
        
        # Add the last clause
        if current_clause.strip():
            clauses.append({
                'id': clause_id,
                'text': current_clause.strip(),
                'start_sentence': current_clause[:100] + "..." if len(current_clause) > 100 else current_clause[:100]
            })
        
        return clauses
    
    def _simple_clause_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Simple clause extraction fallback when spaCy is not available"""
        # Split by common legal section indicators
        patterns = [
            r'\n\s*\d+\.\s+',  # Numbered sections
            r'\n\s*\(\w\)\s+',  # Lettered subsections
            r'\n\s*[A-Z][A-Z\s]+:',  # All caps headers
            r'\n\s*WHEREAS\s+',  # Whereas clauses
            r'\n\s*NOW THEREFORE\s+',  # Therefore clauses
        ]
        
        sections = [text]
        for pattern in patterns:
            new_sections = []
            for section in sections:
                new_sections.extend(re.split(pattern, section))
            sections = [s.strip() for s in new_sections if s.strip()]
        
        clauses = []
        for i, section in enumerate(sections):
            if len(section) > 50:  # Only include substantial sections
                clauses.append({
                    'id': i + 1,
                    'text': section,
                    'start_sentence': section[:100] + "..." if len(section) > 100 else section
                })
        
        return clauses
    
    def _is_clause_start(self, sentence: str) -> bool:
        """Determine if a sentence likely starts a new legal clause"""
        clause_indicators = [
            r'^\d+\.',  # Numbered clauses
            r'^\([a-z]\)',  # Lettered subclauses
            r'^WHEREAS',  # Whereas clauses
            r'^NOW THEREFORE',  # Therefore clauses
            r'^IN WITNESS WHEREOF',  # Signature clauses
            r'^[A-Z][A-Z\s]+:',  # All caps headers
        ]
        
        for pattern in clause_indicators:
            if re.match(pattern, sentence.strip(), re.IGNORECASE):
                return True
        
        return False
    
    def classify_clauses(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify clauses into legal categories and provide simplified summaries
        
        Args:
            clauses: List of extracted clauses
            
        Returns:
            List of clauses with classification and summaries
        """
        classified_clauses = []
        
        for clause in clauses:
            try:
                # Get classification and summary from OpenAI
                classification_result = self._classify_single_clause(clause['text'])
                
                clause.update({
                    'category': classification_result.get('category', 'General'),
                    'simplified_text': classification_result.get('simplified_text', 'Unable to simplify this clause.'),
                    'risk_level': classification_result.get('risk_level', 'low'),
                    'key_terms': classification_result.get('key_terms', []),
                    'concerns': classification_result.get('concerns', [])
                })
                
                classified_clauses.append(clause)
                
            except Exception as e:
                st.warning(f"Error classifying clause {clause['id']}: {str(e)}")
                # Add fallback classification
                clause.update({
                    'category': 'General',
                    'simplified_text': 'Unable to analyze this clause due to processing error.',
                    'risk_level': 'medium',
                    'key_terms': [],
                    'concerns': ['Analysis error occurred']
                })
                classified_clauses.append(clause)
        
        return classified_clauses
    
    def _classify_single_clause(self, clause_text: str) -> Dict[str, Any]:
        """Classify a single clause using IBM Granite"""
        prompt = f"""You are a legal expert assistant. Analyze the following legal clause and provide:
1. Category classification (choose from: Liability, Indemnity, Confidentiality, Termination, Payment, Intellectual Property, Dispute Resolution, Force Majeure, Governing Law, General)
2. Plain English summary (2-3 sentences max)  
3. Risk level (low, medium, high)
4. Key terms mentioned
5. Potential concerns or red flags

Legal clause to analyze:
{clause_text}

Respond in JSON format with keys: category, simplified_text, risk_level, key_terms (array), concerns (array)"""
        
        try:
            # Call IBM Granite via watsonx.ai API
            if self.granite_api_key:
                response = self._call_granite_api(prompt)
                if response:
                    return response
            
            # Fallback to keyword-based classification
            return self._fallback_classification(clause_text)
            
        except Exception as e:
            # Fallback classification using keyword matching
            return self._fallback_classification(clause_text)
            
    def _call_granite_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to IBM Granite model"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.granite_api_key}"
        }
        
        payload = {
            "model_id": self.model_id,
            "inputs": [prompt],
            "parameters": {
                "temperature": 0.3,
                "max_new_tokens": 500,
                "top_p": 1.0
            },
            "project_id": self.granite_project_id
        }
        
        try:
            response = requests.post(self.granite_api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result_data = response.json()
                
                if "results" in result_data and len(result_data["results"]) > 0:
                    generated_text = result_data["results"][0]["generated_text"]
                    
                    # Try to parse as JSON
                    try:
                        result = json.loads(generated_text)
                        
                        # Validate and sanitize the response
                        return {
                            'category': result.get('category', 'General'),
                            'simplified_text': result.get('simplified_text', 'Unable to simplify this clause.'),
                            'risk_level': result.get('risk_level', 'low').lower(),
                            'key_terms': result.get('key_terms', [])[:10],
                            'concerns': result.get('concerns', [])[:5]
                        }
                    except json.JSONDecodeError:
                        # If not valid JSON, return fallback
                        return None
            
            return None
            
        except Exception as e:
            st.warning(f"IBM Granite API error: {str(e)}")
            return None
    
    def _fallback_classification(self, clause_text: str) -> Dict[str, Any]:
        """Fallback classification using keyword matching"""
        text_lower = clause_text.lower()
        
        # Category classification based on keywords
        if any(term in text_lower for term in ['liable', 'liability', 'damages', 'responsible']):
            category = 'Liability'
            risk_level = 'high'
        elif any(term in text_lower for term in ['indemnify', 'indemnification', 'hold harmless']):
            category = 'Indemnity'
            risk_level = 'high'
        elif any(term in text_lower for term in ['confidential', 'proprietary', 'non-disclosure']):
            category = 'Confidentiality'
            risk_level = 'medium'
        elif any(term in text_lower for term in ['terminate', 'termination', 'end', 'expire']):
            category = 'Termination'
            risk_level = 'medium'
        elif any(term in text_lower for term in ['payment', 'pay', 'fee', 'cost', 'price']):
            category = 'Payment'
            risk_level = 'medium'
        else:
            category = 'General'
            risk_level = 'low'
        
        return {
            'category': category,
            'simplified_text': f'This is a {category.lower()} clause. Please review the original text for specific details.',
            'risk_level': risk_level,
            'key_terms': [],
            'concerns': ['Automated analysis - manual review recommended']
        }
    
    def analyze_document_completeness(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall document completeness and missing important clauses"""
        categories_found = set(clause.get('category', 'General') for clause in clauses)
        
        essential_categories = [
            'Liability', 'Termination', 'Payment', 'Confidentiality',
            'Dispute Resolution', 'Governing Law'
        ]
        
        missing_categories = [cat for cat in essential_categories if cat not in categories_found]
        
        return {
            'categories_found': list(categories_found),
            'missing_categories': missing_categories,
            'completeness_score': (len(essential_categories) - len(missing_categories)) / len(essential_categories) * 100
        }
