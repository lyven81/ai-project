import streamlit as st
import time
from typing import Dict, List
import random

class DemoMode:
    """Demo mode for Claude PDF Summarizer when API key is not available"""
    
    def __init__(self):
        self.demo_summaries = {
            'Executive': {
                'content': """
                ## Executive Summary
                
                **Key Findings:**
                • Strategic market analysis reveals 25% growth opportunity in Q4
                • Revenue projections indicate $2.3M potential increase
                • Operational efficiency improvements could reduce costs by 15%
                • Customer satisfaction scores show 92% positive feedback
                
                **Strategic Recommendations:**
                • Implement digital transformation initiative by Q2 2024
                • Expand market presence in Southeast Asia region
                • Invest in AI-powered customer service automation
                • Develop strategic partnerships with key industry leaders
                
                **Risk Assessment:**
                • Market volatility presents moderate risk (3/5)
                • Supply chain disruptions require contingency planning
                • Regulatory changes may impact timeline by 2-3 months
                """,
                'language': 'English'
            },
            'Simple': {
                'content': """
                ## Simple Summary
                
                **What this document is about:**
                This document talks about business opportunities and how to make the company better.
                
                **Main Points:**
                • The business could grow by 25% in the next few months
                • We could make $2.3 million more money
                • We can save 15% on costs by working more efficiently
                • Most customers (92%) are happy with our service
                
                **What we should do:**
                • Use more technology to help customers
                • Start selling in new countries
                • Get better computer systems
                • Work with other companies
                
                **Things to watch out for:**
                • Market prices might change
                • We might have trouble getting supplies
                • New rules might slow us down
                """,
                'language': 'English'
            },
            'For Kids': {
                'content': """
                ## Summary for Kids 🎈
                
                **What's this about?**
                This is like a report card for a company - it shows how well they're doing!
                
                **The Good News! 🎉**
                • The company is growing like a plant in spring (25% bigger!)
                • They might earn lots more money ($2.3 million - that's like having 2,300,000 dollar bills!)
                • They found ways to save money, like using coupons at the store
                • Almost everyone (92 out of 100 people) thinks they do a great job!
                
                **What they want to do next:**
                • Get cool new computers and robots to help customers
                • Start selling their stuff in new places around the world
                • Make friends with other companies
                • Use smart computers to answer questions faster
                
                **Things that might be tricky:**
                • Sometimes prices go up and down like a roller coaster
                • It might be hard to get the things they need
                • Grown-ups might make new rules they have to follow
                
                **Think of it like:** Running a lemonade stand that's doing so well, you want to open more stands in other neighborhoods!
                """,
                'language': 'English'
            }
        }
        
        self.demo_files = [
            "Business_Strategy_Report.pdf",
            "Market_Analysis_Q3_2024.pdf", 
            "Customer_Satisfaction_Study.pdf",
            "Financial_Performance_Review.pdf",
            "Operational_Efficiency_Study.pdf"
        ]

    def show_demo_interface(self):
        """Display the demo interface"""
        st.markdown("""
        <div style="background: #f5f5dc; 
                    padding: 2rem; border-radius: 12px; color: #333; text-align: center; margin-bottom: 2rem;
                    border: 2px solid #daa520;">
            <h2 style="color: #333;">🎬 Demo Mode Active</h2>
            <p>Experience Claude PDF Summarizer without API keys!</p>
            <p><em>Upload any PDF or use our sample document to see the magic happen!</em></p>
        </div>
        """, unsafe_allow_html=True)

    def process_demo_document(self, style: str = "Executive", language: str = "English") -> Dict:
        """Simulate document processing with demo data"""
        
        # Simulate processing time
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = [
            "📄 Extracting text from PDF...",
            "🧠 Analyzing document structure...",
            "✨ Applying AI summarization...",
            "🎯 Tailoring to selected style...",
            "🌐 Optimizing for language...",
            "✅ Generating final summary..."
        ]
        
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(0.8)
        
        progress_bar.empty()
        status_text.empty()
        
        # Return demo summary
        demo_file = random.choice(self.demo_files)
        summary_data = self.demo_summaries.get(style, self.demo_summaries['Executive'])
        
        return {
            'filename': demo_file,
            'summary': summary_data['content'],
            'style': style,
            'language': language,
            'word_count': len(summary_data['content'].split()),
            'processing_time': f"{random.uniform(2.1, 4.7):.1f} seconds"
        }

    def show_demo_features(self):
        """Display demo features and capabilities"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Summary Styles
            - **Executive**: Business-focused
            - **Simple**: Clear & straightforward  
            - **For Kids**: Fun & educational
            """)
        
        with col2:
            st.markdown("""
            ### 🌐 Languages
            - **English**: Full support
            - **Bahasa**: Indonesian 
            - **中文**: Simplified Chinese
            """)
        
        with col3:
            st.markdown("""
            ### ⚡ Features  
            - **Fast Processing**: 2-5 seconds
            - **Multi-format**: PDF, DOCX, TXT
            - **Export Options**: Multiple formats
            """)

    def show_sample_results(self):
        """Show sample results for different styles"""
        
        st.markdown("### 📊 Sample Results Preview")
        
        tab1, tab2, tab3 = st.tabs(["📈 Executive", "📝 Simple", "🎈 For Kids"])
        
        with tab1:
            st.markdown(self.demo_summaries['Executive']['content'])
        
        with tab2:
            st.markdown(self.demo_summaries['Simple']['content'])
        
        with tab3:
            st.markdown(self.demo_summaries['For Kids']['content'])

def run_demo_mode():
    """Main function to run demo mode"""
    demo = DemoMode()
    
    st.title("📄 Claude PDF Summarizer")
    
    # Show demo notice
    demo.show_demo_interface()
    
    # File upload (demo)
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf', 'docx', 'txt'],
        help="In demo mode, any file will use sample data for demonstration"
    )
    
    # Settings
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("Summary Style", ["Executive", "Simple", "For Kids"])
    with col2:
        language = st.selectbox("Language", ["English", "Bahasa", "简体中文"])
    
    # Process button
    if st.button("🚀 Generate Summary (Demo)", type="primary"):
        if uploaded_file or st.session_state.get('demo_run', False):
            st.session_state.demo_run = True
            
            # Process demo
            result = demo.process_demo_document(style, language)
            
            # Show results
            st.success(f"✅ Summary generated for: {result['filename']}")
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Word Count", result['word_count'])
            with col2:
                st.metric("Processing Time", result['processing_time'])
            with col3:
                st.metric("Style", result['style'])
            
            # Summary content
            st.markdown("### 📋 Generated Summary")
            st.markdown(result['summary'])
            
            # Download button (demo)
            st.download_button(
                label="📥 Download Summary",
                data=result['summary'],
                file_name=f"summary_{style.lower()}.md",
                mime="text/markdown"
            )
            
        else:
            st.info("👆 Please upload a file to see the demo in action!")
    
    # Show features and samples
    st.markdown("---")
    demo.show_demo_features()
    
    st.markdown("---")
    with st.expander("👀 Preview Sample Results"):
        demo.show_sample_results()
    
    # API key notice
    st.markdown("---")
    st.info("""
    🔑 **Want to use your own documents?** 
    
    Add your Claude API key to the `.env` file:
    ```
    CLAUDE_API_KEY=your_api_key_here
    ```
    Then restart the application for full functionality!
    """)

if __name__ == "__main__":
    run_demo_mode()