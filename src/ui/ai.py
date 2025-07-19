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
        """Return a chat-based response for choosing a theme and validating kernels."""
        system_prompt = """
### STEP 3 · COMMIT TO A THEME & VALIDATE EVERY KERNEL

**Step 3A – Pick a Candidate Theme**
Answer the question: "In what kind of world or situation would someone need to use the skills from my atomic unit regularly?" Provide a two-sentence mood blurb describing the world's flavour, stakes and common activities.

**Step 3B – Kernel-by-Kernel Mapping**
For each kernel from Step 2, specify an in-world element for the input, an action matching the kernel verb, and the resulting output. Mark the row with `Y` if the Input → Transformation → Output logic is preserved, otherwise `N`.
The theme must cover every kernel. Revise the theme if any kernel cannot be mapped.

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

def step3_mapping(theme: str, skill_kernels) -> str:
        """Generate a kernel mapping table for the chosen theme."""
        system_prompt = """
You are a helpful assistant for the VIOLETA framework.
Given a theme and a collection of kernels (each with input, verb and output), create a mapping table.
For every kernel, propose a theme-specific input, an action expressing the verb, and a theme-based output.
Mark each row with `Y` if the Input → Transformation → Output structure is preserved, otherwise `N`.
Return the result as JSON.
        """
        model = ChatOllama(
                model="deepseek-r1:14b",
                base_url=os.environ["OLLAMA_HOST"],
        )

        lc_messages = [SystemMessage(content=system_prompt)]
        lc_messages.append(HumanMessage(content=f"Theme: {theme}"))
        lc_messages.append(HumanMessage(content=f"Kernels: {skill_kernels}"))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)
