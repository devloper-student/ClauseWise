import streamlit as st
from typing import List, Dict, Any
from utils import format_risk_level, truncate_text, get_risk_color_hex

def render_clause_viewer(clauses: List[Dict[str, Any]], search_query: str = ""):
    """
    Render the interactive clause viewer with side-by-side original and simplified text
    
    Args:
        clauses: List of classified clauses
        search_query: Current search query for highlighting
    """
    if not clauses:
        st.info("No clauses found matching your search criteria.")
        return
    
    st.markdown(f"### 📝 Clause Analysis ({len(clauses)} clauses)")
    
    # Filter and sort options
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        risk_filter = st.selectbox(
            "Filter by Risk Level:",
            options=["All", "High", "Medium", "Low"],
            index=0
        )
    
    with col2:
        category_options = ["All"] + sorted(list(set(clause.get('category', 'General') for clause in clauses)))
        category_filter = st.selectbox(
            "Filter by Category:",
            options=category_options,
            index=0
        )
    
    with col3:
        sort_option = st.selectbox(
            "Sort by:",
            options=["Risk Level (High to Low)", "Risk Level (Low to High)", "Category", "Clause ID"],
            index=0
        )
    
    # Apply filters
    filtered_clauses = clauses.copy()
    
    if risk_filter != "All":
        filtered_clauses = [c for c in filtered_clauses if c.get('risk_level', '').lower() == risk_filter.lower()]
    
    if category_filter != "All":
        filtered_clauses = [c for c in filtered_clauses if c.get('category', '') == category_filter]
    
    # Apply sorting
    if sort_option == "Risk Level (High to Low)":
        risk_order = {'high': 3, 'medium': 2, 'low': 1}
        filtered_clauses.sort(key=lambda x: risk_order.get(x.get('risk_level', 'low'), 0), reverse=True)
    elif sort_option == "Risk Level (Low to High)":
        risk_order = {'high': 3, 'medium': 2, 'low': 1}
        filtered_clauses.sort(key=lambda x: risk_order.get(x.get('risk_level', 'low'), 0))
    elif sort_option == "Category":
        filtered_clauses.sort(key=lambda x: x.get('category', 'General'))
    else:  # Clause ID
        filtered_clauses.sort(key=lambda x: x.get('id', 0))
    
    if not filtered_clauses:
        st.warning("No clauses match the selected filters.")
        return
    
    st.markdown(f"**Showing {len(filtered_clauses)} of {len(clauses)} clauses**")
    
    # Render clauses
    for i, clause in enumerate(filtered_clauses):
        render_single_clause(clause, i, search_query)

def render_single_clause(clause: Dict[str, Any], index: int, search_query: str = ""):
    """Render a single clause with expandable details"""
    
    # Get clause information
    clause_id = clause.get('id', index + 1)
    category = clause.get('category', 'General')
    risk_level = clause.get('risk_level', 'low')
    simplified_text = clause.get('simplified_text', 'No summary available')
    original_text = clause.get('text', '')
    key_terms = clause.get('key_terms', [])
    concerns = clause.get('concerns', [])
    
    # Risk level styling
    risk_color = get_risk_color_hex(risk_level)
    risk_emoji = format_risk_level(risk_level)
    
    # Create expandable clause section
    with st.expander(
        f"{risk_emoji} Clause {clause_id}: {category}",
        expanded=index < 3  # Expand first 3 clauses by default
    ):
        # Clause header with metrics
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Category:** {category}")
        
        with col2:
            st.markdown(f"**Risk Level:** {risk_emoji}")
        
        with col3:
            if key_terms:
                st.markdown(f"**Key Terms:** {len(key_terms)}")
        
        st.markdown("---")
        
        # Side-by-side comparison
        col_original, col_simplified = st.columns(2)
        
        with col_original:
            st.markdown("#### 📄 Original Text")
            
            # Highlight search terms if any
            display_text = original_text
            if search_query and search_query.strip():
                display_text = highlight_search_terms(original_text, search_query)
            
            st.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; border-left: 4px solid {risk_color}; max-height: 300px; overflow-y: auto;'>
                {display_text}
            </div>
            """, unsafe_allow_html=True)
        
        with col_simplified:
            st.markdown("#### 🔍 Plain English Summary")
            
            # Highlight search terms in simplified text too
            display_simplified = simplified_text
            if search_query and search_query.strip():
                display_simplified = highlight_search_terms(simplified_text, search_query)
            
            st.markdown(f"""
            <div style='background-color: #e8f5e8; padding: 1rem; border-radius: 5px; border-left: 4px solid #28a745; max-height: 300px; overflow-y: auto;'>
                {display_simplified}
            </div>
            """, unsafe_allow_html=True)
        
        # Additional details
        if key_terms or concerns:
            st.markdown("#### 📋 Additional Details")
            
            if key_terms:
                st.markdown("**Key Terms:**")
                terms_text = ", ".join(key_terms[:10])  # Limit to first 10 terms
                st.markdown(f"<span style='background-color: #fff3cd; padding: 0.2rem 0.4rem; border-radius: 3px; margin: 0.1rem;'>{terms_text}</span>", unsafe_allow_html=True)
            
            if concerns:
                st.markdown("**Concerns & Red Flags:**")
                for concern in concerns[:5]:  # Limit to first 5 concerns
                    st.markdown(f"• ⚠️ {concern}")
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button(f"📋 Copy Original", key=f"copy_orig_{clause_id}"):
                st.code(original_text, language="text")
        
        with col_btn2:
            if st.button(f"📝 Copy Summary", key=f"copy_summ_{clause_id}"):
                st.code(simplified_text, language="text")
        
        with col_btn3:
            if st.button(f"⚠️ Risk Details", key=f"risk_details_{clause_id}"):
                show_risk_details(clause)

def highlight_search_terms(text: str, search_query: str) -> str:
    """Highlight search terms in text"""
    if not search_query or not search_query.strip():
        return text
    
    import re
    
    # Split search query into individual terms
    terms = search_query.strip().split()
    
    highlighted_text = text
    for term in terms:
        if len(term) > 2:  # Only highlight terms longer than 2 characters
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_text = pattern.sub(
                f'<mark style="background-color: yellow; padding: 0.1rem;">{term}</mark>',
                highlighted_text
            )
    
    return highlighted_text

def show_risk_details(clause: Dict[str, Any]):
    """Show detailed risk analysis for a clause"""
    st.markdown("#### 🔍 Detailed Risk Analysis")
    
    risk_level = clause.get('risk_level', 'low')
    category = clause.get('category', 'General')
    concerns = clause.get('concerns', [])
    
    # Risk assessment
    if risk_level == 'high':
        st.error(f"🔴 **HIGH RISK** - This {category.lower()} clause requires immediate legal review")
    elif risk_level == 'medium':
        st.warning(f"🟡 **MEDIUM RISK** - This {category.lower()} clause should be carefully reviewed")
    else:
        st.success(f"🟢 **LOW RISK** - This {category.lower()} clause appears acceptable")
    
    # Specific concerns
    if concerns:
        st.markdown("**Specific Issues Found:**")
        for i, concern in enumerate(concerns, 1):
            st.markdown(f"{i}. {concern}")
    
    # Recommendations based on category and risk
    recommendations = get_clause_recommendations(category, risk_level)
    if recommendations:
        st.markdown("**Recommendations:**")
        for rec in recommendations:
            st.markdown(f"• {rec}")

def get_clause_recommendations(category: str, risk_level: str) -> List[str]:
    """Get specific recommendations based on clause category and risk level"""
    recommendations = []
    
    if category == "Liability" and risk_level == "high":
        recommendations.extend([
            "Consider adding liability caps or limitations",
            "Review exclusions for consequential damages",
            "Ensure mutual liability provisions where appropriate"
        ])
    elif category == "Termination" and risk_level in ["high", "medium"]:
        recommendations.extend([
            "Review termination notice periods",
            "Check for automatic renewal clauses",
            "Ensure clear post-termination obligations"
        ])
    elif category == "Confidentiality" and risk_level in ["high", "medium"]:
        recommendations.extend([
            "Verify appropriate confidentiality scope",
            "Check duration of confidentiality obligations",
            "Ensure reciprocal confidentiality provisions"
        ])
    elif category == "Payment" and risk_level in ["high", "medium"]:
        recommendations.extend([
            "Review payment terms and schedules",
            "Check for late payment penalties",
            "Verify dispute resolution for payment issues"
        ])
    
    if not recommendations:
        recommendations.append("Consult with legal counsel for detailed review")
    
    return recommendations
