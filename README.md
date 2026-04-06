# CreatorBridge

**CreatorBridge** is a hybrid social media automation system that connects content creation, AI-assisted adaptation, and multi-platform publishing.

It uses **Google Sheets as a structured database**, **local LLMs (Llama 3.1 via Ollama)** for content generation, and a **Python-based automation engine** to manage scheduling and publishing.

The system is designed around a **human-in-the-loop workflow**, ensuring both efficiency and control.

---

## Key Concept

CreatorBridge is not just an automation tool. It is a **workflow system**:

> Human writes → AI adapts → System publishes

- Human creates the original content (LinkedIn-style)
- AI generates platform-specific drafts (Instagram, Facebook, Mastodon)
- System automatically publishes approved content at the scheduled time

---

## System Architecture

The system follows a simple but scalable 3-layer design:

### 1. Data Layer
- **Google Sheets** as the central database
- Stores:
  - Original content
  - AI-generated content
  - Status (`draft`, `review`, `approved`)
  - Scheduling time
  - Posting status (`Yes/No`)
  - Error logs and live links

---

### 2. Intelligence Layer
- **Local LLM (Llama 3.1 via Ollama)**
- Generates platform-specific content:
  - Instagram → shorter, visual tone
  - Facebook → community-oriented
  - Mastodon → concise, technical
- Runs locally for:
  - privacy
  - zero API cost

---

### 3. Execution Layer
- **Python automation script**
- Responsible for:
  - scanning the sheet
  - filtering valid posts
  - calling platform APIs
  - updating status

---

### 4. Scheduling Layer
- **GitHub Actions (planned / optional)**
- Runs every 15–30 minutes
- Enables:
  - fully automated posting
  - system works even when local machine is offline

---

## Workflow (State Machine)

- The system is built around a clear state flow: Draft → Review → Approved → Published

### Draft
- User writes original content

### Review
- AI generates platform-specific drafts
- User reviews and edits

### Approved
- Content is ready to be published
- Scheduled time is set

### Published
- System posts content automatically
- Status updated to prevent duplication

---

## Core Features

### AI-Assisted Content Adaptation
- Uses **Llama 3.1 (local)** for multi-platform formatting
- Adapts tone, length, and structure
- Keeps human in control (no auto-post without approval)

---

### Structured Content Management
- Google Sheets acts as a lightweight CMS
- Easy to edit, track, and collaborate
- No need for a complex database

---

### Automated Publishing
- Multi-platform posting:
  - LinkedIn 
  - Instagram 
  - Facebook 
  - Mastodon 
- Prevents duplicate posts using status flags

---

### Safety Mechanisms
- Double validation before publishing:
  - `status == approved`
  - `posted == No`
- Error logging system
- Live link tracking after publishing

---

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **Database**: Google Sheets API (`gspread`)
- **AI**: Ollama (Llama 3.1:8B)
- **Automation**: GitHub Actions
- **Hardware**: Mac Mini (local inference)

---

## Quick Start

### 1. Install Ollama
```bash
ollama pull llama3.1
```

### 2. Clone the repo
```bash
git clone https://github.com/sophiapyx/CreatorBridge.git
cd CreatorBridge
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
Create a .env file:
GOOGLE_SHEET_ID=your_sheet_id
MASTODON_TOKEN=your_token
```

### 5. Run the system
```bash
python main.py

```

##  Current Limitations

- **Media Hosting Constraints (Instagram API)**  
  Instagram Graph API requires a stable, publicly accessible direct media URL.  
  Dynamic links (e.g., Google Drive) can expire or fail to resolve, requiring additional handling or external hosting (e.g., GitHub raw URLs).

- **API Reliability & Token Management**  
  Some platforms (especially Instagram and Facebook) require periodic token refresh and may introduce instability during long-term automation.

- **Limited Video Support**  
  While image and text posting is fully supported, video publishing workflows are not yet implemented across all platforms.

- **Rate Limiting & Throughput Control**  
  Posting multiple items in a short time window may trigger platform rate limits, requiring manual throttling (e.g., delays between API calls).

- **UI–Backend Coupling**  
  The current Streamlit interface directly interacts with Google Sheets, which may limit scalability for larger teams or higher content volume.

## Future Work

- **Advanced Video Publishing Support**  
  Extend the system to support video content across platforms such as Instagram Reels, Facebook Video, and LinkedIn Video posts.

- **Improved Media Pipeline**  
  Develop a more robust media handling system (e.g., CDN integration or dedicated storage service) to ensure stable and scalable asset delivery.

- **AI Prompt Optimization & Fine-Tuning**  
  Improve prompt design and introduce lightweight fine-tuning to generate more platform-specific, high-quality content with better consistency.

- **Decoupled Backend Architecture**  
  Replace Google Sheets with a more scalable backend (e.g., database + API layer) for better performance and multi-user collaboration.

- **Intelligent Scheduling System**  
  Enhance scheduling logic with priority handling, batching strategies, and adaptive timing based on platform engagement patterns.

- **Analytics & Feedback Loop**  
  Integrate performance tracking (e.g., engagement metrics) to enable data-driven content optimization and AI-assisted iteration.

- **Multi-user Collaboration System**  
  Introduce role-based access (e.g., editor, reviewer, publisher) to support team workflows in larger content production environments.

## Project Context
This project was developed for: IAT 460_Generative AI，Simon Fraser University (SFU).

## Final Note
CreatorBridge demonstrates how AI, automation, and human control can be combined into a practical system for real-world content workflows.
It is not just about generating content，it is about building a reliable publishing pipeline.
