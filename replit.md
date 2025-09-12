# ClauseWise - AI Legal Document Analyzer

## Overview

ClauseWise is an AI-powered legal document analysis platform that helps users understand complex legal contracts and identify potential risks. The application uses advanced natural language processing to automatically extract, classify, and simplify legal clauses while providing comprehensive risk assessments. Built with Streamlit for the frontend and Python for the backend, it supports multiple document formats (PDF, DOCX, TXT) and provides exportable analysis reports.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit-based Interface**: Single-page web application with component-based architecture
- **Modular UI Components**: Separate modules for clause viewer, risk dashboard, and UI components
- **Responsive Design**: Mobile-friendly interface with sidebar navigation and color-coded risk indicators
- **Session Management**: State management for user authentication, document storage, and analysis results

### Backend Architecture
- **Monolithic Python Application**: All functionality contained within a single Streamlit app
- **Document Processing Pipeline**: Multi-format parser supporting PDF (pdfplumber), DOCX (python-docx), and TXT files
- **AI Processing Engine**: Integration with OpenAI GPT models and spaCy for natural language processing
- **Risk Assessment Engine**: Rule-based pattern matching combined with AI-powered risk analysis
- **Authentication System**: Simple username/password authentication with SHA-256 password hashing

### Data Processing Flow
- **Document Ingestion**: Upload and parse documents into text format
- **Clause Extraction**: Use spaCy for sentence segmentation and legal pattern recognition
- **AI Analysis**: OpenAI integration for clause classification and plain-language summarization
- **Risk Assessment**: Pattern matching for high-risk terms and missing essential clauses
- **Report Generation**: PDF and Word export functionality using reportlab and python-docx

### Data Storage
- **SQLite Database**: Lightweight relational database for document storage, user management, and analysis history
- **File System Storage**: Temporary storage for uploaded documents and generated reports
- **Session State**: In-memory storage for current analysis results and user preferences

### Security Architecture
- **Basic Authentication**: Username/password system with salted password hashing
- **Session Management**: Streamlit session state for maintaining user authentication
- **Input Validation**: Document format validation and content sanitization

## External Dependencies

### AI and NLP Services
- **OpenAI API**: GPT models for clause analysis and summarization
- **spaCy**: Natural language processing library with English language model (en_core_web_sm)

### Document Processing Libraries
- **pdfplumber**: PDF text extraction and processing
- **python-docx**: Microsoft Word document parsing and generation
- **reportlab**: PDF report generation and formatting

### Web Framework and UI
- **Streamlit**: Primary web application framework
- **Plotly**: Interactive charts and data visualization for risk dashboards

### Database and Storage
- **SQLite3**: Built-in Python database for persistent data storage
- **Pandas**: Data manipulation and analysis for reporting features

### Authentication and Security
- **hashlib**: Password hashing and security functions (built-in Python library)

### Development and Deployment
- **Python 3.x**: Core runtime environment
- **Requirements.txt**: Package dependency management for Replit deployment