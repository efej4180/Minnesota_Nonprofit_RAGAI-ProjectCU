# Minnesota Nonprofit RAG AI

## Overview
This project creates a **Retrieval-Augmented Generation (RAG) AI** trained on data from Minnesota-based nonprofit organizations.  
The system will provide an **accessible, interactive interface** that helps users discover new and relevant nonprofits based on their interests, causes, or location.

By combining publicly available datasets, supplemental research, and nonprofit website content, the AI will be able to provide context-aware, natural language answers and recommendations.

---

## Goals
- **Centralize nonprofit data** from multiple sources into a single, well-structured dataset  
- **Enhance the dataset** with supplemental details from curated sources and APIs  
- **Train a RAG AI model** that can answer questions and recommend nonprofits  
- **Build an intuitive interface** where users can:
  - Search for nonprofits by cause, location, or mission  
  - Ask natural language questions  
  - Receive personalized recommendations  

---

## Data Collection Pipeline
1. **Scrape public nonprofit records** using the ProPublica Nonprofit Explorer API, filtered by NTEE category and state (Minnesota)  
2. **Merge supplemental CSV data** such as:
   - Website URLs  
   - Activity areas  
   - Communities served  
   - Contact details  
3. **Enrich records with Every.org API data** to add:
   - Cause categories  
   - Tags  
   - Missing website links  
4. **Extract website content** *(planned)* to capture mission statements, service descriptions, and other useful text  
5. **Combine all data** into a single, clean dataset for AI ingestion  

---

## Tech Stack
- **Python** – data scraping, enrichment, and processing  
- **Requests** – API calls and HTTP requests  
- **BeautifulSoup** – HTML parsing  
- **Pandas** – data cleaning and manipulation  
- **Trafilatura** *(planned)* – website content extraction  
- **Every.org API** – nonprofit enrichment data  
- **ProPublica Nonprofit Explorer API** – base dataset  

---

## Planned Features
- **Natural language search** — e.g., “Show me nonprofits focused on youth education in Minneapolis”  
- **Cause-based discovery** — browse organizations by mission area  
- **Recommendation engine** — suggest related nonprofits based on user queries  
- **Simple web interface** — accessible to both the public and nonprofit professionals  

---

## Current Status
- ✅ Public nonprofit data scraping implemented  
- ✅ Supplemental CSV integration implemented  
- ✅ API-based enrichment implemented  
- ⏳ Website content extraction in progress  
- ⏳ AI training phase upcoming  
- ⏳ Interface development planned  

---
