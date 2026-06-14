"""
EX4 (REAL Agent SDK) — a coordinator that delegates to subagents via the real Task tool.

Each subagent OWNS a scoped in-process tool (D2.3); the coordinator's job is to DELEGATE
(D1.2 hub-and-spoke), and the SDK gives each subagent ISOLATED context automatically (D1.2).
This is the genuine mechanism the exam tests — not the raw-API simulation in coordinator.py.

Cheap by design: runs on Haiku with a turn cap (the lesson is the orchestration, not model IQ).
Uses claude-agent-sdk, which spawns the `claude` CLI on your Claude Code auth (real usage).

This is the PRIMARY EX4 artifact for the orchestration mechanism. The reliability layer the
exam also tests here — D5.3 structured error propagation, D5.4 manifest/crash-recovery, D5.6
provenance + conflict annotation — lives in the `coordinator.py` companion (a raw-API
hub-and-spoke that stages those D5 concepts deterministically and cheaply, with toggles).

Run:  cd ccaf-prep/exercises/04-multi-agent-research && uv run python coordinator_sdk.py

Maps to: D1.2 hub-and-spoke + isolated context · D1.3 Task + allowedTools + AgentDefinition
         · D2.3 per-subagent scoped tools.  (D5.3/5.4/5.6 -> coordinator.py)
"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from claude_agent_sdk import (
    query, tool, create_sdk_mcp_server, ClaudeAgentOptions, AgentDefinition,
    AssistantMessage, ToolUseBlock, ResultMessage, SystemMessage,
)

# Portable .env discovery (no machine paths): nearest .env walking up, else the sibling course .env.
_env = find_dotenv(filename=".env", usecwd=True)
if not _env:
    for _p in Path(__file__).resolve().parents:
        if (_p / "claude-with-anthropic-api" / ".env").exists():
            _env = str(_p / "claude-with-anthropic-api" / ".env"); break
load_dotenv(_env)
MODEL = "haiku"   # cheap on purpose


# --- D2.3: two scoped in-process tools (canned data stands in for real backends) ---
# Match on a substring so "Tokyo", "Tokyo, Japan", etc. all hit the same canned record.
@tool("get_weather", "Get a city's current weather.", {"city": str})
async def get_weather(args):
    text = "18C, cloudy" if "tokyo" in args["city"].lower() else "15C, rainy"
    return {"content": [{"type": "text", "text": text}]}


@tool("get_landmark", "Get a city's single most famous landmark.", {"city": str})
async def get_landmark(args):
    text = "Tokyo Tower (333m)" if "tokyo" in args["city"].lower() else "unknown"
    return {"content": [{"type": "text", "text": text}]}


research = create_sdk_mcp_server("research", tools=[get_weather, get_landmark])
W, L = "mcp__research__get_weather", "mcp__research__get_landmark"

# --- D1.3: each subagent is an AgentDefinition with its OWN scoped tool + isolated context ---
AGENTS = {
    "weather": AgentDefinition(
        description="Researches a city's weather.",
        prompt="Call get_weather for the city, then report it in ONE short sentence.",
        tools=[W], model=MODEL),
    "landmark": AgentDefinition(
        description="Researches a city's famous landmark.",
        prompt="Call get_landmark for the city, then report it in ONE short sentence.",
        tools=[L], model=MODEL),
}


async def main():
    options = ClaudeAgentOptions(
        model=MODEL,
        mcp_servers={"research": research},
        agents=AGENTS,
        # allowed_tools is the GLOBAL execution allow-list (best practice — no bypass): it must
        # permit "Task" (the documented spawn contract) AND the MCP data tools the subagents run,
        # or those tool calls get denied. What enforces hub-and-spoke is each subagent's
        # AgentDefinition.tools scope (the weather subagent is scoped to [W] and cannot call
        # get_landmark — the SDK enforces it).
        allowed_tools=["Task", W, L],          # D1.3: include "Task"; list the subagents' tools
        permission_mode="default",             # REAL permissioning — NOT bypassPermissions
        max_turns=12,                           # cost backstop
    )
    prompt = (
        "You are a research COORDINATOR. Delegate to the `weather` subagent and the `landmark` "
        "subagent (via the Task tool, one each) to get Tokyo's weather and most famous landmark, "
        "then give ONE two-sentence briefing combining their findings."
    )

    spawned, tool_calls = [], []
    async for msg in query(prompt=prompt, options=options):
        # A subagent spawn surfaces as a SystemMessage(subtype="task_started") — NOT a
        # ToolUseBlock named "Task". That is the real delegation signal.
        if isinstance(msg, SystemMessage) and getattr(msg, "subtype", None) == "task_started":
            sub = msg.data.get("subagent_type")
            spawned.append(sub)
            print(f"[coordinator -> Task spawns subagent]: {sub!r}")
        elif isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, ToolUseBlock) and b.name.startswith("mcp__research__"):
                    tool_calls.append(b.name)
                    print(f"   [scoped data tool fired]: {b.name}")
        elif isinstance(msg, ResultMessage):
            print("\n[FINAL BRIEFING]\n" + (msg.result or "(none)"))
            cost = f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "n/a"
            print(f"\n(real run on {MODEL}: turns={msg.num_turns}, cost={cost})")

    print(f"\nTask spawned subagents? {bool(spawned)} -> {spawned}")
    print(f"Scoped subagent tools fired? {bool(tool_calls)} -> {tool_calls}")


if __name__ == "__main__":
    asyncio.run(main())
