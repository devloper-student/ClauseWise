import streamlit as st
import os
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from auth import authenticate_user, init_auth
from database import init_database, save_document, get_documents, save_analysis
from document_parser import parse_document
from ai_engine import AIEngine
from risk_engine import RiskEngine
from components.ui_components import render_sidebar, render_header, render_disclaimer
from components.clause_viewer import render_clause_viewer
from components.risk_dashboard import render_risk_dashboard
from utils import export_to_pdf, export_to_word

# Page configuration
st.set_page_config(
    page_title="ClauseWise - AI Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_document' not in st.session_state:
    st.session_state.current_document = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Initialize database and auth
init_database()
init_auth()

def main():
    """Main application function"""
    
    # Authentication check
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Initialize AI and Risk engines
    ai_engine = AIEngine()
    risk_engine = RiskEngine()
    
    # Render header and disclaimer
    render_header()
    render_disclaimer()
    
    # Sidebar navigation
    page = render_sidebar()
    
    # Main content area
    if page == "Upload Document":
        render_upload_page(ai_engine, risk_engine)
    elif page == "View Analysis":
        render_analysis_page()
    elif page == "Risk Summary":
        render_risk_summary_page()
    elif page == "Download Report":
        render_download_page()
    elif page == "Document History":
        render_history_page()

def render_login_page():
    """Render the login page"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f4e79; font-size: 3rem; margin-bottom: 1rem;'>⚖️ ClauseWise</h1>
        <h3 style='color: #666; margin-bottom: 2rem;'>AI-Powered Legal Document Analyzer</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to Continue")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        st.markdown("Username: `demo` | Password: `demo123`")
        st.markdown("Username: `legal_analyst` | Password: `clausewise2024`")

def render_upload_page(ai_engine, risk_engine):
    """Render the document upload and analysis page"""
    st.markdown("## 📄 Upload Legal Document")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Upload PDF, DOCX, or TXT files containing legal contracts or agreements"
    )
    
    if uploaded_file is not None:
        # Display file information
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success(f"File uploaded: {uploaded_file.name}")
            st.info(f"File size: {uploaded_file.size} bytes")
        
        with col2:
            analyze_button = st.button("🔍 Analyze Document", type="primary", use_container_width=True)
        
        if analyze_button:
            with st.spinner("Analyzing document... This may take a few minutes."):
                try:
                    # Parse document
                    text_content = parse_document(uploaded_file)
                    
                    if not text_content.strip():
                        st.error("No text content found in the document. Please check the file format.")
                        return
                    
                    # Extract and classify clauses
                    progress_bar = st.progress(0)
                    st.text("Extracting clauses...")
                    progress_bar.progress(25)
                    
                    clauses = ai_engine.extract_clauses(text_content)
                    progress_bar.progress(50)
                    
                    st.text("Classifying clauses...")
                    classified_clauses = ai_engine.classify_clauses(clauses)
                    progress_bar.progress(75)
                    
                    st.text("Performing risk analysis...")
                    risk_analysis = risk_engine.analyze_risks(classified_clauses)
                    progress_bar.progress(100)
                    
                    # Store results
                    analysis_results = {
                        'filename': uploaded_file.name,
                        'upload_time': datetime.now(),
                        'clauses': classified_clauses,
                        'risk_analysis': risk_analysis,
                        'original_text': text_content
                    }
                    
                    # Save to database
                    doc_id = save_document(uploaded_file.name, text_content)
                    save_analysis(doc_id, analysis_results)
                    
                    # Update session state
                    st.session_state.current_document = analysis_results
                    st.session_state.analysis_results = analysis_results
                    
                    st.success("Analysis complete!")
                    
                    # Display quick summary
                    display_quick_summary(analysis_results)
                    
                except Exception as e:
                    st.error(f"Error analyzing document: {str(e)}")

def display_quick_summary(results):
    """Display a quick summary of the analysis"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_clauses = len(results['clauses'])
    high_risk = sum(1 for clause in results['clauses'] if clause.get('risk_level') == 'high')
    medium_risk = sum(1 for clause in results['clauses'] if clause.get('risk_level') == 'medium')
    low_risk = total_clauses - high_risk - medium_risk
    
    with col1:
        st.metric("Total Clauses", total_clauses)
    
    with col2:
        st.metric("🔴 High Risk", high_risk)
    
    with col3:
        st.metric("🟡 Medium Risk", medium_risk)
    
    with col4:
        st.metric("🟢 Low Risk", low_risk)

def render_analysis_page():
    """Render the detailed analysis page"""
    if st.session_state.analysis_results is None:
        st.warning("No document analysis available. Please upload and analyze a document first.")
        return
    
    st.markdown("## 📊 Document Analysis")
    
    results = st.session_state.analysis_results
    
    # Search functionality
    search_query = st.text_input(
        "🔍 Search clauses",
        value=st.session_state.search_query,
        placeholder="Enter keywords to search within clauses..."
    )
    st.session_state.search_query = search_query
    
    # Filter clauses based on search
    filtered_clauses = results['clauses']
    if search_query:
        filtered_clauses = [
            clause for clause in results['clauses']
            if search_query.lower() in clause.get('text', '').lower() or
               search_query.lower() in clause.get('simplified_text', '').lower() or
               search_query.lower() in clause.get('category', '').lower()
        ]
    
    # Render clause viewer
    render_clause_viewer(filtered_clauses, search_query)

def render_risk_summary_page():
    """Render the risk summary page"""
    if st.session_state.analysis_results is None:
        st.warning("No document analysis available. Please upload and analyze a document first.")
        return
    
    st.markdown("## ⚠️ Risk Summary")
    
    results = st.session_state.analysis_results
    render_risk_dashboard(results['risk_analysis'], results['clauses'])

def render_download_page():
    """Render the download/export page"""
    if st.session_state.analysis_results is None:
        st.warning("No document analysis available. Please upload and analyze a document first.")
        return
    
    st.markdown("## 📥 Download Report")
    
    results = st.session_state.analysis_results
    
    st.markdown("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download PDF Report", use_container_width=True):
            pdf_data = export_to_pdf(results)
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_data,
                file_name=f"clausewise_report_{results['filename']}.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("📝 Download Word Report", use_container_width=True):
            word_data = export_to_word(results)
            st.download_button(
                label="⬇️ Download Word",
                data=word_data,
                file_name=f"clausewise_report_{results['filename']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

def render_history_page():
    """Render the document history page"""
    st.markdown("## 📚 Document History")
    
    documents = get_documents()
    
    if not documents:
        st.info("No documents have been analyzed yet.")
        return
    
    # Create a dataframe for display
    df_data = []
    for doc in documents:
        df_data.append({
            'Filename': doc['filename'],
            'Upload Date': doc['created_at'].strftime('%Y-%m-%d %H:%M'),
            'Status': 'Analyzed' if doc.get('analysis_id') else 'Uploaded'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
