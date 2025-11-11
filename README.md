# 🚀 Ideenfinder - Agent Factory for Project Planning

Transform your project ideas into structured, executable plans using parallel AI agents and context engineering.

## What is Ideenfinder?

Ideenfinder uses the **Agent Factory pattern** to analyze your project idea through 5 coordinated phases:

1. **Research** - Market analysis, competitors, opportunities
2. **Planning** - Features, tech stack, reusable components (parallel agents)
3. **Specification** - Consolidated project plan
4. **Validation** - Quality assessment and risk analysis
5. **Output** - JSON, Markdown, and Archon-ready formats

### Key Features

- ✅ **Parallel Agent Execution** - Phase 2 runs 3 agents simultaneously (Feature Planner, Techstack Analyzer, Reusability Scout)
- ✅ **Token-Efficient** - Separate context windows per agent (~11k tokens vs 20-30k traditional)
- ✅ **Structured Output** - JSON + Markdown + Archon import format
- ✅ **Archon Integration** - Queries RAG for similar projects and reusable components
- ✅ **Context Engineering** - Uses proven patterns from Agent Factory

---

## Quick Start

### 1. Installation

```bash
cd ~/ideenfinder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Initialize config files
python ideenfinder.py init

# Edit config.yaml - Add your API key
vim config.yaml
```

**Required**: Set your Anthropic API key in `config.yaml`:
```yaml
claude:
  api_key: "sk-ant-..."  # Your API key here
```

**Optional**: Enable Archon integration in `config.yaml`:
```yaml
archon:
  api_url: "http://localhost:8000"
  enabled: true
```

### 3. Run

```bash
# Interactive mode
python ideenfinder.py start

# Direct input
python ideenfinder.py start --idea "Trading bot with RSI indicators"

# Custom output directory
python ideenfinder.py start --idea "..." --output ./my-project
```

---

## Usage Examples

### Example 1: Interactive Mode

```bash
$ python ideenfinder.py start

🚀 Ideenfinder - Agent Factory

Tell me about your project idea:
💡 Your idea: A diet tracking app with barcode scanner and meal planning

Your Idea: A diet tracking app with barcode scanner and meal planning

Proceed with analysis? [Y/n]: y

Phase 0: Processing Idea Input
✓ Idea captured

Phase 1: Market Research
✓ Research completed

Phase 2: Parallel Planning (3 agents)
   ├─ Feature Planner ████████████ 100%
   ├─ Techstack Analyzer ████████████ 100%
   └─ Reusability Scout ████████████ 100%
✓ Planning completed

Phase 3: Generating Specification
✓ Specification generated

Phase 4: Validation
✓ Validation completed

Phase 5: Generating Outputs
✓ Outputs generated

✨ Project Specification Complete!

Generated Files:
  • json: ./outputs/20250110_150000/project-spec.json
  • markdown: ./outputs/20250110_150000/project-spec.md
  • archon: ./outputs/20250110_150000/archon-import.json

Next Steps:
  1. Review: less project-spec.md
  2. Import to Archon: Use archon-import.json
  3. Start coding with Claude Code!
```

### Example 2: Direct Input

```bash
python ideenfinder.py start \
  --idea "Mobile app for tracking workouts with AI-powered form correction" \
  --output ./workout-tracker

# Runs immediately, outputs to ./workout-tracker/
```

---

## Output Files

Each run generates three files:

### 1. `project-spec.json` - Structured Specification

```json
{
  "version": "1.0",
  "generated_at": "2025-01-10T15:00:00",
  "project": {
    "title": "Trading Bot",
    "description": "...",
    "type": "web-app"
  },
  "research": {
    "report": "## Market Analysis\n..."
  },
  "features": {
    "plan": "## MVP Features\n..."
  },
  "techstack": {
    "recommendations": "## Recommended Tech Stack\n..."
  },
  "reusability": {
    "assets": "## Reusable Assets\n...",
    "similar_projects": [...]
  },
  "validation": {
    "report": "## Validation Report\n..."
  }
}
```

### 2. `project-spec.md` - Human-Readable Report

Complete markdown document with:
- Market research findings
- Feature breakdown
- Tech stack recommendations
- Reusable components
- Validation assessment
- Next steps

### 3. `archon-import.json` - Archon Integration Format

Ready-to-import format for creating project in Archon:

```json
{
  "version": "1.0",
  "project": {
    "title": "Trading Bot",
    "description": "..."
  },
  "documents": [
    {
      "title": "Project Specification",
      "document_type": "spec",
      "content": {...}
    }
  ]
}
```

---

## Architecture

### Agent Workflow

```
┌─────────────────────────────────────────────────┐
│         ORCHESTRATOR                            │
└───────────────┬─────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │   Phase 0: Input      │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │   Phase 1: Research   │ (Research Agent)
    └───────────┬───────────┘
                │
    ┌───────────▼──────────────────────┐
    │   Phase 2: Parallel Planning     │
    ├──────────────────────────────────┤
    │  ⚡ Feature Planner               │
    │  ⚡ Techstack Analyzer            │
    │  ⚡ Reusability Scout             │
    │     (All run simultaneously)     │
    └───────────┬──────────────────────┘
                │
    ┌───────────▼───────────┐
    │   Phase 3: Spec Gen   │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │   Phase 4: Validation │ (Validator Agent)
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │   Phase 5: Output     │
    └───────────────────────┘
```

### Project Structure

```
ideenfinder/
├── ideenfinder.py          # CLI entry point
├── orchestrator.py         # Main workflow coordinator
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
│
├── agents/
│   ├── base_agent.py       # Base class
│   ├── research_agent.py   # Market research
│   ├── feature_planner.py  # Feature planning
│   ├── techstack_analyzer.py
│   ├── reusability_scout.py
│   └── validator_agent.py
│
├── utils/
│   ├── claude_api.py       # Claude API wrapper
│   ├── archon_rag.py       # Archon integration
│   └── parallel_executor.py # Parallel agent runner
│
├── templates/
│   ├── project-spec-schema.json
│   └── archon-import-schema.json
│
└── outputs/                # Generated specifications
    └── [timestamp]/
        ├── project-spec.json
        ├── project-spec.md
        └── archon-import.json
```

---

## Integration with Archon & Claude Code

### Workflow: Idea → Archon → Development

```bash
# 1. Generate specification
python ideenfinder.py start --idea "Trading Bot"

# 2. Review output
less outputs/20250110_150000/project-spec.md

# 3. Import to Archon (in Claude Code)
# Open archon-import.json and say:
"Create this project in Archon using archon-import.json"

# 4. Start development
# Claude Code now has structured plan with:
# - Market research context
# - Feature breakdown
# - Tech stack decisions
# - Reusable components identified
```

### Benefits

- **Context Continuity**: All research and decisions documented
- **Reusability**: Archon RAG finds similar past projects
- **Structured Tasks**: Ready-to-import task breakdown
- **Token Efficiency**: Claude Code starts with focused context

---

## Configuration Reference

### config.yaml

```yaml
claude:
  api_key: "your-api-key"
  model: "claude-sonnet-4"      # or claude-opus-4
  max_tokens: 4096
  temperature: 0.7

archon:
  api_url: "http://localhost:8000"
  enabled: true                 # Set false to disable RAG queries

output:
  directory: "./outputs"
  formats: ["json", "markdown"]
  include_validation: true

agents:
  research_tokens: 3000
  planning_tokens: 1500
  techstack_tokens: 1000
  reusability_tokens: 800
  validator_tokens: 1500
```

---

## Advanced Usage

### Custom Output Directory

```bash
python ideenfinder.py start \
  --idea "Your idea" \
  --output ~/projects/my-app
```

### Programmatic Usage

```python
from orchestrator import IdeenfinderOrchestrator
import asyncio

async def main():
    orchestrator = IdeenfinderOrchestrator()
    result = await orchestrator.run_ideation(
        idea_input="Trading bot with RSI indicators",
        output_dir="./my-project"
    )

    print(f"Spec: {result['specification']}")
    print(f"Output: {result['output_directory']}")

asyncio.run(main())
```

---

## Token Usage & Costs

### Estimated Token Consumption

| Phase | Agent(s) | Tokens | Parallel? |
|-------|----------|--------|-----------|
| 1 | Research | 2,500 | No |
| 2 | Feature Planner | 1,500 | ⚡ Yes |
| 2 | Techstack Analyzer | 1,000 | ⚡ Yes |
| 2 | Reusability Scout | 800 | ⚡ Yes |
| 3 | Consolidation | 2,000 | No |
| 4 | Validator | 1,500 | No |
| 5 | Output | 500 | No |
| **Total** | | **~10-12k** | |

**Cost Estimate** (Claude Sonnet 4):
- Input: ~8k tokens (~$0.06)
- Output: ~4k tokens (~$0.30)
- **Total: ~$0.36 per ideation**

### Comparison

- Traditional single prompt: 20-30k tokens (~$1.50)
- **Savings: ~75%** 💰

---

## Troubleshooting

### "API Key not found"

Make sure `config.yaml` exists and contains your API key:
```bash
python ideenfinder.py init
vim config.yaml  # Add API key
```

### "Archon RAG query failed"

Archon integration is optional. If you see warnings, either:
1. Set `archon.enabled: false` in config.yaml
2. Start Archon server: check Archon documentation

### "Import Error"

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Roadmap

### v1.1 (Next)
- [ ] Confidence scores per phase
- [ ] Interactive refinement loops
- [ ] Project templates (web-app, cli-tool, etc.)
- [ ] Enhanced Archon task generation

### v2.0 (Future)
- [ ] MCP Server version
- [ ] Multi-approach comparison
- [ ] Learning from past projects
- [ ] Web UI with Streamlit

---

## Credits

Inspired by:
- [Agent Factory Pattern](https://github.com/coleam00/context-engineering-intro)
- [Context Engineering](https://github.com/coleam00/context-engineering-intro)
- [Pydantic AI](https://ai.pydantic.dev/)

Built for integration with:
- [Archon](https://github.com/your-archon-repo) - Project management with RAG
- [Claude Code](https://claude.com/claude-code) - AI coding assistant

---

## License

MIT License - See LICENSE file

---

## Support

Issues? Questions?
- Check troubleshooting section above
- Review example outputs in `outputs/`
- Ensure API key and config are correct

---

**Happy Building! 🚀**
