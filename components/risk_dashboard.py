import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import pandas as pd

def render_risk_dashboard(risk_analysis: Dict[str, Any], clauses: List[Dict[str, Any]]):
    """
    Render the comprehensive risk dashboard
    
    Args:
        risk_analysis: Risk analysis results
        clauses: List of analyzed clauses
    """
    
    # Dashboard header
    st.markdown("## ⚠️ Risk Assessment Dashboard")
    
    # Overview metrics
    render_risk_overview(risk_analysis)
    
    # Risk breakdown charts
    render_risk_charts(risk_analysis, clauses)
    
    # Missing clauses analysis
    render_missing_clauses(risk_analysis)
    
    # High-risk clauses detail
    render_high_risk_clauses(risk_analysis)
    
    # Recommendations
    render_recommendations(risk_analysis)

def render_risk_overview(risk_analysis: Dict[str, Any]):
    """Render the risk overview metrics"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    overall_risk = risk_analysis.get('overall_risk_score', 0)
    completeness = risk_analysis.get('completeness_score', 0)
    risk_breakdown = risk_analysis.get('risk_breakdown', {})
    
    with col1:
        # Overall risk score with color coding
        risk_color = get_risk_score_color(overall_risk)
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: {risk_color}; border-radius: 10px; color: white;'>
            <h2 style='margin: 0; font-size: 2.5rem;'>{overall_risk:.1f}%</h2>
            <p style='margin: 0; font-weight: bold;'>Overall Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Completeness score
        completeness_color = get_completeness_color(completeness)
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: {completeness_color}; border-radius: 10px; color: white;'>
            <h2 style='margin: 0; font-size: 2.5rem;'>{completeness:.1f}%</h2>
            <p style='margin: 0; font-weight: bold;'>Completeness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        high_risk_count = risk_breakdown.get('high', 0)
        st.metric(
            label="🔴 High Risk Clauses",
            value=high_risk_count,
            delta=f"Requires immediate attention" if high_risk_count > 0 else "None found"
        )
    
    with col4:
        missing_count = len(risk_analysis.get('missing_clauses', []))
        st.metric(
            label="📋 Missing Clauses",
            value=missing_count,
            delta=f"Essential clauses missing" if missing_count > 0 else "All essential clauses present"
        )

def render_risk_charts(risk_analysis: Dict[str, Any], clauses: List[Dict[str, Any]]):
    """Render risk visualization charts"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk level distribution pie chart
        risk_breakdown = risk_analysis.get('risk_breakdown', {})
        
        if any(risk_breakdown.values()):
            fig_pie = px.pie(
                values=list(risk_breakdown.values()),
                names=['High Risk', 'Medium Risk', 'Low Risk'],
                title="Risk Level Distribution",
                color_discrete_map={
                    'High Risk': '#ff4444',
                    'Medium Risk': '#ffaa00',
                    'Low Risk': '#00aa44'
                }
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No risk data available for visualization")
    
    with col2:
        # Category risk analysis
        if clauses:
            category_risk_data = analyze_category_risks(clauses)
            
            if category_risk_data:
                df_cat = pd.DataFrame(category_risk_data)
                
                fig_bar = px.bar(
                    df_cat,
                    x='Category',
                    y='Average_Risk_Score',
                    color='Highest_Risk_Level',
                    title="Risk by Category",
                    color_discrete_map={
                        'high': '#ff4444',
                        'medium': '#ffaa00',
                        'low': '#00aa44'
                    }
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)

def analyze_category_risks(clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze risk levels by category"""
    category_data = {}
    
    for clause in clauses:
        category = clause.get('category', 'General')
        risk_level = clause.get('risk_level', 'low')
        
        if category not in category_data:
            category_data[category] = {
                'risks': [],
                'count': 0
            }
        
        # Convert risk level to numeric score
        risk_score = {'high': 3, 'medium': 2, 'low': 1}.get(risk_level, 1)
        category_data[category]['risks'].append(risk_level)
        category_data[category]['count'] += 1
    
    # Calculate averages and highest risk per category
    result = []
    for category, data in category_data.items():
        if data['count'] > 0:
            risk_scores = [{'high': 3, 'medium': 2, 'low': 1}.get(r, 1) for r in data['risks']]
            avg_score = sum(risk_scores) / len(risk_scores)
            
            # Find highest risk level in category
            if 'high' in data['risks']:
                highest_risk = 'high'
            elif 'medium' in data['risks']:
                highest_risk = 'medium'
            else:
                highest_risk = 'low'
            
            result.append({
                'Category': category,
                'Average_Risk_Score': avg_score,
                'Highest_Risk_Level': highest_risk,
                'Clause_Count': data['count']
            })
    
    return result

def render_missing_clauses(risk_analysis: Dict[str, Any]):
    """Render missing clauses analysis"""
    missing_clauses = risk_analysis.get('missing_clauses', [])
    
    if missing_clauses:
        st.markdown("### 📋 Missing Essential Clauses")
        
        for clause in missing_clauses:
            category = clause.get('category', 'Unknown')
            risk_level = clause.get('risk_level', 'medium')
            description = clause.get('description', 'No description available')
            
            risk_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(risk_level, '⚪')
            
            with st.expander(f"{risk_emoji} Missing: {category}", expanded=risk_level == 'high'):
                st.markdown(f"**Risk Level:** {risk_level.title()}")
                st.markdown(f"**Purpose:** {description}")
                
                if risk_level == 'high':
                    st.error("This is a critical missing clause that should be added immediately.")
                elif risk_level == 'medium':
                    st.warning("This clause is important and should be considered for inclusion.")
                else:
                    st.info("This clause would provide additional protection if included.")
    else:
        st.success("✅ All essential clauses are present in the document!")

def render_high_risk_clauses(risk_analysis: Dict[str, Any]):
    """Render detailed view of high-risk clauses"""
    high_risk_clauses = risk_analysis.get('high_risk_clauses', [])
    
    if high_risk_clauses:
        st.markdown("### 🔴 High-Risk Clauses Requiring Attention")
        
        for i, clause in enumerate(high_risk_clauses):
            clause_id = clause.get('id', i + 1)
            category = clause.get('category', 'Unknown')
            text_preview = clause.get('text_preview', 'No preview available')
            risks = clause.get('risks', [])
            concerns = clause.get('concerns', [])
            
            with st.expander(f"🔴 Clause {clause_id}: {category}", expanded=i < 2):
                st.markdown(f"**Preview:** {text_preview}")
                
                if risks:
                    st.markdown("**Identified Risks:**")
                    for risk in risks:
                        st.markdown(f"• ⚠️ {risk}")
                
                if concerns:
                    st.markdown("**Specific Concerns:**")
                    for concern in concerns:
                        st.markdown(f"• 🚨 {concern}")
                
                st.error("**Action Required:** This clause requires immediate legal review before contract execution.")
    else:
        st.success("✅ No high-risk clauses identified!")

def render_recommendations(risk_analysis: Dict[str, Any]):
    """Render actionable recommendations"""
    recommendations = risk_analysis.get('recommendations', [])
    
    if recommendations:
        st.markdown("### 💡 Recommendations")
        
        # Categorize recommendations by priority
        critical_recs = [r for r in recommendations if '🔴' in r]
        important_recs = [r for r in recommendations if '🟡' in r]
        general_recs = [r for r in recommendations if '🟢' in r or ('🔴' not in r and '🟡' not in r)]
        
        if critical_recs:
            st.markdown("#### 🔴 Critical Actions")
            for rec in critical_recs:
                st.error(rec)
        
        if important_recs:
            st.markdown("#### 🟡 Important Considerations")
            for rec in important_recs:
                st.warning(rec)
        
        if general_recs:
            st.markdown("#### 💡 General Recommendations")
            for rec in general_recs:
                st.info(rec)
    else:
        st.info("No specific recommendations available.")

def get_risk_score_color(score: float) -> str:
    """Get color based on risk score"""
    if score >= 70:
        return "#dc3545"  # Red
    elif score >= 40:
        return "#fd7e14"  # Orange
    else:
        return "#28a745"  # Green

def get_completeness_color(score: float) -> str:
    """Get color based on completeness score"""
    if score >= 80:
        return "#28a745"  # Green
    elif score >= 60:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red

def render_risk_trend_analysis(risk_analysis: Dict[str, Any]):
    """Render risk trend analysis (for future enhancement)"""
    # This function can be expanded to show historical risk trends
    # across multiple document analyses
    pass

def render_comparison_metrics(risk_analysis: Dict[str, Any]):
    """Render comparison with industry standards (for future enhancement)"""
    # This function can be expanded to compare risk levels
    # with industry benchmarks
    pass
