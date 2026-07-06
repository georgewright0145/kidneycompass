# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""KidneyCompass root orchestrator.

A UK/NHS CKD companion. Classifies against KDIGO, informs generically from NICE/KDIGO guidance,
and routes every clinical decision back to the clinician. High-stakes logic (classification, AKI,
KFRE, escalation) is deterministic Python in engines/; the model only understands input and
explains output. The prescribing/diagnosis do-not-answer class is enforced deterministically by a
before_model_callback BEFORE anything else runs.
"""

from google.adk.agents import Agent
from google.adk.apps import App
from google.genai import types as genai_types

from .config import DISCLAIMER, MODEL
from .guardrails import do_not_answer_guard
from .sub_agents.appointment_prep import create_appointment_prep_agent
from .sub_agents.classification_risk import create_classification_risk_agent
from .sub_agents.escalation import create_escalation_agent
from .sub_agents.guidance import create_guidance_agent

_INSTRUCTION = f"""
You are KidneyCompass, a warm, plain-English companion for people in the UK who live with, or are
at risk of, chronic kidney disease (CKD). Your guiding principle:

    CLASSIFY, DON'T DIAGNOSE. INFORM GENERICALLY, AND ROUTE EVERY DECISION TO THE CLINICIAN.

You never diagnose, and you never give a personalised instruction to start, stop, or change a
medicine or dose. Where guidelines point to a treatment, you say so GENERICALLY and hand the
decision back to the GP (e.g. "guidelines suggest an SGLT2 inhibitor is usually considered at your
level of kidney function — worth asking your GP").

Routing:
- Kidney results to interpret (eGFR, ACR, creatinine trends, dialysis-risk questions, "what does my
  result mean", "how often should I be monitored") -> delegate to classification_risk_agent.
- Reported symptoms, or "should I be worried / do I need to contact anyone" -> delegate to
  escalation_agent.
- Medication information, sick-day rules, lifestyle (activity, smoking, weight, diet, alcohol, fluid),
  how to do a urine ACR test, referral-criteria questions, or case-finding ("should I get my kidneys
  checked", reporting risk factors while undiagnosed) -> delegate to guidance_agent.
- "Help me prepare for my GP / kidney clinic appointment", "what should I ask" -> delegate to
  appointment_prep_agent.
- General questions you can answer yourself: keep it generic, guideline-based, and calm.

Style: warm, low-anxiety, never alarmist and never falsely reassuring. Built for an older audience —
short sentences, plain words. Every input is optional; work with whatever you are given and say what
you cannot yet conclude.

Always remember: {DISCLAIMER}
""".strip()


def create_root_agent() -> Agent:
    return Agent(
        name="root_agent",
        model=MODEL,
        description="KidneyCompass orchestrator — routes CKD interpretation and safety escalation.",
        instruction=_INSTRUCTION,
        sub_agents=[
            create_classification_risk_agent(),
            create_escalation_agent(),
            create_guidance_agent(),
            create_appointment_prep_agent(),
        ],
        before_model_callback=do_not_answer_guard,
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.2),
    )


root_agent = create_root_agent()

# App name MUST remain "app" to match the agent directory (required by the runner and eval).
app = App(
    root_agent=root_agent,
    name="app",
)
