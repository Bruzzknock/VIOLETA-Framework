import re
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def step1() -> str:
        template = """ Theory about what Atomic Unit is:
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

An Atomic Unit is wider than a single learning objective – it bundles related, 
mutually‑reinforcing skills so the player practises them as a coherent package. 
By surfacing the whole bundle early you make it obvious what "good play" will look 
like in real life.

Generate 3 ideas for atomic unit."""
        prompt = PromptTemplate.from_template(template)
        model = OllamaLLM(model="deepseek-r1:14b",
                          base_url="http://127.0.0.1:11434")
        chain = prompt | model
        return remove_think_block(chain.invoke({}))

def remove_think_block(text: str) -> str:
        return re.sub(r"<think>.*?</think>\s*","", text, flags=re.DOTALL)

def step2(atomic_unit: str) -> str:
        template = """ Theory about what Atomic Unit Skills are:
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
Cohesion is particularly important in serious games because it allows thematic
elements, player decisions, and feedback systems to all point in the
same conceptual direction. This not only strengthens the educational impact
but also improves player immersion. A player who senses that all game
elements are “pulling in the same direction” is more likely to perceive their
actions as meaningful and transferable to real life.
In the case of our time management atomic unit, we identify a wide range
of supporting skills. While categorization is not required by the framework,
grouping related skills into meaningful categories can greatly assist the designer
by simplifying the design process. Specifically, it provides a clearer
overview of the skills involved, reduces cognitive load during integration
steps, and allows the designer to reason more effectively about emotional
alignment, gameplay mapping, or tiered progression. These groupings are
not mandatory—they serve purely as a scaffolding tool to help manage complexity
when working with a large or diverse set of skills.
With this in mind, the time management skill set has been organized into
the following four categories:
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

Generate skills for this atomic unit."""
        print("IM YELINNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNG -------------------------------------------------------------------- STEP TWO:", atomic_unit)
        prompt = PromptTemplate.from_template(template)
        prompt.format(atomic_unit=atomic_unit)
        model = OllamaLLM(model="deepseek-r1:14b",
                          base_url="http://127.0.0.1:11434")
        chain = prompt | model
        return remove_think_block(chain.invoke({"atomic_unit": atomic_unit}))


def step3(atomic_unit_skills: str) -> str:
        template = """ Theory about what Theme is:
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
For our time management example, we have chosen a theme grounded in real
life: the daily struggle of a high-performing, overcommitted young adult.
Theme: “The 20-Year-Old Entrepreneur-Student-Athlete”
You play as a 20-year-old student trying to juggle multiple roles: a university
degree, launching a startup, maintaining an active social life, engaging in
creative hobbies, and staying physically fit through regular athletic training.
Each week brings a mix of self-defined goals and unexpected challenges. Will
you manage to finish your coursework? Will your company gain traction?
Will your friendships or your health suffer under the weight of ambition?
This theme was selected not only because it is relatable for the intended
audience, but because it naturally embodies the core skills of time
management. Prioritization, planning, scheduling, and habit formation
are not just embedded—they are the essence of what the player must do in
order to succeed.

Our Atomic Unit Skills: {atomic_unit}

Generate theme for these atomic unit skills."""
        print("IM YELINNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNG -------------------------------------------------------------------- STEP THREE:", atomic_unit_skills)
        prompt = PromptTemplate.from_template(template)
        prompt.format(atomic_unit=atomic_unit_skills)
        model = OllamaLLM(model="deepseek-r1:14b",
                          base_url="http://127.0.0.1:11434")
        chain = prompt | model
        return remove_think_block(chain.invoke({"atomic_unit": atomic_unit_skills}))