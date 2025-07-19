import re
import os
from typing import List, Dict

from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

load_dotenv(override=True)

def step1(messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response for choosing an atomic unit."""
        system_prompt = """Theory about what Atomic Unit is:
        
        The first step in applying the VIOLETA framework is to answer a deceptively
simple question:

“What is the atomic unit that the game should be based on?”

An atomic unit, as defined in the framework, refers to a bundled set of
real-world knowledge, behaviors, or skills that should be learned together as
a cohesive whole. It is the educational “nucleus” of the game—what the game
aims to teach or train, not as isolated trivia, but as a functional, applicable
cluster of competencies.
Atomic units can vary greatly in complexity. They may be as narrow
as a single soft skill—such as assertive communication or basic mental
arithmetic—or as broad as an entire interdisciplinary domain, such as
systems thinking or quantum physics. The choice of atomic unit depends on
the designer’s educational goals, target audience, and contextual constraints.
        """
        model = ChatOllama(
                model="deepseek-r1:14b",
                base_url=os.environ["OLLAMA_HOST"],
        )

        lc_messages = [HumanMessage(content=system_prompt)]
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)

def remove_think_block(text: str) -> str:
        return re.sub(r"<think>.*?</think>\s*","", text, flags=re.DOTALL)


def step2(atomic_unit, messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response for choosing atomic skills."""
        system_prompt = """
### STEP 2 · IDENTIFY THE ATOMIC SKILLS

**Context**
An *atomic unit* is a bundled set of real-world knowledge, behaviours, or skills that should be learned together as a cohesive whole. It is the educational “nucleus” of the game—what the game aims to teach or train, not as isolated trivia but as a functional, applicable cluster of competencies.  
Atomic units can range from a narrow soft skill (e.g. assertive communication) to an entire interdisciplinary domain (e.g. systems thinking). The choice depends on educational goals, target audience, and design constraints.

**Task for the AI**
Break the atomic unit into the smallest set of **atomic skills** that must be mastered to achieve functional competence.

**When to STOP decomposing**
* If the atomic unit/skill is already a single, self-contained skill or behaviour (e.g. *Encryption*), return **that one skill only**.
* Otherwise, list each atomic skill separately.  
  *Categories are optional*—use them only when they add clarity.

**Coherence check**
Every atomic skill must directly support the atomic unit’s overarching goal; drop anything tangential.

**Required output format**
atomic unit: <name>
atomic skills:
– <skill 1>
– <skill 2>
…

Examples:
<example>
atomic unit: Foundational Personal Budgeting - The ability to build, execute, and iterate a month-to-month budget that keeps spending below income while funding short- and long-term goals.
atomic skills:
- Income recording
- Expense tracking
- Categorisation
- Cash-flow snapshot
- SMART goal setting
- Prioritisation & trade-off analysis
- Envelope / zero-based allocation
- Real-time variance monitoring
- Mid-cycle adjustment
</example>

<example>
atomic unit: Cryptography
atomic skills:
- Encryption
- Decryption
- Hashing Algorithm, modulo division method
</example>

**Note**
These examples illustrate *one* valid decomposition. Adapt the granularity and wording to suit your pedagogical intent and audience context. Internal coherence and direct relevance to the atomic unit matter most.

Our atomic unit: {atomic_unit}
        """
        model = ChatOllama(
                model="deepseek-r1:14b",
                base_url=os.environ["OLLAMA_HOST"],
        )

        lc_messages = [SystemMessage(content=system_prompt)]

        lc_messages.append(HumanMessage(content=f"My atomic unit is: {atomic_unit}"))
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step2_kernels(atomic_unit: str, atomic_skills) -> str:
        """Generate kernel sentences for each atomic skill."""
        system_prompt = """
You are a helpful assistant for the VIOLETA framework.
Given an atomic skills, create a one-sentence kernel for each
skill. A kernel follows the pattern: Input -> Transformation -> Output and
uses active verbs and plain language. Use one active verb only per sentence.
If a skill needs more than one verb, split it into multiple kernels.
Return the kernels as a JSON object mapping each skill to its kernel sentence.

Examples:
<example>
atomic unit: Cryptography
atomic skill: Encryption
output:
{{
  "Encryption": [
    {{
      "kernel":"Transform readable data into unreadable data with a reversible rule.",
      "input": "readable data",
      "verb": "transform into",
      "output": "unreadable data with a reversible rule"
    }}
  ]
}}
</example>

<example>
atomic unit: Cryptography
atomic skill: Hashing
output:
{{
  "Hashing": [
    {{
      "kernel": "Condense variable-length data into a fixed-length fingerprint.",
      "input": "variable-length data",
      "verb": "condense into",
      "output": "fixed-length fingerprint"
    }}
  ]
}}
</example>

<example>
atomic unit: Cryptography
atomic skill: Modulo Division Hashing
{{
  "Modulo Division Hashing": [
    {{
      "kernel": "Divide the key by the table size to obtain its remainder index.",
      "input": "key and table size",
      "verb": "divide by",
      "output": "remainder index"
    }},
    {{
      "kernel": "Add the modulus to a negative key to obtain a positive remainder.",
      "input": "negative key and modulus",
      "verb": "add to",
      "output": "positive remainder"
    }},
    {{
      "kernel": "Link colliding keys into a chain to keep every entry reachable.",
      "input": "colliding keys at same index",
      "verb": "link into",
      "output": "chain with reachable entries"
    }},
    {{
      "kernel": "Divide the number of stored entries by the table size to calculate the load factor.",
      "input": "number of entries and table size",
      "verb": "divide by",
      "output": "load factor"
    }}
  ]
}}
</example>
        """
        model = ChatOllama(
                model="deepseek-r1:14b",
                base_url=os.environ["OLLAMA_HOST"],
        )

        lc_messages = [SystemMessage(content=system_prompt)]
        lc_messages.append(HumanMessage(content=f"Atomic unit: {atomic_unit}"))
        lc_messages.append(HumanMessage(content=f"Skills: {atomic_skills}"))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)

def remove_think_block(text: str) -> str:
        return re.sub(r"<think>.*?</think>\s*","", text, flags=re.DOTALL)


def step3(atomic_skills, messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response for choosing a theme."""
        system_prompt = """
Once the atomic unit and its component skills are defined, the next step is to
select a theme—a narrative setting and emotional context in which the skills
of the atomic unit are naturally relevant and continuously engaged.
The designer does this by answering the question:

“In what kind of world or situation would someone need to use the skills
from my atomic unit regularly?”

This formulation is designed to trigger System 1 intuition. Instead of forcing
a rational, top-down selection of theme, the question gently activates the
designer’s subconscious ability to associate real-life scenarios with the skills
involved. It encourages creativity while keeping the design anchored in pedagogical
relevance.
While there are no restrictions on the type of theme—realistic, fictional,
metaphorical, or fantastical—the key is that the theme provides a meaningful
context for the atomic unit to manifest and develop. A good
theme not only helps players emotionally invest in the game world, but also
ensures that practicing the target skills feels logical and engaging within that
context.

Example:
atomic unit: Foundational Personal Budgeting - The ability to build, execute, and iterate a month-to-month budget that keeps spending below income while funding short- and long-term goals.
atomic skills: 
1. Gather & organise facts	
- Income recording = List all income streams and their cadence
- Expense tracking = Capture every outflow as it happens
- Categorisation = Sort expenses into fixed, variable, discretionary
2. Build a workable plan	
- Cash-flow snapshot = Calculate disposable income (= income – must-pay costs)
- Goal setting (SMART) = Translate life goals into monthly saving targets
Prioritisation & trade-off analysis = Decide what gets funded first when money is tight
3. Execute & monitor	
- Envelope / zero-based allocation = Assign every euro to a category before the month starts
- Real-time variance monitoring = Compare actual vs. planned spend and flag overruns
- Mid-cycle adjustment = Shift funds between categories without breaking the plan
4. Sustain & improve	
- Periodic review ritual = Run a weekly/monthly retro and roll lessons into next plan
- Tool fluency = Use a tracker or spreadsheet efficiently (import data, automate rules)
- Impulse-control tactics = Deploy cues (cool-down timers, wish-lists) to curb unplanned buys


Choosen theme Theme:  Moon-Base Quartermaster
Keep a fledgling lunar colony supplied until the next cargo shuttle arrives.

Income recording : supply-pod manifests—each incoming cargo flight (helium-3 sales revenue, government stipends, private-sector grants) is logged as a new income line.
Expense tracking : live consumption feeds from habitat modules (life-support power, hydroponic nutrients, 3-D-printer filament) stream into the ledger via IoT monitor beacons.
Categorisation : tag every cost node as Fixed (comm-sat bandwidth lease), Variable (solar-panel dust-clearing, EVA-suit repairs) or Discretionary (crew-morale VR cinema nights).
Cash-flow snapshot : the Colony Dashboard recomputes “Survival runway” (days of oxygen/food) and “Investment headroom” after costs are categorised.
SMART goal setting : create goal cards such as “Expand hydro-farm capacity by 20 % within 60 sols” and link them to an “Expansion” funding envelope.
Prioritisation & trade-off analysis : weigh diverting credits from science-lab upgrades to emergency water-filter replacements when resources tighten.
Envelope / zero-based allocation : during pre-sol planning, drag every projected credit into envelopes (Life-Support, Infrastructure, R&D, Morale) so none remain unassigned.
Real-time variance monitoring : meteorite damage spikes power costs; live budget vs plan deltas glow red on the Ledger HUD.
Mid-cycle adjustment : reroute surplus helium-3 export revenue into the “Emergency Repairs” envelope when a rover tyre bursts mid-week.
Periodic review ritual : convene a weekly Sol-End Council with department heads, paging through auto-generated KPI slides before approving next-week baselines.
Tool fluency : use the colony’s “LunaBooks” app to bulk-import sensor CSVs, set up auto-rules (e.g., flag any category exceeding 120 % of plan).
Impulse-control tactics : incoming crew requests (e.g., power-hungry holo-surf park) enter a 24-hour cooling rack; many expire or become cheaper off-peak, curbing impulse spending.


Our Atomic Skills: {atomic_skills}
        """
        model = ChatOllama(
                model="deepseek-r1:14b",
                base_url=os.environ["OLLAMA_HOST"],
        )

        lc_messages = [SystemMessage(content=system_prompt)]

        lc_messages.append(HumanMessage(content=f"My atomic skills are: {atomic_skills}"))
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)
