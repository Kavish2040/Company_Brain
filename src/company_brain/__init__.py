"""company_brain — a company knowledge graph in canonical markdown."""

from dotenv import load_dotenv

# Loaded here rather than in app.py so *every* entry point gets it: the CLI, the
# MCP server, the FastAPI app, and any script that imports a single module.
# Keeping it in the composition root meant a script importing extract.claude
# directly got no credentials and failed with an auth error instead.
# override=False so an explicitly exported variable always wins over the file.
load_dotenv(override=False)
