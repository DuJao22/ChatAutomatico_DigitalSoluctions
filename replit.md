# Digital Soluctions - AI Chat Lead Capture System

## Overview

Digital Soluctions is a professional AI-powered chat system designed to capture business leads through intelligent conversation. The application uses Google's Gemini AI to conduct natural language conversations, extracting user information (name and phone number) before redirecting them to relevant business solutions pages.

The system identifies the user's business niche through URL parameters (`?tag=`) and provides personalized responses based on their interests. All leads are stored in a SQLite database for follow-up.

**Core Purpose:** Automated lead generation with AI-driven conversation flows

**Primary Technologies:**
- Backend: Python 3.x + Flask
- Frontend: HTML5 + Tailwind CSS + Vanilla JavaScript
- Database: SQLite3 (native Python driver)
- AI: Google Gemini API
- Design Pattern: Mobile-first WhatsApp-style chat interface

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

**Multi-file Flask Application:**
- `main.py` - Application entry point (imports and runs Flask app)
- `app.py` - Core Flask application with routing logic
- `db_init.py` - Database initialization and data access layer
- `gemini.py` - AI integration module for natural language processing
- `leads.db` - SQLite database (auto-created on first run)

### Frontend Architecture

**Template-Based Rendering with AJAX:**
- Uses Jinja2 templating engine with base template inheritance
- `base.html` - Shared layout with header, fonts, and Tailwind CDN
- `chat.html` - Main chat interface with message container
- `thankyou.html` - Post-submission confirmation page
- AJAX-based chat interaction (no page reloads during conversation)

**Design System:**
- Tailwind CSS via CDN (no build step required)
- Custom CSS animations in `static/css/style.css`
- Mobile-first responsive design targeting WhatsApp aesthetic
- Google Fonts (Inter family) for typography
- Color scheme: Blue (#2563eb) primary, purple gradient for user messages

### Backend Architecture

**Flask Application (app.py):**
- Session-based conversation state management
- Route handlers for chat interface and AJAX message endpoint
- Environment variable validation on startup (fails fast if missing secrets)
- Niche-based routing logic using tag parameters

**Conversation Flow:**
1. User arrives with optional `?tag=` parameter (identifies business niche)
2. System requests name via AI chat
3. System requests phone number
4. Lead saved to database
5. User redirected to niche-specific landing page

**State Machine:**
- `currentStep` tracked client-side: 'name' → 'phone' → 'complete'
- Server validates and extracts information using regex patterns in `gemini.py`

### Data Storage Solutions

**SQLite3 Database (db_init.py):**
- Single table schema: `leads` table
- Fields: id (autoincrement), name, phone, tag, created_at (timestamp)
- No ORM - uses native Python `sqlite3` module for direct SQL execution
- Database file: `leads.db` in project root
- Auto-initialization on first application start

**Schema Design Rationale:**
- Lightweight solution for lead capture (no complex relationships needed)
- Timestamp tracking for lead conversion analytics
- Tag field enables segmentation by marketing campaign/niche

### AI Integration

**Google Gemini API (gemini.py):**
- Uses `google-genai` Python SDK
- Function: `extract_user_info()` - Regex-based extraction of name/phone from natural language
- Function: `ask_gemini()` - **Intelligent sales consultant** that understands niche-specific pain points and suggests strategic solutions
- Function: `get_product_link()` - Identifies products/services mentioned in messages
- API key stored in environment variable: `GEMINI_API_KEY`

**AI Sales Strategy (Updated Nov 2025):**
The AI acts as a strategic sales consultant that:
1. **Identifies the niche** based on the `tag` parameter
2. **Understands pain points** specific to each business type (barbearias, restaurantes, e-commerce, etc.)
3. **Suggests primary solutions** that address the main problem
4. **Recommends complementary services** (cross-sell/upsell) that multiply results
5. **Explains the "why"** behind each recommendation (consultative approach)

**Niche-Specific Intelligence:**
The AI has built-in knowledge about common pain points for:
- **Barbearias:** Disorganized schedules, no-shows, financial control
- **Restaurantes/Hamburguerias:** Outdated menus, WhatsApp chaos, competition with iFood
- **E-commerce:** Low conversion rates, expensive traffic, cart abandonment
- **Marketing:** Poor ROI, unmeasured campaigns
- **Tecnologia/Startups:** Slow MVPs, lack of automation
- **Consultoria:** Lack of online authority, empty schedules

**Information Extraction Strategy:**
- Hybrid approach: Regex patterns + AI understanding
- Phone patterns: Supports Brazilian format (10-11 digits with optional formatting)
- Name patterns: Multiple regex patterns to catch common Portuguese language structures
- Fallback to AI when regex fails

**Personalized First Message:**
Based on the `tag` parameter, the chat displays a personalized greeting:
- Example: `/?tag=barbearia` → "Hum... bom saber que você veio para conhecer sobre soluções para barbearias! 🎯"
- Supports 30+ different niches/services (see `NICHO_MENSAGENS` in app.py)

### Session Management

**Flask Sessions:**
- Secret key required via `SESSION_SECRET` environment variable
- Stores conversation state and extracted user information
- Enables multi-step form flow without database writes until completion

**Security Consideration:**
- Application exits on startup if `SESSION_SECRET` not configured
- Prevents deployment with weak/default session keys

### Routing and Redirection

**Dynamic URL Mapping (NICHO_URLS in app.py):**
- Maps business niches to specific landing pages
- All current niches redirect to main site sections
- Default fallback to homepage
- Extensible design for future niche-specific pages

**Niche Identification:**
- URL parameter: `?tag=marketing`, `?tag=tecnologia`, etc.
- Enables campaign tracking and personalized conversation starters

## External Dependencies

### Third-Party APIs

**Google Gemini AI:**
- Service: Generative AI API for conversational responses
- Authentication: API key via environment variable
- SDK: `google-genai` Python package
- Usage: Natural language understanding and response generation
- Obtain key: https://aistudio.google.com/app/apikey

### Frontend Libraries (CDN-based)

**Tailwind CSS:**
- Version: Latest (loaded via CDN)
- URL: `https://cdn.tailwindcss.com`
- Purpose: Utility-first CSS framework for responsive design

**Google Fonts:**
- Font Family: Inter (weights: 300, 400, 500, 600, 700)
- Purpose: Modern, readable typography

### Python Packages

Required packages (install via pip/replit packages):
- `flask` - Web framework
- `python-dotenv` - Environment variable management
- `google-genai` - Google Gemini AI SDK

**Standard Library Dependencies:**
- `sqlite3` - Database operations (built-in)
- `os`, `sys` - Environment and system operations
- `re` - Regular expression pattern matching
- `json` - JSON handling for API interactions

### Environment Variables (Required)

**Critical Configuration:**
1. `GEMINI_API_KEY` - Google Gemini API authentication
   - Required: Yes (app exits if missing)
   - Source: Google AI Studio
   
2. `SESSION_SECRET` - Flask session encryption key
   - Required: Yes (app exits if missing)
   - Recommendation: Generate strong random string (32+ characters)

**Deployment Notes:**
- Application validates environment variables on startup
- Missing required variables trigger immediate exit with error message
- Design choice: Fail-fast approach prevents insecure deployments

### External Redirects

**Landing Pages:**
- Main site: `https://fullstackdavi.github.io/DigitalSoluctions/`
- Services section: `https://fullstackdavi.github.io/DigitalSoluctions/#services`
- Post-chat redirect destination based on captured niche tag