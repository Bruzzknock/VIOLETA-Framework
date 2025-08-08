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
        """Generate kernel sentences for each atomic skill by learning type."""

        prompts = {
                "Declarative": (
                        """
You are a helpful assistant for the VIOLETA framework.

Given a declarative atomic skill, create one or more one-sentence kernels for the skill.

Each kernel must:
• Follow the Input → Transformation → Output mapping explicitly.
• Express a causal or functional fact that supports real-world mastery of the skill.
• Use one active verb (or one passive verb phrase if unavoidable, e.g., "are classified as").
• Avoid purely descriptive, aesthetic, or sensory traits (e.g., "crisp texture," "bright color") unless directly linked to a functional property relevant to the skill.
• Be concrete and teach something actionable or scientifically relevant.
• Avoid subjective judgments or opinions.

Return the kernels as a JSON object mapping each skill to its kernel sentence, with explicit 'input', 'verb', and 'output' fields.

Before finalizing, run a "Quality Gate":
1. Does the kernel directly advance mastery of the atomic skill?
2. Does it show a clear cause-and-effect relationship?
3. Could it be mapped to a game mechanic where success requires applying this fact?

If any answer is "no," discard or rewrite the kernel.

Examples:
<example>
atomic unit: Nutrition
atomic skill: Protein sources
output:
{
  "Protein sources": [
    {
      "kernel": "Meat has protein, which builds muscle and aids recovery.",
      "input": "meat",
      "verb": "has",
      "output": "protein, which builds muscle and aids recovery"
    },
    {
      "kernel": "Eggs contain protein that supports tissue repair.",
      "input": "eggs",
      "verb": "contain",
      "output": "protein that supports tissue repair"
    }
  ]
}
</example>

<example>
atomic unit: Energy nutrients
atomic skill: Carbohydrates
output:
{
  "Carbohydrates": [
    {
      "kernel": "Bread provides quick energy for the body.",
      "input": "bread",
      "verb": "provides",
      "output": "quick energy for the body"
    },
    {
      "kernel": "Potatoes supply energy that fuels activity.",
      "input": "potatoes",
      "verb": "supply",
      "output": "energy that fuels activity"
    }
  ]
}
</example>
        """
                ),
                "Procedural": (
                        """
You are a helpful assistant for the VIOLETA framework.

Given a procedural atomic skill, create one or more one-sentence kernels for the skill.

Each kernel must:
• Be in active voice, present tense.
• Contain exactly one imperative or present-simple verb that a learner would physically or mentally perform.
• Clearly follow the Input → Transformation → Output mapping in the JSON fields.
• Describe an action that advances mastery of the skill in a real-world context.
• Avoid filler actions or decorative phrasing (e.g., “prepare nicely,” “carefully handle”) unless the adverb specifies a measurable outcome.
• Avoid subjective judgments or aesthetic results unless they have functional significance.
• Make the output tangible or verifiable (size, form, state, structure, readiness).

**Quality Gate before finalizing:**
1. Does the action directly contribute to mastering the atomic skill?
2. Is there a clear transformation from the input state to the output state?
3. Could the step be mapped to a concrete in-game mechanic that requires correct execution?

If any answer is “no,” discard or rewrite the kernel.

Return the kernels as a JSON object mapping each skill to its kernel sentence, with explicit 'input', 'verb', and 'output' fields.


Examples:
<example>
atomic unit: Digital Photography
atomic skill: Adjust camera exposure
output:
{
  "Adjust camera exposure": [
    {
      "kernel": "Increase shutter speed to reduce motion blur in bright light.",
      "input": "shutter speed",
      "verb": "increase",
      "output": "reduced motion blur in bright light"
    },
    {
      "kernel": "Decrease aperture size to increase depth of field.",
      "input": "aperture size",
      "verb": "decrease",
      "output": "increased depth of field"
    }
  ]
}
</example>
<example>
atomic unit: Data Analysis
atomic skill: Sort dataset by value
output:
{
  "Sort dataset by value": [
    {
      "kernel": "Arrange data rows in ascending order by numeric value.",
      "input": "data rows",
      "verb": "arrange",
      "output": "ascending order by numeric value"
    }
  ]
}
</example>
                        """
                ),
                "Metacognitive": (
                        """
You are a helpful assistant for the VIOLETA framework.

Given a metacognitive atomic skill, create one or more one-sentence kernels for the skill.

Each kernel must:
• Be in active voice, present tense.
• Contain exactly one cognitive verb about self-regulation, strategic thinking, or reflective adjustment (e.g., plan, monitor, decide, evaluate, prioritise, adjust, reflect).
• Explicitly follow the Input → Transformation → Output mapping in the JSON fields.
• Describe a mental process that advances mastery of the atomic skill in a real-world context.
• Avoid vague introspection without actionable outcomes (e.g., “think about the task”).
• Make the output tangible or verifiable (e.g., improved plan, detected issue, revised approach).

**Quality Gate before finalizing:**
1. Does the cognitive act directly contribute to mastering the atomic skill?
2. Is there a clear transformation from the input state to the output state?
3. Could the mental step be mapped to a concrete in-game mechanic where success requires applying this reflective act?

If any answer is “no,” discard or rewrite the kernel.

Return the kernels as a JSON object mapping each skill to its kernel sentence, with explicit 'input', 'verb', and 'output' fields.

Examples:
<example>
atomic unit: Project Management
atomic skill: Risk assessment
output:
{
  "Risk assessment": [
    {
      "kernel": "Evaluate project milestones to identify risks before they escalate.",
      "input": "project milestones",
      "verb": "evaluate",
      "output": "identified risks before escalation"
    },
    {
      "kernel": "Adjust resource allocation to prevent delays in critical tasks.",
      "input": "resource allocation",
      "verb": "adjust",
      "output": "prevention of delays in critical tasks"
    }
  ]
}
</example>
<example>
atomic unit: Competitive Strategy
atomic skill: Match strategy adaptation
output:
{
  "Match strategy adaptation": [
    {
      "kernel": "Monitor opponent tactics to detect exploitable patterns.",
      "input": "opponent tactics",
      "verb": "monitor",
      "output": "detected exploitable patterns"
    },
    {
      "kernel": "Revise team formation to counter emerging threats.",
      "input": "team formation",
      "verb": "revise",
      "output": "counter to emerging threats"
    }
  ]
}
</example>
                        """
                ),
        }

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

        if isinstance(atomic_skills, dict):
                skills_by_type = {k: _flatten(v) for k, v in atomic_skills.items()}
        else:
                skills_by_type = {"Procedural": _flatten(atomic_skills)}

        results = {}

        for lt, skills in skills_by_type.items():
                prompt = prompts.get(lt, prompts["Procedural"])
                for skill in skills:
                        lc_messages = [SystemMessage(content=prompt)]
                        lc_messages.append(HumanMessage(content=f"Atomic unit: {atomic_unit}"))
                        lc_messages.append(HumanMessage(content=f"Atomic skill: {skill}"))

                        response = model.invoke(lc_messages)
                        cleaned = remove_think_block(response.content)
                        cleaned = remove_code_fences(cleaned)
                        try:
                                data = json.loads(cleaned)
                                for k, kernels in list(data.items()):
                                        if isinstance(kernels, list):
                                                for kernel in kernels:
                                                        if isinstance(kernel, dict):
                                                                kernel["learning_type"] = lt
                                        elif isinstance(kernels, dict):
                                                kernels["learning_type"] = lt
                                                data[k] = [kernels]
                                        else:
                                                data[k] = [{"kernel": kernels, "learning_type": lt}]
                        except Exception:
                                data = {skill: [{"kernel": cleaned, "learning_type": lt}]}
                        results.update(data)

        # Ensure each kernel has a unique id
        counter = 1
        for kernels in results.values():
                if isinstance(kernels, list):
                        for kernel in kernels:
                                if isinstance(kernel, dict):
                                        kernel.setdefault("id", f"k{counter}")
                                        counter += 1

        return json.dumps(results, indent=2)


def step2_why_it_matters(atomic_unit: str, kernel: dict) -> List[str]:
        """Generate a couple of short reasons why a kernel matters."""
        system_prompt = """
You are a helpful assistant for the VIOLETA framework.

Given an atomic unit and a kernel mapping (with input, verb, and output), provide 1–3 concise reasons **why mastering this kernel is important in real life**.

Guidelines:
• Focus on the practical, functional, or safety-related value of knowing and applying this fact or skill.
• Emphasise how it contributes to competence, efficiency, safety, or long-term success.
• Avoid restating the kernel itself; explain its *value*.
• Avoid decorative, subjective, or purely aesthetic reasons unless they are directly linked to a functional outcome.
• Order the reasons from most to least important based on real-life impact.

Return the reasons as a JSON list of strings.

Example:
<example>
atomic unit: Budgeting
{"kernel": "Meat has protein, which builds muscle and aids recovery.", "input": "meat", "verb": "has", "output": "protein, which builds muscle and aids recovery"}
output:
[
  "supports muscle growth and repair after physical activity",
  "helps maintain healthy immune function",
  "provides essential amino acids the body cannot produce on its own"
]
</example>
        """

        model = get_llm()
        lc_messages = [SystemMessage(content=system_prompt)]
        lc_messages.append(HumanMessage(content=f"Atomic unit: {atomic_unit}"))
        lc_messages.append(HumanMessage(content=f"Kernel: {json.dumps(kernel)}"))

        response = model.invoke(lc_messages)
        cleaned = remove_think_block(response.content)
        cleaned = remove_code_fences(cleaned)
        try:
                data = json.loads(cleaned)
                if isinstance(data, list):
                        return [str(r).strip() for r in data if str(r).strip()]
                if isinstance(data, str):
                        return [data.strip()]
        except Exception:
                pass
        return [cleaned.strip()] if cleaned.strip() else []






def step3a_old(atomic_skills, kernels_with_benefits, messages: List[Dict[str, str]]) -> str:
        """Return a chat-based response for choosing a theme."""
        system_prompt = """
### STEP 3A – PICK A CANDIDATE THEME
Answer the question: “In what kind of world or situation would someone need to use the skills from my atomic unit regularly?”

Write a 4–6 sentence mood blurb that:

Describes the world’s flavour, atmosphere, and stakes.

Explains the player’s role and common activities in that setting.

Briefly shows how each type of skill (Declarative, Procedural, Metacognitive) fits naturally into this world.
    • For Declarative kernels, do not just restate the fact — use its benefit (“why it matters”) to give it an in-world effect or consequence.
    • For Procedural and Metacognitive kernels, draw from their Input → Verb → Output logic directly.

Ensure the theme is cohesive, emotionally engaging, and offers multiple opportunities to practice all the skills.

Output format:
Theme name: [short, evocative title]
Theme blurb: [4–6 sentences as described above]

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
Our Kernels with Benefits: {kernels_with_benefits}
        """
        model = get_llm()

        lc_messages = [SystemMessage(content=system_prompt)]

        lc_messages.append(HumanMessage(content=f"My atomic skills are: {atomic_skills}"))
        lc_messages.append(
                HumanMessage(content=f"My kernels with benefits are: {kernels_with_benefits}")
        )
        for msg in messages:
                if msg["role"] == "user":
                        lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                        lc_messages.append(AIMessage(content=msg["content"]))

        response = model.invoke(lc_messages)
        return remove_think_block(response.content)


def step3a(kernel: dict) -> str:
        """Find an analogy for a kernel while preserving its benefits."""
        system_prompt = """
STEP 3A – ANALOGY FOR EACH KERNEL
Given a kernel and its benefits, produce a concise analogy that explains the kernel and demonstrates why each of its benefits is important.

Instructions:

Provide 2 to 3 distinct analogies for each kernel.

For each analogy, first state the analogy as a single-sentence header.

Then, in a paragraph below the header, write the analogy.

Below that explain how the analogy works.

Within the explanation, use bold text to explicitly link each of the kernel's benefits to a corresponding part of the analogy.

Example Kernel:
Kernel: Record all categorized expenses in a financial tracking system.
Benefits:

Enables accurate tracking of spending habits and identification of areas for savings.

Provides essential data for creating realistic budgets and achieving financial goals.

Facilitates quick detection of financial discrepancies or potential fraud.

Desired Output Format:
Analogy 1: [Your analogy header]
[Paragraph explaining the analogy, with bolded connections to each benefit]

Analogy 2: [Your analogy header]
[Paragraph explaining the analogy, with bolded connections to each benefit]

<example>
Kernel: Record all categorized expenses in a financial tracking system.
Benefits:

Enables accurate tracking of spending habits and identification of areas for savings.

Provides essential data for creating realistic budgets and achieving financial goals.

Facilitates quick detection of financial discrepancies or potential fraud.

Analogy 1: Curating the Memories in a Time Traveler’s Archive
A time traveler maintains an intricate archive of every moment they’ve visited — each memory stored in a crystal labeled by era, location, 
and emotional tone — just like recording each expense in its correct financial category. After every jump, the traveler logs the exact 
date, people met, and events witnessed, ensuring the timeline stays intact.
In this analogy, reviewing which eras they revisit most often helps the traveler understand their personal patterns and biases, mirroring 
how tracking expenses reveals spending habits and areas for savings. The archive also guides the traveler in planning future journeys to 
prevent paradoxes and ensure they have enough chrono-energy for the trip, just as your records provide essential data for creating 
realistic budgets and achieving financial goals. And if a crystal has been altered by a rival time traveler — a tiny change in the 
hue or the recorded events — the archivist spots the distortion immediately, reflecting how quick detection of discrepancies or fraud 
works in a financial tracking system.

Analogy 2: Operating a Starship’s Navigation Log
A starship captain keeps a precise navigation log that records every hyperspace jump, resource use, and cargo manifest — just like recording each 
expense into the correct financial category. The log is updated after every mission, ensuring no data point is lost in the void.
In this analogy, tracking the ship’s resource consumption across missions reveals where fuel, food, or energy is wasted, just as tracking categorized 
expenses highlights spending habits and areas for savings. The navigation log also provides critical data for planning long voyages and allocating 
supplies, mirroring how your expense records give essential information for creating realistic budgets and achieving financial goals. And if an 
alien stowaway tampers with the cargo or a system glitch alters the coordinates, the captain can spot the irregularity immediately, just like 
quick detection of discrepancies or potential fraud in a financial tracking system.

Analogy 3: Maintaining a Wizard’s Spellbook
A wise wizard keeps a meticulously organized spellbook, with each spell written under its proper school of magic — fire, illusion, healing, and so on — 
just like recording each expense into the correct financial category. The wizard updates it after every magical encounter, ensuring no incantation is forgotten.
In this analogy, tracking which spells are used most often lets the wizard see their strengths and weaknesses, just as tracking categorized expenses 
reveals spending habits and areas for savings. The spellbook also guides the wizard when preparing for future battles or quests, just as your records 
provide essential data for creating realistic budgets and achieving financial goals. And if a page has been tampered with by a mischievous imp, the 
wizard spots the anomaly at once, mirroring how quick detection of financial discrepancies or fraud works in a tracking system.
</example>
        """
        model = get_llm()
        kernel_text = kernel.get("kernel")
        benefits = kernel.get("why_it_matters") or []

        lc_messages = [SystemMessage(content=system_prompt)]
        lc_messages.append(HumanMessage(content=f"Kernel: {kernel_text}"))
        if benefits:
                lc_messages.append(HumanMessage(content=f"Benefits: {benefits}"))

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


def step3(
        atomic_skills, skill_kernels, kernels_with_benefits, messages: List[Dict[str, str]]
) -> str:
        """Generate analogies for each kernel and return them grouped by skill."""

        analogies: dict = {}
        if isinstance(kernels_with_benefits, dict):
                for skill, kern_list in kernels_with_benefits.items():
                        results = []
                        if isinstance(kern_list, list):
                                for kern in kern_list:
                                        try:
                                                analogy = step3a(kern)
                                                results.append({
                                                        "kernel": kern.get("kernel"),
                                                        "analogy": analogy,
                                                })
                                        except Exception:
                                                continue
                        analogies[skill] = results

        return json.dumps(analogies, indent=2)

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
