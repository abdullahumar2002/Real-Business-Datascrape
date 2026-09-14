# Business Lead Agent

AI-powered business research and verification system for collecting real, publicly verifiable business information from UAE and USA.

## ⚠️ DATA INTEGRITY WARNING

**THIS SYSTEM NEVER FABRICATES DATA.**

- No fake business names
- No invented phone numbers
- No generated email addresses
- No constructed websites
- No fabricated ratings or reviews
- No made-up addresses

Every record must have a traceable source URL. If information cannot be found or verified, fields remain EMPTY.

## Features

- **Real Data Collection**: Only collects verifiable business information from permitted public sources
- **Source Traceability**: Every record includes source URL and verification status
- **Website Verification**: Checks official websites and extracts contact information
- **Deduplication**: Advanced duplicate detection using multiple criteria
- **Lead Scoring**: Scores businesses as potential digital-service leads
- **Multiple Export Formats**: CSV, Excel, JSON, PDF
- **Resume Support**: Survives interruptions and continues from existing data
- **Rate Limiting**: Respectful crawling with configurable delays
- **Robots/Terms Compliance**: Respects robots.txt and terms of service

## Project Structure

```
business-lead-agent/
├── agent.py                 # Main CLI interface
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
│
├── config/
│   ├── settings.yaml       # Application configuration
│   └── sources.yaml        # Data sources configuration
│
├── src/
│   ├── __init__.py
│   ├── database.py         # Database management
│   ├── models.py           # Database models
│   ├── crawler.py          # Web crawler with rate limiting
│   ├── source_manager.py   # Source configuration management
│   ├── robots.py           # Robots.txt checker
│   ├── parser.py           # Business data parser
│   ├── normalizer.py       # Data normalization
│   ├── website_checker.py  # Website verification
│   ├── deduplicator.py     # Duplicate detection
│   ├── ai_agent.py         # AI classification (optional)
│   ├── lead_scoring.py     # Lead scoring system
│   ├── csv_importer.py     # CSV data import
│   ├── exporters.py        # Data export (CSV, Excel, JSON)
│   ├── pdf_report.py       # PDF report generation
│   └── statistics.py       # Statistics and reporting
│
├── data/
│   ├── raw/                # Raw data storage
│   └── business.db         # SQLite database
│
├── output/                 # Exported files
├── logs/                   # Application logs
└── tests/                  # Test suite
    ├── test_normalizer.py
    ├── test_deduplicator.py
    ├── test_email.py
    └── test_phone.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**

```bash
cd business-lead-agent
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key if you want to use AI features:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

AI features are optional - the system will use rule-based fallbacks if no API key is provided.

5. **Configure sources**

Edit `config/sources.yaml` to add permitted data sources:

```yaml
sources:
  - name: "Your Business Directory"
    country: "UAE"
    url: "https://example-directory.com"
    source_type: "directory"
    allowed: true
    priority: 1
    parser: "generic"
    automation_allowed: true
    requires_manual_export: false
```

**IMPORTANT**: Only configure sources that permit automated data collection. If a source prohibits automation, set `allowed: false` and use CSV import instead.

## Usage

### Basic Commands

**Run full collection process:**

```bash
python agent.py --target 500
```

**Process specific country:**

```bash
python agent.py --country UAE --target 250
python agent.py --country USA --target 250
```

**Resume from existing data:**

```bash
python agent.py --resume
```

**Verify existing businesses:**

```bash
python agent.py --verify
```

**Export existing data:**

```bash
python agent.py --export
```

**Import from CSV:**

```bash
python agent.py --import-csv data/raw/businesses.csv
```

**Generate PDF report:**

```bash
python agent.py --pdf
```

**Show statistics:**

```bash
python agent.py --stats
```

### CSV Import Format

Create a CSV file with the following columns (flexible naming supported):

```csv
name,category,address,city,state,country,phone,email,website,rating,review_count,source_url
"ABC Company LLC","Construction","123 Main St","Dubai","Dubai","UAE","+971-4-123-4567","info@abccompany.com","https://abccompany.com",4.5,25,"https://directory.com/abc-company"
```

Supported column name variations:
- `name`, `business_name`, `company`, `title`
- `phone`, `telephone`, `tel`
- `email`, `email_address`
- `website`, `url`, `site`

### Configuration

Edit `config/settings.yaml` to customize:

```yaml
targets:
  total: 500
  uae: 250
  usa: 250

rate_limiting:
  delay_min: 2
  delay_max: 5
  timeout: 30
  max_retries: 3

lead_scoring:
  no_website: 20
  outdated_website: 15
  unreachable_website: 15
  has_public_email: 10
  has_public_phone: 10
  established_local: 10
  many_reviews: 5
  high_value_category: 5
```

## Output Files

The system generates the following files in the `output/` directory:

- `verified_businesses.csv` - All verified businesses in CSV format
- `verified_businesses.xlsx` - Excel file with multiple sheets:
  - All Businesses
  - UAE
  - USA
  - High Priority Leads
  - No Website
  - Website Verified
  - Rejected
  - Duplicates
  - Statistics
- `verified_businesses.json` - JSON format with metadata
- `verified_businesses.pdf` - Professional PDF report
- `verification_report.json` - Verification statistics

## Data Verification Methodology

### Source Traceability

Every record includes:
- `source` - Name of the data source
- `source_url` - Original URL where data was found
- `source_type` - Type of source (directory, api, csv)
- `source_verified` - Whether source was verified

### Verification Status Levels

- `DIRECTORY_ONLY` - Business exists in directory but website not verified
- `DIRECTORY_PLUS_WEBSITE` - Directory listing with website URL
- `WEBSITE_VERIFIED` - Website responds and appears to belong to business
- `MULTI_SOURCE_VERIFIED` - Multiple independent sources support the business
- `REJECTED` - Record rejected due to invalid data or issues

### Website Verification

For each business with a website:
- HTTP/HTTPS status check
- Domain validation
- Page title extraction
- Business name matching
- Contact page detection
- Email/phone extraction from official site
- Website quality scoring

### Deduplication

Priority order for duplicate detection:
1. Exact website domain
2. Exact phone number
3. Exact normalized email
4. Business name + city
5. Business name + address

When uncertain, businesses are marked as `duplicate: "possible"` rather than deleted.

### Lead Scoring

Score range: 0-100

Factors:
- +20: No website
- +15: Outdated website
- +15: Unreachable website
- +10: Weak online presence
- +10: Has public email
- +10: Has public phone
- +10: Established local business
- +5: Many reviews
- +5: High-value category

Priority levels:
- High: 70+ points
- Medium: 40-69 points
- Low: 0-39 points

## Responsible Crawling Limitations

This system respects the following limitations:

### Robots.txt Compliance

- Checks robots.txt before crawling
- Respects disallowed paths
- Stops if automation is prohibited

### Terms of Service

- Does not bypass CAPTCHA
- Does not bypass Cloudflare
- Does not bypass login requirements
- Does not bypass paywalls
- Does not bypass API authentication
- Respects rate limits
- Does not bypass anti-bot systems

### Rate Limiting

- Default delay: 2-5 seconds between requests
- Configurable via environment variables
- Exponential backoff for retries
- Maximum 3 retries for temporary failures

### Non-Destructive Requests

- Only uses GET/HEAD requests
- No POST/PUT/DELETE operations
- No form submissions
- No authentication attempts

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python -m unittest tests/test_normalizer.py
python -m unittest tests/test_deduplicator.py
python -m unittest tests/test_email.py
python -m unittest tests/test_phone.py
```

## Troubleshooting

### Database Issues

If you encounter database errors:

```bash
rm data/business.db
python agent.py --resume
```

### Import Errors

If you get import errors, ensure you're in the project directory and the virtual environment is activated:

```bash
cd business-lead-agent
source venv/bin/activate
pip install -r requirements.txt
```

### Logging

Check logs for detailed error information:

```bash
cat logs/agent.log
```

### API Key Issues

If AI features fail without an API key, this is expected. The system will use rule-based fallbacks. To use AI features:

1. Get an OpenAI API key from https://platform.openai.com/
2. Add it to your `.env` file:
   ```env
   OPENAI_API_KEY=your_key_here
   ```

## Security

- Never commit `.env` file
- Never hardcode API keys
- Database file is excluded from git
- Output files are excluded from git
- Logs may contain sensitive information

## Adding Authorized Sources

To add a new data source:

1. Edit `config/sources.yaml`
2. Add a new source entry:

```yaml
- name: "New Business Directory"
  country: "UAE"
  url: "https://new-directory.com"
  source_type: "directory"
  allowed: true
  priority: 1
  parser: "generic"
  automation_allowed: true
  requires_manual_export: false
```

3. If the source requires custom parsing, create a parser in `src/parser.py`
4. Update the `parser` field to match your custom parser name

**Important**: Only add sources that explicitly permit automated data collection in their terms of service.

## License

This project is provided as-is for educational and legitimate business research purposes. Users are responsible for ensuring compliance with all applicable laws, terms of service, and robots.txt directives of any websites they interact with.

## Support

For issues or questions:
1. Check the logs in `logs/agent.log`
2. Review this README
3. Ensure all dependencies are installed
4. Verify your configuration files

## Data Integrity Commitment

This system is designed with a zero-tolerance policy for data fabrication:

- **No invented businesses** - Every business must come from a verifiable source
- **No fake contact details** - Phone, email, and website must be publicly displayed
- **No fabricated ratings** - Ratings only from actual source data
- **No duplicate filler** - Never duplicate records to reach targets
- **Source traceability** - Every record has a traceable source URL

If the system finds 437 verified businesses, it outputs 437 - not 500.

The target is a goal, not permission to fabricate.
