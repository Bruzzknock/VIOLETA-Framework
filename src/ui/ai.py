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

Theory about what Atomic Skills are:
        
Once the atomic unit has been defined, the next step is to dissect it into its
component parts by asking:

“What knowledge, actions, and/or skills are necessary to master this
atomic unit?”

This dissection serves multiple purposes. First, it provides granular control
in later stages of the design process, particularly during theme and mechanics
integration. Second, and more subtly, it ensures internal cohesion: by
identifying sub-skills that all contribute to a common overarching goal, the
designer avoids the risk of mixing unrelated competencies simply for the sake
of variety.

For example in the case of time management atomic unit, we identify a wide range
of supporting skills.

Group 1: Use Productivity Tools
• Time Tracking
• Task Management
• Calendar and Scheduling
• Knowledge/Information and Note Management (e.g., shared OneNote)
• AI-Powered Productivity (e.g., ChatGPT)
• Focus and Distraction-Blocking Tools
Group 2: Use Established Techniques
• Goal Setting (e.g., SMART framework)
• Minimize Context Switching (e.g., batch similar tasks)
• 80/20 Principle
• Energy Management (e.g., scheduling tasks around personal energy
peaks)
Group 3: Develop Personal Skills
• Learning to Say No
• Prioritization Frameworks
• Planning and Delegation
• Focus and Concentration
• Control of Delayed Gratification
Group 4: Build Sustainable Habits
• Adequate Sleep
• Avoiding Procrastination
• Consistent Work Environment (e.g., working on the same task in the
same location)

Note: This list is not exhaustive, nor is it intended to be universally applicable.
It reflects one interpretation—my own—of the competencies involved in
effective time management. Educators and designers are encouraged to adapt
this step to fit their own pedagogical intent and audience context. What matters
most is that the selected skill set is internally coherent and directly
relevant to the atomic unit.

Our Atomic Unit: {atomic_unit}
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
