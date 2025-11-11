# ⚡ Quick Start Guide

Get Ideenfinder running in 5 minutes!

## Step 1: Setup (2 min)

```bash
cd ~/ideenfinder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize config
python ideenfinder.py init
```

## Step 2: Configure (1 min)

Edit `config.yaml` and add your Anthropic API key:

```yaml
claude:
  api_key: "sk-ant-your-key-here"  # ← Add your key
```

Get your API key from: https://console.anthropic.com/

## Step 3: Run (2 min)

```bash
python ideenfinder.py start
```

Enter your idea when prompted, and watch the agents work!

## Example Run

```bash
$ python ideenfinder.py start

💡 Your idea: Trading bot with RSI divergence detection

Phase 1: Market Research... ✓
Phase 2: Parallel Planning... ✓
Phase 3: Specification... ✓
Phase 4: Validation... ✓
Phase 5: Output... ✓

✨ Done! Check outputs/[timestamp]/
```

---

## What You Get

- `project-spec.json` - Full structured specification
- `project-spec.md` - Human-readable report
- `archon-import.json` - Ready for Archon import

---

## Next Steps

1. **Review**: `less outputs/[timestamp]/project-spec.md`
2. **Import to Archon**: Use with Claude Code
3. **Start Building**: Follow the generated plan!

---

## Need Help?

- Check `README.md` for full documentation
- Troubleshooting section in README
- Verify your API key in config.yaml

**Happy Building! 🚀**
