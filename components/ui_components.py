import streamlit as st
from datetime import datetime

def render_header():
    """Render the main application header"""
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem; background: linear-gradient(90deg, #1f4e79 0%, #2c5f88 100%); border-radius: 10px; color: white;'>
        <h1 style='margin: 0; font-size: 2.5rem;'>⚖️ ClauseWise</h1>
        <p style='margin: 0; font-size: 1.1rem; opacity: 0.9;'>AI-Powered Legal Document Analyzer</p>
    </div>
    """, unsafe_allow_html=True)

def render_disclaimer():
    """Render the legal disclaimer banner"""
    st.warning("""
    **⚠️ IMPORTANT DISCLAIMER:** ClauseWise is an AI assistant designed to help with document analysis. 
    It is NOT a replacement for professional legal advice. Always consult with qualified legal counsel 
    for important legal matters.
    """)

def render_sidebar():
    """Render the sidebar navigation and return selected page"""
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        # User info
        if st.session_state.get('authenticated'):
            st.success("✅ Logged in")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()
            
            st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Select Page:",
            [
                "📤 Upload Document",
                "📊 View Analysis", 
                "⚠️ Risk Summary",
                "📥 Download Report",
                "📚 Document History"
            ],
            format_func=lambda x: x.split(" ", 1)[1]  # Remove emoji for cleaner display
        )
        
        # Extract page name without emoji
        page_name = page.split(" ", 1)[1]
        
        st.markdown("---")
        
        # Quick stats if analysis available
        if st.session_state.get('analysis_results'):
            results = st.session_state.analysis_results
            st.markdown("### 📈 Quick Stats")
            
            total_clauses = len(results.get('clauses', []))
            st.metric("Total Clauses", total_clauses)
            
            if 'risk_analysis' in results:
                risk_data = results['risk_analysis']
                high_risk = risk_data.get('risk_breakdown', {}).get('high', 0)
                st.metric("🔴 High Risk", high_risk)
                
                overall_risk = risk_data.get('overall_risk_score', 0)
                st.metric("Risk Score", f"{overall_risk:.1f}%")
        
        st.markdown("---")
        
        # Help section
        with st.expander("ℹ️ Help & Tips"):
            st.markdown("""
            **Supported Formats:**
            - PDF documents
            - Word documents (.docx)
            - Text files (.txt)
            
            **Risk Levels:**
            - 🔴 High: Requires immediate attention
            - 🟡 Medium: Should be reviewed
            - 🟢 Low: Generally acceptable
            
            **Tips:**
            - Upload clear, text-based documents
            - Review all high-risk clauses carefully
            - Consider legal counsel for complex agreements
            """)
        
        # Footer
        st.markdown("---")
        st.markdown(f"**ClauseWise v1.0**  \n{datetime.now().strftime('%Y-%m-%d')}")
    
    return page_name

def render_file_upload_zone():
    """Render an enhanced file upload zone"""
    st.markdown("""
    <div style='border: 2px dashed #cccccc; border-radius: 10px; padding: 2rem; text-align: center; margin: 1rem 0;'>
        <h3 style='color: #666; margin-bottom: 1rem;'>📄 Upload Your Legal Document</h3>
        <p style='color: #888; margin-bottom: 1rem;'>Drag and drop your file here or click to browse</p>
        <p style='color: #aaa; font-size: 0.9rem;'>Supported formats: PDF, DOCX, TXT</p>
    </div>
    """, unsafe_allow_html=True)

def render_loading_spinner(message: str = "Processing..."):
    """Render a loading spinner with custom message"""
    return st.spinner(f"🔄 {message}")

def render_success_message(message: str):
    """Render a success message with custom styling"""
    st.markdown(f"""
    <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 1rem; margin: 1rem 0;'>
        <strong style='color: #155724;'>✅ {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_error_message(message: str):
    """Render an error message with custom styling"""
    st.markdown(f"""
    <div style='background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 1rem; margin: 1rem 0;'>
        <strong style='color: #721c24;'>❌ {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_info_card(title: str, content: str, icon: str = "ℹ️"):
    """Render an information card"""
    st.markdown(f"""
    <div style='background-color: #f8f9fa; border-left: 4px solid #1f4e79; padding: 1rem; margin: 1rem 0; border-radius: 5px;'>
        <h4 style='margin: 0 0 0.5rem 0; color: #1f4e79;'>{icon} {title}</h4>
        <p style='margin: 0; color: #666;'>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def render_progress_bar(progress: int, message: str = ""):
    """Render a progress bar with message"""
    progress_bar = st.progress(progress)
    if message:
        st.text(message)
    return progress_bar

def render_metric_card(title: str, value: str, delta: str = None, color: str = "#1f4e79"):
    """Render a metric card with custom styling"""
    delta_html = ""
    if delta:
        delta_html = f"<p style='margin: 0; color: #666; font-size: 0.8rem;'>{delta}</p>"
    
    st.markdown(f"""
    <div style='background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        <h3 style='margin: 0 0 0.5rem 0; color: {color}; font-size: 2rem;'>{value}</h3>
        <p style='margin: 0; color: #666; font-weight: bold;'>{title}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
