"""
Career Chatbot Utility
Provides career guidance using keyword-based responses.
Optionally uses OpenAI API if OPENAI_API_KEY is set in .env
"""

import re
import os
from config import Config


# ─── Static Knowledge Base ────────────────────────────────────────────────────

CAREER_KB = {
    'dsa': {
        'keywords': ['dsa', 'data structure', 'algorithm', 'leetcode', 'coding interview', 'competitive', 'cp'],
        'response': """## DSA Roadmap for Placements 🗺️

**Phase 1 – Foundations (4-6 weeks)**
- Arrays, Strings, 2-pointer, Sliding Window
- Linked Lists (singly/doubly, reversal, cycle detection)
- Stacks, Queues, Deques, Monotonic Stack

**Phase 2 – Core Algorithms (6-8 weeks)**
- Binary Search (standard + search on answer)
- Recursion & Backtracking (subsets, permutations)
- Trees: BFS, DFS, BST, DP on trees
- Heaps: Top-K, Median Finder

**Phase 3 – Advanced (4-6 weeks)**
- Graphs: BFS/DFS, Dijkstra, Topo Sort, Union-Find
- Dynamic Programming: 1D, 2D, knapsack, strings
- Greedy Algorithms

**Daily Plan**
- Solve 2-3 LeetCode problems (minimum)
- 1 easy warm-up + 1-2 mediums
- Review solutions after solving

**Resources**
- NeetCode 150 (best curated list)
- Striver's SDE Sheet
- CSES Problem Set (for CP)"""
    },
    'python': {
        'keywords': ['python', 'learn python', 'python roadmap', 'python for beginners'],
        'response': """## Python Learning Roadmap 🐍

**Week 1-2: Basics**
- Variables, data types, loops, functions
- Lists, dicts, sets, tuples
- File I/O, exceptions

**Week 3-4: Intermediate**
- OOP (classes, inheritance, magic methods)
- List comprehensions, generators, decorators
- Modules and packages

**Week 5-6: Applied**
- Virtual environments, pip
- Popular libraries: NumPy, Pandas, Requests
- Build small projects (CLI tools, automation scripts)

**Resources**
- Official Python docs (docs.python.org)
- Automate the Boring Stuff (free book)
- Real Python tutorials
- Python Crash Course by Eric Matthes"""
    },
    'sql': {
        'keywords': ['sql', 'database', 'mysql', 'postgresql', 'query', 'joins'],
        'response': """## SQL Roadmap 🗄️

**Basics (Week 1)**
- SELECT, WHERE, ORDER BY, GROUP BY, HAVING
- Aggregate functions: COUNT, SUM, AVG, MIN, MAX
- Filtering with LIKE, IN, BETWEEN, IS NULL

**Joins (Week 2)**
- INNER, LEFT, RIGHT, FULL OUTER JOIN
- Self joins, cross joins
- Subqueries (correlated vs non-correlated)

**Advanced (Week 3-4)**
- Window functions: ROW_NUMBER, RANK, LAG, LEAD
- CTEs (Common Table Expressions)
- Indexes, EXPLAIN, query optimization
- Stored procedures, triggers, views

**Practice Resources**
- SQLZoo (free, interactive)
- Mode SQL Tutorial
- LeetCode Database section (50 problems)
- HackerRank SQL challenges"""
    },
    'system_design': {
        'keywords': ['system design', 'hld', 'lld', 'scalability', 'microservices', 'distributed'],
        'response': """## System Design Roadmap 🏗️

**Core Concepts**
- Horizontal vs vertical scaling
- Load balancers (Round Robin, Consistent Hashing)
- Caching strategies (Redis, Memcached, CDN)
- Database sharding and replication
- CAP theorem, BASE vs ACID

**Common Interview Designs**
1. URL Shortener (like bit.ly)
2. Rate Limiter
3. WhatsApp / Messaging App
4. Instagram / Image Storage
5. YouTube / Video Streaming
6. Google Search / Web Crawler
7. Ride-sharing (Uber)
8. Distributed Cache

**Study Resources**
- System Design Primer (GitHub) ⭐
- Designing Data-Intensive Applications (book)
- Grokking System Design Interview (Educative)
- ByteByteGo newsletter
- Alex Xu's System Design Interview books"""
    },
    'ai_ml': {
        'keywords': ['machine learning', 'ai', 'ml roadmap', 'deep learning', 'nlp', 'data science'],
        'response': """## AI/ML Roadmap 🤖

**Prerequisites (1-2 months)**
- Python (NumPy, Pandas, Matplotlib)
- Math: Linear Algebra, Calculus, Probability, Statistics
- SQL for data manipulation

**Core ML (2-3 months)**
- Supervised: Linear Regression, Decision Trees, SVM, Random Forest
- Unsupervised: K-Means, PCA, DBSCAN
- Model evaluation, cross-validation, bias-variance tradeoff
- scikit-learn hands-on practice

**Deep Learning (2-3 months)**
- Neural Networks, Backpropagation
- CNNs (image classification), RNNs/LSTMs (sequences)
- Transfer Learning (HuggingFace)
- TensorFlow or PyTorch

**Specializations**
- NLP: Transformers, BERT, GPT, LangChain
- Computer Vision: OpenCV, YOLO, Detectron
- MLOps: MLflow, Docker, FastAPI deployment

**Resources**
- fast.ai (practical approach)
- Andrew Ng's ML Specialization (Coursera)
- Deep Learning Book (Goodfellow)
- Kaggle competitions"""
    },
    'resume': {
        'keywords': ['resume', 'cv', 'resume tips', 'ats', 'interview', 'resume format'],
        'response': """## Resume Tips for CSE Students 📄

**Structure (1 page max)**
1. Contact Info + LinkedIn + GitHub
2. Education (with GPA if > 7.5/10)
3. Technical Skills
4. Projects (2-4 strong ones)
5. Experience / Internships
6. Achievements / Certifications

**Strong Projects Include**
- Full-stack web app with real users
- ML project with a live demo
- Open source contribution
- Anything solving a real problem

**Quantify Everything**
❌ "Worked on backend API"
✅ "Built REST API serving 500 req/sec, reduced latency by 40%"

**ATS Tips**
- Use simple single-column layout
- Include job description keywords
- Use standard section headings
- Save as PDF with selectable text

**Common Mistakes**
- Generic objective statement (skip it)
- "Responsible for..." (use action verbs)
- Listing every course you took
- No GitHub or project links"""
    },
    'internship': {
        'keywords': ['internship', 'job', 'placement', 'campus placement', 'off campus', 'hiring'],
        'response': """## Internship & Placement Strategy 🎯

**Timeline (Final Year)**
- Aug-Oct: On-campus season (major product companies)
- Oct-Jan: Off-campus applications + startups
- Year-round: Remote internships, freelance

**Top Platforms**
- LinkedIn (most important - optimize profile)
- Naukri, Internshala (India)
- AngelList / Wellfound (startups)
- Company career pages directly
- Referrals (most effective!)

**Preparation Checklist**
✅ LeetCode 100+ problems (focus: mediums)
✅ System Design basics
✅ 2-3 solid projects on GitHub
✅ Resume reviewed and ATS-optimized
✅ LinkedIn with 500+ connections
✅ Mock interviews (Pramp, interviewing.io)

**Company Tiers**
- Tier 1: Google, Microsoft, Amazon, Meta, Apple
- Tier 2: Flipkart, Paytm, Zomato, Swiggy
- Tier 3: TCS, Infosys, Wipro, Cognizant
- Startups: High risk, high learning

**Apply broadly - getting one offer changes everything!**"""
    },
    'default': {
        'response': """I'm your Career AI Assistant! 🤖 I can help you with:

- **DSA Roadmap** - "Give me DSA roadmap"
- **Python** - "How to learn Python?"
- **SQL** - "SQL interview prep"
- **System Design** - "System design for interviews"
- **AI/ML** - "ML roadmap for beginners"
- **Resume Tips** - "How to improve my resume?"
- **Internships** - "How to get internship?"

Just ask your question naturally and I'll guide you! 🚀"""
    }
}


def get_bot_response(user_message: str, history: list = None) -> str:
    """
    Get chatbot response. Uses OpenAI API if key is configured,
    otherwise falls back to keyword-based responses.
    """
    if Config.USE_AI_CHATBOT and Config.OPENAI_API_KEY:
        return _openai_response(user_message, history or [])
    else:
        return _keyword_response(user_message)


def _keyword_response(message: str) -> str:
    """Keyword-based response system."""
    message_lower = message.lower().strip()

    # Greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'namaste']
    if any(g in message_lower for g in greetings):
        return """Hello! 👋 I'm CareerAI, your personal career assistant!

I'm here to help you with:
🗺️ **Roadmaps** for DSA, Python, SQL, System Design, AI/ML
📄 **Resume tips** and ATS optimization
💼 **Placement strategies** and interview prep
🎯 **Career guidance** for CSE students

What would you like to explore today?"""

    # Search through knowledge base
    for topic, data in CAREER_KB.items():
        if topic == 'default':
            continue
        if any(kw in message_lower for kw in data['keywords']):
            return data['response']

    # Handle specific question patterns
    if any(w in message_lower for w in ['how many days', 'how long', 'timeline', 'preparation time']):
        return """## Preparation Timeline ⏰

**6 Months Plan (Ideal)**
- Month 1-2: DSA Fundamentals
- Month 3: Advanced DSA + Projects
- Month 4: System Design
- Month 5: Domain specialization (ML/Web/Cloud)
- Month 6: Mock interviews + applications

**3 Months Intensive**
- Week 1-4: Array, String, LinkedList, Stack, Queue
- Week 5-8: Trees, Graphs, DP, Binary Search
- Week 9-10: System Design basics
- Week 11-12: Mock interviews + resume polish

**1 Month Crash Course**
- Focus only on NeetCode 150 (Easy + Medium)
- Apply to everything simultaneously
- Practice 4-6 problems/day minimum"""

    if any(w in message_lower for w in ['best', 'recommend', 'suggest', 'which']):
        return """## My Top Recommendations 🌟

**Best for Placements**
1. LeetCode (essential - 150+ problems)
2. NeetCode YouTube (best explanations)
3. Striver's SDE Sheet (systematic)

**Best for Concepts**
1. GeeksforGeeks (theory + practice)
2. Abdul Bari (algorithms deep dive)
3. MIT OpenCourseWare (academic rigor)

**Best Projects to Build**
1. Full-stack web app (React/Next.js + Backend)
2. ML project with deployment (HuggingFace Spaces)
3. CLI tool or automation script
4. Open source contribution

Ask me about any specific topic for a detailed roadmap!"""

    # Default response
    return CAREER_KB['default']['response']


def _openai_response(message: str, history: list) -> str:
    """Use OpenAI API for more intelligent responses."""
    try:
        import openai
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

        system_prompt = """You are CareerAI, an expert career counselor for Computer Science Engineering students in India.
You help with: DSA roadmaps, programming languages, system design, ML/AI, resume tips, interview prep, and internship strategies.
Keep responses concise, practical, and use markdown formatting with emojis for readability.
Focus on actionable advice. When giving roadmaps, be specific with timelines and resources."""

        messages = [{"role": "system", "content": system_prompt}]

        # Include recent history (last 6 messages to save tokens)
        for h in history[-6:]:
            messages.append({"role": h['role'], "content": h['message']})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        # Fall back to keyword responses
        return _keyword_response(message)
