This project aims to create a Retrieval-Augmented Generation (RAG) AI trained on data from Minnesota-based nonprofit organizations.
The system will provide an accessible, interactive interface that allows users to easily discover new and relevant nonprofits based on their interests, causes, or location.

By combining publicly available data, supplemental research, and web content extraction, the AI will be able to give context-aware, natural language answers and recommendations.

Goals
Centralize nonprofit data from multiple sources into a clean, comprehensive dataset.

Enhance the dataset with supplemental information from CSV files, Every.org’s API, and organization websites.

Train a RAG AI model that uses this dataset as a knowledge base.

Build an intuitive interface where users can:

Search for nonprofits by cause, location, or mission

Ask natural language questions

Receive personalized recommendations

Data Collection Pipeline
Scraping ProPublica Nonprofit Explorer

Gathers Minnesota nonprofit records, categorized by NTEE codes.

Supplemental CSV Integration

Adds additional information such as:

Website URLs

Activity areas

Communities served

Contact details

Every.org API Enrichment

Appends cause categories, tags, and missing website data.

Website Content Extraction (Planned)

Crawls and parses nonprofit websites for descriptive content.

Dataset Assembly

Combines all collected data into a single CSV for AI ingestion.

Tech Stack
Python – Data scraping, enrichment, and processing

Requests – API calls and HTTP requests

BeautifulSoup – HTML parsing

Pandas – Data cleaning and manipulation

Trafilatura (planned) – Website content extraction

Every.org API – Nonprofit enrichment data

ProPublica Nonprofit Explorer API – Base dataset

Planned Features
Natural Language Search – Ask “Show me nonprofits focused on youth education in Minneapolis” and get results instantly.

Cause-Based Discovery – Explore organizations by category (e.g., environmental, arts, healthcare).

Recommendation Engine – Suggest related nonprofits based on user queries.

Simple Web Interface – Accessible UI for both general users and nonprofit professionals.

Current Status
✅ ProPublica data scraping implemented

✅ CSV-based data supplementation implemented

✅ Every.org API enrichment implemented

⏳ Website content extraction in progress

⏳ AI training phase upcoming

⏳ Interface development planned

Output Files
gotta backdoor.csv – Dataset with supplemental CSV details added.

holy grail.csv – Final merged dataset with enrichment from Every.org.

holy grail (incomplete).csv – Partially processed dataset in case of script interruption.

