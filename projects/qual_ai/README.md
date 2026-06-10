# QUAL-AI - Qualitative Research Analysis Agent

An expert qualitative research analyst powered by Google's Gemini-3.5-Flash model, designed to conduct rigorous, transparent, and evidence-based qualitative analysis.

## Overview

QUAL-AI transforms large volumes of unstructured qualitative data into meaningful, traceable, and actionable insights while preserving the richness and nuance of human experiences.

## Features

### Core Capabilities
- **Thematic Analysis** - Identify patterns and themes from qualitative data
- **Grounded Theory** - Build theories grounded in evidence
- **Narrative Analysis** - Interpret participant stories and experiences
- **Content Analysis** - Systematic analysis of text and communication
- **Evidence-Based Insights** - Generate conclusions backed by data
- **Contradiction Detection** - Surface tensions, contradictions, and minority viewpoints
- **Segmentation Analysis** - Identify meaningful participant segments

### Supported Data Sources
- Interview transcripts
- Focus group discussions
- Open-ended survey responses
- Ethnographic observations
- Field notes
- Community discussions
- Social media conversations
- WhatsApp chats & forum discussions
- Customer feedback
- User research data
- Reports & PDFs
- Audio/video transcripts
- Multi-source datasets

## Architecture

### Components
- **agents.py** - Core agent definition with `GlobalGemini` client and `root_agent`
- **app.py** - FastAPI server for REST API access
- **main.py** - Direct execution script for command-line usage

### GlobalGemini Class
Custom Gemini integration that routes requests to Google's global endpoint, enabling access to `gemini-3.5-flash` series models regardless of regional AgentEngine instances.

## Installation

```bash
pip install -r requirements.txt
```

### Requirements
- `google-adk` - Google Agent Development Kit
- `google-genai` - Google Generative AI client
- `google-cloud-aiplatform` - Vertex AI platform support
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `python-dotenv` - Environment configuration

## Usage

### Option 1: Direct Execution
```bash
python main.py
```

### Option 2: REST API Server
```bash
python app.py
```

Server starts on `http://localhost:8000`

#### API Endpoints

**GET** `/` - Health check and API info
```json
{
  "agent": "Agent_Studio_agent___10_06_2026",
  "status": "active",
  "model": "gemini-3.5-flash"
}
```

**GET** `/agent` - Detailed agent information
```json
{
  "name": "Agent_Studio_agent___10_06_2026",
  "model": "gemini-3.5-flash",
  "description": "Expert qualitative research analyst"
}
```

**POST** `/analyze` - Analyze qualitative data
```json
{
  "data": "interview transcript or qualitative data",
  "data_type": "interview_transcript",
  "context": "optional research context"
}
```

**POST** `/batch-analyze` - Batch analyze multiple datasets
```json
[
  {"data": "...", "data_type": "interview_transcript"},
  {"data": "...", "data_type": "survey_response"}
]
```

**GET** `/health` - Health check

## Analysis Framework

### 5-Stage Research Thinking Process

1. **Understanding** - Comprehend the data context, speakers, emotions, and motivations
2. **Coding** - Generate concise, descriptive codes close to participant language
3. **Categorization** - Group codes into broader concepts and relationships
4. **Theme Development** - Identify higher-order themes with supporting evidence
5. **Interpretation** - Explain patterns, underlying beliefs, and implications

### Data Reduction Strategy

- **Phase 1**: Retain ~40% of responses (richness & diversity)
- **Phase 2**: Retain ~10% of responses (strongest evidence)
- **Phase 3**: Identify strategically important findings for decision-making

### Quality Standards

- Analytical rigor and transparency
- Evidence-backed reasoning
- Traceability between data and conclusions
- Interpretive depth beyond summarization
- Active contradiction detection

## Output Structure

1. Research Context
2. Dataset Overview
3. Participant Segmentation
4. First-Level Codes
5. Second-Level Themes
6. Theme Relationships
7. Key Supporting Evidence
8. Contradictions and Outliers
9. Top Strategic Findings
10. Interpretations
11. Recommendations
12. Confidence Assessment
13. Executive Summary

## Analytical Philosophy

- All insights emerge from the data
- Themes allowed to emerge naturally
- Openness to unexpected patterns
- Minority opinions valued equally
- No confirmation bias
- No overgeneralization
- Never invent or fabricate evidence

## Configuration

### Environment Variables
- `PORT` - Server port (default: 8000)
- `GOOGLE_APPLICATION_CREDENTIALS` - GCP service account JSON path

### Google Cloud Setup

Ensure you have:
1. GCP project with Vertex AI enabled
2. Service account with appropriate permissions
3. `GOOGLE_APPLICATION_CREDENTIALS` environment variable set

## Example Usage

```python
from agents import root_agent

# The agent is now ready for use
print(root_agent.name)
# Output: Agent_Studio_agent___10_06_2026

print(root_agent.model.model)
# Output: gemini-3.5-flash
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
- Single agent design
- No sub-agents (extensible)
- Tool-based architecture (currently empty, extensible)

## Future Enhancements

- Tool integration for data fetching
- Multi-agent orchestration
- Advanced visualization
- Export to multiple formats
- Collaborative annotation support

## License

All rights reserved.

## Support

For issues or questions, refer to the Google ADK documentation or contact the development team.
