import json
import re
import os
from typing import List, Dict

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

try:
        from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:  # Module may not be installed
        ChatGoogleGenerativeAI = None
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

load_dotenv(override=True)


def get_llm():
        """Return a chat model using Gemini if available, otherwise Ollama."""
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
        if gemini_key:
                if ChatGoogleGenerativeAI is None:
                        raise ImportError(
                                "langchain_google_genai must be installed to use Gemini"
                        )
                return ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash", #gemini-2.5-flash #gemini-2.5-pro
                        google_api_key=gemini_key,
                )
        return ChatOllama(
                model="deepseek-r1:14b",
                base_url=os.environ["OLLAMA_HOST"],
        )

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
        model = get_llm()

        lc_messages = [HumanMessage(content=system_prompt)]
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step2_kernels(atomic_unit: str, atomic_skills) -> str:
        """Generate kernel sentences for each atomic skill recursively."""

        system_prompt = (
                """
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
        )

        model = get_llm()

        def _flatten(sk):
                if isinstance(sk, dict):
                        result = []
                        for val in sk.values():
                                if isinstance(val, list):
                                        result.extend(val)
                                else:
                                        result.append(val)
                        return result
                if isinstance(sk, list):
                        return sk
                return [s.strip() for s in str(sk).splitlines() if s.strip()]

        skills = _flatten(atomic_skills)
        results = {}

        for skill in skills:
                lc_messages = [SystemMessage(content=system_prompt)]
                lc_messages.append(HumanMessage(content=f"Atomic unit: {atomic_unit}"))
                lc_messages.append(HumanMessage(content=f"Atomic skill: {skill}"))

                response = model.invoke(lc_messages)
                cleaned = remove_think_block(response.content)
                cleaned = remove_code_fences(cleaned)
                try:
                        data = json.loads(cleaned)
                except Exception:
                        data = {skill: cleaned}
                results.update(data)

        return json.dumps(results, indent=2)






def step3a(atomic_skills, messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response for choosing a theme."""
        system_prompt = """
### STEP 3A \u2013 PICK A CANDIDATE THEME
Answer the question: "In what kind of world or situation would someone need to use the skills from my atomic unit regularly?" Provide a two-sentence mood blurb describing the world's flavour, stakes and common activities.

Examples:
<example>
atomic unit: Programming Syntax
atomic skills: ["Data types", "Variables declaration and assignment", "Operators and their precedence", "Control flow (conditionals, loops)", "Functions definition and invocation", "Scope management", "Arrays and collections syntax", "Error handling", "String manipulation functions"]
output:
Fantasy Theme: Magic and Code
In a realm where technology and magic intertwine, the world of Arcanecode is governed by the principles of programming and spellcasting. Wizards and sorcerers wielding arcane knowledge cast spells using intricate code syntax, 
with data types representing different magical elements—fire, water, earth, and air. Variables declaration and assignment are essential for assigning magical energies or resources, while operators and precedence dictate the 
order in which spells are combined. Control flow through conditionals and loops governs the decision-making processes of magic, such as casting protective shields until a specific condition is met. Functions definition and 
invocation allow for reusable spells and magical constructs, while scope management limits the effect of spells to certain areas or durations. Error handling is crucial for addressing failed spells or unexpected magical reactions, 
and string manipulation shapes and alters magical runes or incantations. In this world, the stakes are high—incorrect code can lead to disastrous consequences like spells backfiring or magical energy overflows. Being a skilled programmer 
in Arcanecode is not just a talent; it is essential for survival and success in a realm where magic is powered by code.

</example>

Our Atomic Skills: {atomic_skills}
        """
        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]

        lc_messages.append(HumanMessage(content=f"My atomic skills are: {atomic_skills}"))
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step3b(theme: str, skill_kernels) -> str:
        """Generate a kernel mapping table for the chosen theme."""
        system_prompt = """
### STEP 3B \u2013 KERNEL-BY-KERNEL MAPPING
For each kernel from Step 2, specify an in-world element for the input, an action matching the kernel verb, and the resulting in-world element output. Mark the row with `Y` if the Input \u2192 Transformation \u2192 Output logic is preserved, otherwise `N`.
The theme must cover every kernel. Revise the theme if any kernel cannot be mapped.

Return the result as JSON.

Examples:
<example>
theme: Fantasy Theme: Magic and Code
kernels: {"Data types": [{"kernel": "Transform data without context into structured information using predefined categories.", "input": "data without context", "verb": "transform into", "output": "structured information with data types"}], "Variables declaration and assignment": [{"kernel": "Create or update variable storage to hold specific values or references.", "input": "variable and value/reference", "verb": "create/update", "output": "variable storage with assigned value/reference"}]}
output:
{
  "theme": "Fantasy Theme: Magic and Code",
  "kernels": [
    {
      "kernel": "Data types",
      "input": "raw magical energy",
      "verb": "transform into",
      "output": "categorized magic (e.g., fire, water)",
      "preserved": "Y"
    },
    {
      "kernel": "Variables declaration and assignment",
      "input": "magic energy source",
      "verb": "bind into",
      "output": "bound amulet or container",
      "preserved": "Y"
    },
    {
      "kernel": "Control flow (conditionals, loops)",
      "input": "protective magic and conditions",
      "verb": "cast based on",
      "output": "active protective shield",
      "preserved": "Y"
    },
    {
      "kernel": "Functions definition and invocation (define function)",
      "input": "spell parameters and task",
      "verb": "define as",
      "output": " reusable spell template",
      "preserved": "Y"
    },
  ]
}
</example>
        """
        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]
        lc_messages.append(HumanMessage(content=f"Theme: {theme}"))
        lc_messages.append(HumanMessage(content=f"Kernels: {skill_kernels}"))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step2(atomic_unit, messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response for choosing atomic skills."""
        system_prompt = """
### STEP 2 · DECOMPOSE & TYPE-TAG THE ATOMIC SKILLS

**Context**  
An *atomic unit* is a tightly-coupled bundle of knowledge, behaviours, or skills that should be learned as one functional whole. Your job is to unpack it into the *atomic skills* a learner must master, 
then label each skill with exactly one learning-type tag drawn from {learning_types}.

**Learning-type tags**  
- **Declarative (D)**  — Knowing *what*: facts, terminology, conceptual relationships.  
- **Procedural (P)**  — Knowing *how*: sequences, operations, motor or cognitive routines.  
- **Metacognitive (M)** — Knowing *why/when*: monitoring, planning, and regulating one’s own performance.

> *If a skill clearly spans two types, choose the tag that best represents what will be **practised during gameplay or assessment***.

**Task for the AI**  
1. Break **{atomic_unit}** into its minimal set of atomic skills.  
2. Assign exactly one tag (D, P, or M) to every skill.

**When to STOP decomposing**  
- If the atomic unit is already a single, self-contained skill or behaviour, return **that one skill only**.  
- Otherwise, list each atomic skill on its own line—no sub-skills or sub-bullets.

**Coherence check**  
Every atomic skill must directly support the atomic unit’s functional goal; discard anything tangential.

**Required output format**  
atomic unit: {atomic_unit}

declarative skills (D):  
– <skill 1>  
– <skill 2>  

procedural skills (P):  
– <skill 3>  
– <skill 4>  

metacognitive skills (M):  
– <skill 5>  
– <skill 6>  

*(If a list is empty, include the heading and write “– none” so no category is skipped.)*

---

#### Example

atomic unit: Foundational Chess Competence—play a complete game under classical rules while making sound strategic decisions.

declarative skills (D):  
– Opening principles (control centre, develop pieces, king safety)  
– Piece valuation (relative point values, material trade-offs)  
– Basic tactical motifs vocabulary (fork, pin, skewer, discovered attack)  

procedural skills (P):  
– Legal piece movement & captures  
– Castling and en-passant execution  
– Using algebraic notation to record moves  

metacognitive skills (M):  
– Choosing *when* to transition from opening to middlegame  
– Planning a move sequence based on long-term strategic goals  
– Evaluating positions to decide *whether* to simplify into an endgame  

---

*(End of prompt)*
        """
        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]

        lc_messages.append(HumanMessage(content=f"My atomic unit is: {atomic_unit}"))
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)



def remove_think_block(text: str) -> str:
        return re.sub(r"<think>.*?</think>\s*","", text, flags=re.DOTALL)


def remove_code_fences(text: str) -> str:
        """Strip markdown-style triple backtick fences from the text."""
        text = re.sub(r"```[a-zA-Z]*\n", "", text)
        text = text.replace("```", "")
        return text.strip()


def step3(atomic_skills, skill_kernels, messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response using Step 3A then Step 3B."""
        theme = step3a(atomic_skills, messages)
        mapping = step3b(theme, skill_kernels)
        return f"{theme}\n\n{mapping}"

def step3_mapping(theme: str, skill_kernels) -> str:
        """Backward compatible wrapper for step3b."""
        return step3b(theme, skill_kernels)


def step4(theme: str, atomic_skills, messages: List[Dict[str, str]]) -> str:
        """Generate a short emotional arc description."""
        system_prompt = f"""
### STEP 4 – Map the Emotional Arc
Theme: {theme}
Atomic skills: {atomic_skills}

Write a 2–3 sentence vignette showing how a player would feel while applying these skills in this world. Then list the 3–5 key feelings, each with a brief explanation of which skill triggers it. Keep the answer concise.

<example output>
Vignette:
The dim light of the flickering scrap-wood fire dances across your face as you carefully measure out the day's meager rations, each grain of salvaged powder a precious commodity. 
Your stomach rumbles, but you push past the hunger, focusing on the precise adjustments to the heat source, knowing that a single misstep could ruin the tough, scavenged meat simmering in the communal pot. 
As you divide the meal into carefully calculated portions, a sense of grim satisfaction settles over you – another day's survival secured, thanks to your unwavering precision.
Key feelings:
Responsibility: Triggered by Portion control and Balanced meal composition, as the player holds the community's survival in their hands, ensuring everyone receives their crucial share.
Carefulness: Evoked by Measuring techniques and Heat management & cooking methods, where even the smallest error can have dire consequences in a world of scarcity.
Relief Satisfaction: Arises from the successful application of all skills, particularly after dividing the meal, signifying another small victory against the constant threat of starvation.
</example output>
        """

        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step5(feelings: str, messages: List[Dict[str, str]]) -> str:
        """Arrange feelings into a simple hierarchy or sequence."""

        system_prompt = f"""
### STEP 5 – Layer Feelings

> **Goal** — introduce just enough structure into the emotional-design space  
> to support the upcoming mechanics-mapping phase.

---

## 🔹 Inputs
1. **Core Emotional States** — the emotions you selected in the previous step:
2. *(Optional)* Supporting design notes or narrative beats that clarify why each emotion matters
Input: {feelings}
---

## 🔹 Tasks
### 1. Brainstorm Relationships
For every pair of emotional states, ask  
- Does one reliably **lead to** or **intensify** the other?  
- Does one emotion **contain** or **subdivide** the other?  
- Are they largely **independent / parallel**?  
Capture each answer as a short note (≤ 12 words).

### 2. Draft Candidate Structures
Sketch **2–4** different relationship graphs using any of these forms:
- **Hierarchy** (parent → child)  
- **Causal chain** (A → B → C)  
- **Cluster** (no clear order; group with a label)

### 3. Justify & Select
For each sketch, write **one sentence** explaining *why* the structure fits your experience, pedagogy, or story.  
Choose the arrangement that feels most “playable”; keep an alternative if you’re torn.

### 4. Record the LF Map
Output your chosen structure as **indented text** (see template below) plus a one-sentence rationale.  
If you kept an alternative, list it under **Back-ups**.

---

## 🔹 Output Template
```text
Layer Feelings Map
- Parent Emotion
-- Child Emotion
- Parallel Emotion

Rationale
<one concise sentence>

Back-ups (optional)
<bullet list of alt structures>

🔹 Example (Time-Management Prototype)
Layer Feelings Map
- Progress
-- Gradual Control of Life
- Constant Pressure

Rationale
Players feel mounting pressure first, but moments of progress unlock a sense of growing control—mirroring real-world time-management learning.

Back-ups
• Gradual Control → Progress | Constant Pressure (linear)
• Parallel: Gradual Control, Constant Pressure, Progress

        """

        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step6_mechanic_ideas(
    layered_feelings: str, medium: str, messages: List[Dict[str, str]]
) -> str:
        """Suggest mechanics for each feeling."""

        system_prompt = f"""
### STEP 6A – Map Feelings to Mechanics

You are brainstorming **{medium} mechanics** that could evoke each emotional
state listed below. Return concise suggestions using the format
`Feeling: mechanic1, mechanic2`.

Layer Feelings:
{layered_feelings}

<example>
Layer Feelings
- Progress
  - Gradual control
- Constant pressure

Suggestions
Progress: Deck-building, Skill Tree
Gradual control: Expanding action options
Constant pressure: Tight margin of success
</example>
        """

        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step7_mvp_ideas(mechanic: str, medium: str, messages: List[Dict[str, str]]) -> str:
        """Suggest schema breakdowns for building the MVP."""

        system_prompt = f"""
### STEP 7 – From Base Mechanics Tree to MVP (Recursive)

We are designing for {medium.lower()}. Break down the mechanic "{mechanic}" step by step.
Encourage the user to identify concrete game elements, then ask how each one
functions within the mechanics. Provide 3-5 short suggestions
using the format `Name: Description`.

<example>
Mechanic:
Deck Building

Suggestions:
Engine Cards: Cards with abilities that synergize with other cards, allowing for powerful combinations and increased card draw or resource generation.
Trash Pile: A designated area for removed cards. Players can move unwanted cards from their deck here to permanently remove them from the game.
Supply Piles: Stacks of identical cards. Players can purchase or acquire cards from these piles to add to their deck.
Victory Point Cards: Cards that, when acquired into a deck, contribute to a player's final score but often clog the deck during gameplay.
etc...
</example>
Target Mechanic:
{mechanic}
        """

        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step7_theme_fit(
    theme_vignette: str,
    kernel_mappings,
    parent: str,
    element: str,
    messages: List[Dict[str, str]],
) -> str:
    """Suggest how an element functions within the chosen theme."""

    mapping_text = json.dumps(kernel_mappings, indent=2) if kernel_mappings else ""
    system_prompt = f"""
### STEP 7 – Theme-fit Check

Theme vignette:
{theme_vignette}

Kernel to theme mappings:
{mapping_text}

Parent: {parent}
Element: {element}

Provide short suggestions on how this element could represent or operate within the theme. Use 2-4 concise bullet points or `Name: Explanation` style sentences.
"""

    model = get_llm()

    lc_messages = [SystemMessage(content=system_prompt)]
    for msg in messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))

    response = model.invoke(lc_messages)
    return remove_think_block(response.content)

def step8_sit_ideas(skills, emotions, messages: List[Dict[str, str]]) -> str:
    """Suggest direct skill → emotion links for the SIT."""

    skills_text = ", ".join(skills)
    emo_text = ", ".join(emotions)
    system_prompt = f"""
### STEP 8 – Scaling Influence Table

Skills:
{skills_text}

Emotions:
{emo_text}

Suggest which skills directly influence which emotions. Respond using the format `Skill: emotion1, emotion2` for a few likely connections. Only include direct effects.
"""
    model = get_llm()

    lc_messages = [SystemMessage(content=system_prompt)]
    for msg in messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))

    response = model.invoke(lc_messages)
    return remove_think_block(response.content)


def step8b_cell(kernel: str, mechanic: str, emotion: str) -> str:
    """Evaluate how a mechanic serves a kernel for a given emotion."""
    system_prompt = (
        "### STEP 8B – Triadic Integration Table – Kernel\n\n"
        "For the given kernel and mechanic, determine whether the mechanic can "
        "express the real-life micro-action trained by the kernel within the "
        "emotional context. Respond with one of: Accepted – <rationale>, "
        "Revised – <rationale>, or Rejected – <rationale>. Return only a single "
        "sentence."
    )

    user_prompt = (
        f"Emotion: {emotion}\n"
        f"Kernel: {kernel}\n"
        f"Mechanic: {mechanic}"
    )

    model = get_llm()
    lc_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = model.invoke(lc_messages)
    return remove_think_block(response.content)


def generate_game_description(data: dict) -> str:
    """Generate a high-level game description from gathered data."""
    system_prompt = (
        "You are a helpful assistant for the VIOLETA framework. "
        "The user will supply structured JSON describing an educational game. "
        "Interpret the fields as follows:\n"
        "- atomic_unit: overarching subject to master.\n"
        "- atomic_skills: list of core skills within that subject.\n"
        "- skill_kernels: minimal kernel for each skill with input, verb, and output.\n"
        "- theme: detailed narrative setting; theme_name: its short title.\n"
        "- kernel_theme_mapping: how each kernel appears in the theme with specific inputs, verbs, and outputs.\n"
        "- emotional_arc: vignette and mapping of feelings triggered by particular skills.\n"
        "- layered_feelings: hierarchy showing how feelings build on one another.\n"
        "- mechanic_mappings: which mechanics embody each feeling.\n"
        "- base_mechanics_tree: root mechanics and their dependents.\n"
        "- step7_queue: mechanics queued for further decomposition.\n"
        "- list_of_schemas: descriptive properties for named mechanics.\n"
        "- sit_table: Skill Impact Table (SIT) marking '+' or '-' for a skill's effect on a feeling.\n"
        "- tit_table: Triadic Integration Table (TIT) linking skill–emotion pairs to the mechanics and feedback that teach them.\n"
        "Using these elements, craft a concise, non-redundant description of the game. Follow this output structure without naming the sections:\n"
        "1) Elevator Pitch (≤30 words) — theme_name plus a hook.\n"
        "2) Learning Goal — 1-2 sentences summarising the atomic_unit in plain language.\n"
        "3) How You'll Master It — bullet list: Skill → in-game action → immediate feedback.\n"
        "4) Core Gameplay Loop — 2-3 sentences using mechanic_mappings and base_mechanics_tree to describe moment-to-moment play.\n"
        "5) Emotional Journey — paragraph using emotional_arc and layered_feelings explaining why mechanics evoke the feelings.\n"
        "6) Integration — explain how SIT/TIT and schemas keep learning, theme, and mechanics aligned.\n"
        "7) Scenario Snapshot — a 40-word vignette of a tense decision.\n"
        "Stylistic rules: 350-550 words total, second-person voice, active verbs, vivid sensory language, no technical jargon or raw JSON, mention each design artefact once.\n"
        "Validation checklist: ensure every atomic_skill appears in section 3, no section labels leak except theme_name, word count within limits, and return only the finished description with no headings or meta-commentary."
    )
    model = get_llm()
    content = json.dumps(data, indent=2)
    lc_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Structured game data:\n{content}"),
    ]
    response = model.invoke(lc_messages)
    return remove_think_block(response.content)
