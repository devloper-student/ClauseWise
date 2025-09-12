from typing import List, Dict, Any
import re

class RiskEngine:
    """Risk analysis engine for legal documents"""
    
    def __init__(self):
        self.risk_patterns = self._initialize_risk_patterns()
        self.essential_clauses = self._initialize_essential_clauses()
    
    def _initialize_risk_patterns(self) -> Dict[str, List[str]]:
        """Initialize risk detection patterns"""
        return {
            'high_risk_terms': [
                r'unlimited liability',
                r'no limitation of liability',
                r'gross negligence',
                r'willful misconduct',
                r'liquidated damages',
                r'punitive damages',
                r'consequential damages',
                r'personal guarantee',
                r'joint and several',
                r'automatic renewal',
                r'perpetual license',
                r'irrevocable'
            ],
            'medium_risk_terms': [
                r'material breach',
                r'immediate termination',
                r'sole discretion',
                r'as is basis',
                r'no warranty',
                r'time is of the essence',
                r'force majeure',
                r'change in control',
                r'non-compete',
                r'exclusive rights'
            ],
            'concerning_phrases': [
                r'in perpetuity',
                r'without notice',
                r'at any time',
                r'sole and absolute discretion',
                r'waive all rights',
                r'release all claims',
                r'hold harmless from all',
                r'indemnify against all'
            ]
        }
    
    def _initialize_essential_clauses(self) -> Dict[str, Dict[str, Any]]:
        """Initialize essential clause requirements"""
        return {
            'Liability': {
                'required': True,
                'risk_level': 'high',
                'description': 'Defines responsibility for damages and losses'
            },
            'Termination': {
                'required': True,
                'risk_level': 'medium',
                'description': 'Specifies how and when the agreement can end'
            },
            'Confidentiality': {
                'required': True,
                'risk_level': 'medium',
                'description': 'Protects sensitive information'
            },
            'Payment': {
                'required': True,
                'risk_level': 'medium',
                'description': 'Details payment terms and conditions'
            },
            'Dispute Resolution': {
                'required': True,
                'risk_level': 'medium',
                'description': 'Outlines how disputes will be resolved'
            },
            'Governing Law': {
                'required': True,
                'risk_level': 'low',
                'description': 'Specifies which jurisdiction\'s laws apply'
            },
            'Intellectual Property': {
                'required': False,
                'risk_level': 'medium',
                'description': 'Defines ownership and use of IP'
            },
            'Force Majeure': {
                'required': False,
                'risk_level': 'low',
                'description': 'Addresses unforeseeable circumstances'
            }
        }
    
    def analyze_risks(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive risk analysis on document clauses
        
        Args:
            clauses: List of classified clauses
            
        Returns:
            Dictionary containing risk analysis results
        """
        risk_analysis = {
            'overall_risk_score': 0,
            'risk_breakdown': {'high': 0, 'medium': 0, 'low': 0},
            'missing_clauses': [],
            'high_risk_clauses': [],
            'concerning_terms': [],
            'recommendations': [],
            'completeness_score': 0
        }
        
        # Analyze individual clauses
        categories_found = set()
        total_risk_score = 0
        
        for clause in clauses:
            category = clause.get('category', 'General')
            categories_found.add(category)
            
            # Calculate clause-specific risks
            clause_risks = self._analyze_clause_risks(clause)
            
            # Update risk breakdown
            risk_level = clause.get('risk_level', 'low')
            risk_analysis['risk_breakdown'][risk_level] += 1
            
            # Add high-risk clauses to list
            if risk_level == 'high':
                risk_analysis['high_risk_clauses'].append({
                    'id': clause['id'],
                    'category': category,
                    'text_preview': clause['text'][:200] + "..." if len(clause['text']) > 200 else clause['text'],
                    'risks': clause_risks['identified_risks'],
                    'concerns': clause.get('concerns', [])
                })
            
            # Add concerning terms
            risk_analysis['concerning_terms'].extend(clause_risks['concerning_terms'])
            
            # Calculate risk score contribution
            risk_multiplier = {'high': 3, 'medium': 2, 'low': 1}
            total_risk_score += risk_multiplier[risk_level]
        
        # Check for missing essential clauses
        for category, requirements in self.essential_clauses.items():
            if requirements['required'] and category not in categories_found:
                risk_analysis['missing_clauses'].append({
                    'category': category,
                    'risk_level': requirements['risk_level'],
                    'description': requirements['description']
                })
        
        # Calculate overall scores
        max_possible_score = len(clauses) * 3  # Maximum if all clauses were high risk
        risk_analysis['overall_risk_score'] = min(100, (total_risk_score / max_possible_score * 100)) if max_possible_score > 0 else 0
        
        # Calculate completeness score
        required_clauses = [cat for cat, req in self.essential_clauses.items() if req['required']]
        found_required = len([cat for cat in required_clauses if cat in categories_found])
        risk_analysis['completeness_score'] = (found_required / len(required_clauses)) * 100
        
        # Generate recommendations
        risk_analysis['recommendations'] = self._generate_recommendations(risk_analysis, categories_found)
        
        return risk_analysis
    
    def _analyze_clause_risks(self, clause: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risks in a single clause"""
        clause_text = clause.get('text', '').lower()
        
        identified_risks = []
        concerning_terms = []
        
        # Check for high-risk patterns
        for pattern in self.risk_patterns['high_risk_terms']:
            if re.search(pattern, clause_text, re.IGNORECASE):
                identified_risks.append(f"Contains high-risk term: {pattern}")
                concerning_terms.append(pattern)
        
        # Check for medium-risk patterns
        for pattern in self.risk_patterns['medium_risk_terms']:
            if re.search(pattern, clause_text, re.IGNORECASE):
                identified_risks.append(f"Contains medium-risk term: {pattern}")
                concerning_terms.append(pattern)
        
        # Check for concerning phrases
        for pattern in self.risk_patterns['concerning_phrases']:
            if re.search(pattern, clause_text, re.IGNORECASE):
                identified_risks.append(f"Contains concerning phrase: {pattern}")
                concerning_terms.append(pattern)
        
        return {
            'identified_risks': identified_risks,
            'concerning_terms': concerning_terms
        }
    
    def _generate_recommendations(self, risk_analysis: Dict[str, Any], categories_found: set) -> List[str]:
        """Generate actionable recommendations based on risk analysis"""
        recommendations = []
        
        # Recommendations for missing clauses
        for missing_clause in risk_analysis['missing_clauses']:
            if missing_clause['risk_level'] == 'high':
                recommendations.append(f"🔴 CRITICAL: Add a {missing_clause['category']} clause to {missing_clause['description'].lower()}")
            elif missing_clause['risk_level'] == 'medium':
                recommendations.append(f"🟡 IMPORTANT: Consider adding a {missing_clause['category']} clause to {missing_clause['description'].lower()}")
        
        # Recommendations for high-risk clauses
        if risk_analysis['high_risk_clauses']:
            recommendations.append(f"🔴 REVIEW: {len(risk_analysis['high_risk_clauses'])} high-risk clauses require immediate legal review")
        
        # Overall risk recommendations
        if risk_analysis['overall_risk_score'] > 70:
            recommendations.append("🔴 HIGH RISK: This document contains significant legal risks. Professional legal review is strongly recommended")
        elif risk_analysis['overall_risk_score'] > 40:
            recommendations.append("🟡 MEDIUM RISK: This document has moderate risks. Consider legal consultation")
        else:
            recommendations.append("🟢 LOW RISK: This document appears to have acceptable risk levels")
        
        # Completeness recommendations
        if risk_analysis['completeness_score'] < 60:
            recommendations.append("📋 INCOMPLETE: This document is missing several essential clauses")
        elif risk_analysis['completeness_score'] < 80:
            recommendations.append("📋 REVIEW: Consider adding missing clauses for better protection")
        
        # Specific category recommendations
        if 'Liability' not in categories_found:
            recommendations.append("⚖️ Add liability limitations to protect against excessive damages")
        
        if 'Termination' not in categories_found:
            recommendations.append("🚪 Include clear termination procedures and notice requirements")
        
        if 'Dispute Resolution' not in categories_found:
            recommendations.append("🤝 Add dispute resolution mechanisms (arbitration, mediation, or court jurisdiction)")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def get_risk_color(self, risk_level: str) -> str:
        """Get color code for risk level"""
        colors = {
            'high': '#ff4444',    # Red
            'medium': '#ffaa00',  # Orange/Yellow
            'low': '#00aa44'      # Green
        }
        return colors.get(risk_level.lower(), '#888888')
    
    def get_risk_emoji(self, risk_level: str) -> str:
        """Get emoji for risk level"""
        emojis = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return emojis.get(risk_level.lower(), '⚪')
