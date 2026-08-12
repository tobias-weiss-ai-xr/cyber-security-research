#!/usr/bin/env python3
"""Phase-2b: regenerate extraction evidence tables (rq1-5.md).

Reads docs/research/extraction/final_shortlists.json and fills the
protocol extraction columns (Setting / Population / Intervention /
Measures / Outcomes / Limitations / Notes) from the EXTRACTION map
below — abstract-level extraction (tiers provisional until full-text
review). Rows without a map entry stay TBD.

Usage:
    python3 tools/extract_rows.py
"""

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTION_DIR = os.path.join(BASE, "docs", "research", "extraction")

QUESTIONS = {
    "RQ1": "Which conceptualizations and stage models of AI literacy exist, and which have empirical support?",
    "RQ2": "Which implementation strategies for organization-level AI-literacy programs are evidenced, and under which conditions do they work?",
    "RQ3": "How is AI literacy measured — which instruments exist, with what validity — and which evaluation frameworks apply to programs?",
    "RQ4": "What evidence links AI-literacy training to behavior change, productivity and firm performance?",
    "RQ5": "How do organizations operationalize EU AI Act Art. 4 literacy obligations in practice?",
}

# (rq, title-fragment) -> (Setting, Population, Intervention, Measures,
#                          Outcomes, Limitations, Notes)
EXTRACTION = {
    # ---------------- RQ1: constructs & stage models ----------------
    ("RQ1", "A Conceptual Exploration of Generative AI-Induced"):
        ("Higher-education academic writing", "University students",
         "GenAI-induced cognitive dissonance (CD) construct", "Conceptual synthesis",
         "CD as trigger+amplifier; mitigations: reflective pedagogy, AI literacy programs, transparency",
         "Hypothetical construct; no primary data", "Construct evidence for Guide 1"),
    ("RQ1", "Rethinking Generative AI Literacy"):
        ("K-12 teacher education", "67 studies (2023-25)",
         "RAIL-Ed framework (integrative, developmental, dialectical)", "Systematic review + framework analysis",
         "GenAI literacy lag; ethics as constitutive commitment; equity & agency",
         "Framework from review, not primary data", "★ recent (2026-08); RQ1 synthesis core"),
    ("RQ1", "Artificial Intelligence Literacy in Counselor Education"):
        ("Counselor education", "Counselors-in-training (CITs)",
         "DALF: developmental AI literacy framework", "Conceptual model",
         "3 stages: foundational awareness → reflective application → integrated professionalization",
         "Conceptual; discipline-specific", "Stage model example for tiering"),
    ("RQ1", "AI-Mediated Relational Competence"):
        ("Medical education", "Clinicians",
         "Construct rationale + curriculum maturity framework", "Preprint review",
         "Relational competencies gap when AI mediates patient encounter",
         "Preprint; not peer-reviewed", "Construct landscape"),
    ("RQ1", "Fostering Transversal Skills Through Open Schooling"):
        ("Open schooling, underserved communities", "Students/community",
         "CARE-KNOW-DO pedagogical model + UNESCO AI competencies", "Empirical validation",
         "AI competencies emerge through social learning ecosystems",
         "Abstract unavailable", "Verify via Springer"),
    ("RQ1", "From G-Factor to A-Factor"):
        ("Adults/students (lab)", "N=517 across 3 studies",
         "18-item assessment battery (4 dimensions)", "3 sequential validation studies",
         "Dominant A-factor accounts for 44.16% variance; communication, idea generation, content evaluation, collaboration",
         "Lab settings; WEIRD samples", "★ psychometric construct evidence (RQ1+RQ3)"),
    ("RQ1", "Strategic Integration of AI Chatbots in Physics Teacher"):
        ("University teacher-preparation capstone", "Pre-service teachers",
         "TPACK-guided SWOT: 3 chatbot-assisted activities", "Qualitative (reflections, artifacts)",
         "Strengths: information-seeking, scaffolded planning, symbolic reasoning",
         "Single course context", "Pedagogy input for Guide 1"),
    ("RQ1", "A framework for AI ethics literacy"):
        ("Higher education", "Students",
         "AI ethics literacy framework (knowledge-based)", "Framework development + validation",
         "Framework links to self-rated learning competence with AI",
         "Abstract unavailable", "Ethics dimension"),
    ("RQ1", "How to Assess AI Literacy"):
        ("K-12 education", "Teachers",
         "SR + OB measures within Concept/Use/Evaluate/Ethics framework", "CFA + latent profile analysis",
         "Low SR-OB correlation; prior AI literacy experience shapes the relationship",
         "K-12 teachers only", "★ SR-vs-OB evidence for Guide 2"),
    ("RQ1", "FALCON-AI"):
        ("Higher education", "University faculty",
         "FALCON-AI scale (CTRL framework; 43 items → concise)", "Scale development + validation",
         "Three literacies (functional, critical, ...); role-embedded indicators",
         "Faculty-specific", "★ instrument for RQ3 too"),
    ("RQ1", "The LLM Fallacy"):
        ("Cognitive workflows (writing, programming, analysis)", "Individual users",
         "LLM fallacy construct (misattribution)", "Conceptual + case analysis",
         "Systematic divergence between perceived and actual capability",
         "New construct; needs replication", "RQ1 mechanism evidence"),
    ("RQ1", "UNESCO's AI Competency Framework"):
        ("Education contexts", "Teachers and students",
         "UNESCO AI competence framework", "Framework review",
         "Challenges: ethics, contextual adaptability, assessment, professional growth",
         "Review, not empirical", "Context anchor for frameworks"),
    ("RQ1", "School librarians developing AI literacy"):
        ("School libraries", "Teachers and librarians",
         "AI Citizenship Framework with scope & sequence", "Theoretical framework",
         "Foundational knowledge, critical thinking, ethical decision-making",
         "Conceptual", "Design input"),
    ("RQ1", "From AI Intuition to AI Literacy"):
        ("K-12 education", "Students",
         "AI intuition construct (experiential learning)", "Position paper",
         "Intuition precedes formal concepts; complements literacy",
         "Position paper", "Pedagogy input"),
    ("RQ1", "From AI Literacy to AI Fluency"):
        ("Higher education", "Students, faculty, staff",
         "6-level developmental AI Fluency framework", "Conceptual article",
         "Literacy insufficient; fluency = strategic, critical, ethical, contextual use",
         "Conceptual; no empirical test", "★ stage model for ALaaS tiering"),
    ("RQ1", "Towards Rhetorical AI Literacy"):
        ("General (communication contexts)", "AI users",
         "Rhetorical AI literacy framework", "Conceptual framework",
         "3 domains: pragmatism, interface design, discourse",
         "Conceptual", "Construct landscape"),
    ("RQ1", "Preparing K–12 Students With AI Literacy"):
        ("K-12 education", "Students",
         "Framework + hypothesized learning progression + task design (ECD)", "Evidence-centered design review",
         "Competencies incl. ethical decision-making, AI-powered collaboration; behavior indicators",
         "Progression hypothesized, not validated", "★ assessment design principles"),
    ("RQ1", "From Understanding to Creation"):
        ("Higher education (George Mason)", "Undergraduates across majors",
         "UNIV 182 course: 5 mechanisms (pipeline, ethics, AI Studios, portfolio, ...)", "Course report",
         "Prerequisite-free technical depth; cumulative assessment portfolio",
         "Single institution", "★ course architecture example"),
    ("RQ1", "Democratizing Generative AI"):
        ("Firms", "Employees",
         "Cross-level framework: AI democratization (usefulness, ease, literacy)", "Conceptual framework",
         "AI literacy mediates org GenAI investment → sustainable competitive advantage",
         "Conceptual", "★ firm-level literacy framing for Guide 1"),
    ("RQ1", "Awareness of Technological Isomorphism"):
        ("Elementary mathematics education", "Students",
         "Awareness of Technological Isomorphism construct", "Case study",
         "Metacognitive transfer from math reasoning to AI comprehension",
         "Single classroom", "Construct + pedagogy"),
    ("RQ1", "Constructing Epistemic AI Literacy"):
        ("Student-AI co-programming", "Students",
         "Epistemic AI Literacy (EAIL) + AIR framework", "Qualitative study",
         "Epistemic aims and processes enacted in co-programming",
         "Context-specific", "Construct + method"),
    ("RQ1", "Uncovering Students' Mental Models"):
        ("Technology ethics course", "N=64 undergraduates",
         "Concept maps of GenAI", "Qualitative concept-map study",
         "Declarative/procedural/conditional knowledge in mental models",
         "Small sample", "Method for baseline assessment"),
    ("RQ1", "Assistant, Parrot, or Colonizing Loudspeaker"):
        ("Education (critical AI literacy)", "Researchers/educators",
         "Metaphor discussion (Selber multiliteracies)", "Collaborative autoethnography",
         "Metaphor analysis builds functional, critical, rhetorical literacy",
         "Self-reflective method", "Pedagogy input"),
    ("RQ1", "AI Thinking"):
        ("Practice contexts across disciplines", "Practitioners",
         "AI Thinking framework: 5 practice-based competencies", "Conceptual framework",
         "Motivating AI use, formulating AI methods, ... in context",
         "Conceptual", "Framework for practice"),
    ("RQ1", "AI Mindset"):
        ("Education (teachers)", "Teachers",
         "AI Mindset triadic model (dispositional, contextual, technology appraisals)", "Empirical model test",
         "Psychological factors shape AI competence and AI use",
         "Educational context", "★ empirical construct evidence"),

    # ---------------- RQ2: implementation strategies ----------------
    ("RQ2", "From AI Literacy to AI Use"):
        ("Multiple organizations (upskilling program)", "Employees across orgs",
         "UTAUT-based multi-organization AI literacy program", "Survey (UTAUT constructs)",
         "Adoption behavior after literacy program", "Provisional C; abstract only",
         "Confirm at full text"),
    ("RQ2", "EMPOWERING MSMEs"):
        ("Indonesian MSMEs (West Jakarta)", "N=35 MSME owners",
         "1-day Canva AI + ChatGPT training (prompts, copywriting, CTA)", "Participatory case report",
         "Digital marketing content-creation capacity",
         "Single event; no follow-up", "SME program example"),
    ("RQ2", "Preparing High School Teachers"):
        ("US high-school STEM classrooms", "Teachers",
         "5-day PD units (Data Analytics → Transfer learning)", "Experience report",
         "Scaffolded learning progression; ethics of bias",
         "Report; no outcome measures", "Curriculum architecture"),
    ("RQ2", "From Exposure to Adoption"):
        ("35 European countries", "EU workforce sample",
         "GenAI exposure/adoption (no formal program)", "Survey + shift-share design",
         "Workplace training steepens exposure-adoption gradient; gender gap in exposed occupations",
         "Country-level training proxy", "Effect on task restructuring not yet detectable"),
    ("RQ2", "AI Adoption and Workplace Training"):
        ("Firms/establishments (panel)", "Establishments",
         "AI adoption + workplace training", "Econometric panel",
         "Training complements adoption (key evidence: training mediates adoption ROI)",
         "SSRN preprint; abstract unavailable", "Verify published JEBO version"),
    ("RQ2", "Co-Designing an AI Literacy Curriculum"):
        ("Elementary education", "Teachers, administrators, parents",
         "Design-thinking co-design process", "Design case study",
         "Key challenges, pedagogical strategies, content",
         "Single district", "Co-design method for Guide 1"),
    ("RQ2", "A Study on the Visual Convergence Design Curriculum"):
        ("Korean design education", "Students",
         "GenAI-based AI information design course", "Literature review + survey + tool analysis",
         "Curriculum differences and effective teaching methods",
         "Korean-language study", "Curriculum example"),
    ("RQ2", "Applying AI Tools to Develop a Curriculum"):
        ("Vietnamese HE, SME-dominated labor market", "Students",
         "AI tools: apriori algorithm, genetic algorithm for ELO-based curriculum", "Method development",
         "Expected learning outcomes quantified to credits; personalized learning",
         "Country-specific", "Curriculum method"),
    ("RQ2", "Assessment of Digital Capabilities by 9 Countries"):
        ("WHO healthy-cities network (Asia)", "Cities/municipalities",
         "AI-based digital capability assessment", "Cross-sectional analysis",
         "Capability profiles across 9 countries",
         "Framework-dependent", "Org readiness assessment method"),
    ("RQ2", "Artificial Intelligence in HR"):
        ("HR departments", "Employees",
         "AI in recruitment, performance evaluation, employee development", "Analysis/review",
         "Ethical challenges: bias, transparency, privacy, responsibility",
         "Review", "Context for Guide 1"),
    ("RQ2", "AN EVALUATION OF THE LONG-TERM EFFECTS"):
        ("IT sector", "N=174 IT professionals",
         "AI-integrated training programs", "Descriptive-correlational survey",
         "Performance development, adaptiveness, technology readiness over extended periods",
         "Cross-sectional; self-report", "★ training-outcome evidence"),
    ("RQ2", "Artificial Intelligence Adoption and Business Decision-Making"):
        ("Nigerian SMEs (Delta State)", "N=400 respondents",
         "AI adoption with employee training + leadership support", "Survey + regression",
         "Data readiness, employee training, leadership support influence decision-making",
         "Cross-sectional", "★ SME evidence"),
    ("RQ2", "The human side of AI adoption"):
        ("Manufacturing SMEs", "Employees (survey)",
         "Technical capability, technostress, well-being; training as moderator", "Cross-sectional SEM",
         "TC→AIA positive; TS→AIA/EWB negative; training moderates",
         "Cross-sectional; self-report", "★ org conditions — key for Guide 1"),
    ("RQ2", "AI Governance for Workforce Development"):
        ("National digital strategies", "Workforce",
         "AI governance framework for reskilling/upskilling", "Conceptual framework",
         "Bias, opacity, data-abuse risks in reskilling governance",
         "Conceptual", "Governance angle"),
    ("RQ2", "Enterprise AI Upskilling at Scale"):
        ("Large banks (Citi 175k, JPM, BofA, WF)", "Enterprise workforce",
         "Prompt-engineering training programs", "Case analysis",
         "Success factors: adaptive learning design, continuous upskilling, psychological safety",
         "Practitioner analysis", "Citable practitioner evidence"),
    ("RQ2", "Bridging the AI skills gap"):
        ("UK / OECD context", "Workforce",
         "Upskilling programs (OECD)", "Report",
         "TBD — abstract unavailable", "—", "Verify via OECD"),
    ("RQ2", "Design of an Intelligence-Based AI Literacy Curriculum"):
        ("Primary schools", "Students",
         "Intelligence-based curriculum, 6 competencies, performative learning", "Curriculum design study",
         "AI thinking as new agent for critical creation/evaluation",
         "Proposal", "Curriculum example"),
    ("RQ2", "Sustainable AI Literacy in Higher Education"):
        ("Higher education", "Undergraduates",
         "AWARE-AI study: environmental footprint awareness", "Chapter/study",
         "Ecological cost awareness → sustainable curriculum design",
         "Chapter-level", "Environmental angle"),
    ("RQ2", "Before Professional AI Fluency"):
        ("Business education", "Non-IT undergraduates",
         "Basic AI literacy as pre-PAF foundation", "Conceptual (abstract unavailable)",
         "Sequencing argument for business curricula",
         "Fetch error on abstract", "Curriculum sequencing"),
    ("RQ2", "Curriculum Design Principles for AI Literacy in Junior Primary"):
        ("Primary schools (USA, UK, China)", "Students",
         "Curriculum design (Bruner spiral, Piaget, Vygotsky, Tyler)", "Chapter",
         "Implementation approaches across countries",
         "Chapter-level", "Curriculum example"),
    ("RQ2", "Integrating AI ethics across the computing curriculum"):
        ("Computing curricula", "Students",
         "AI ethics integration", "Abstract unavailable", "TBD",
         "—", "Verify via Routledge chapter"),
    ("RQ2", "Developing a Curriculum for Ethical and Responsible AI"):
        ("University course", "Students",
         "Course on safety, fairness, privacy, ethics", "Abstract unavailable", "TBD",
         "—", "Verify via Springer chapter"),
    ("RQ2", "AI Is Not a Wildcard"):
        ("Design education", "Design students",
         "AI integration challenges in design curricula", "Abstract unavailable", "TBD",
         "—", "Verify via CHI paper"),
    ("RQ2", "Getting Practical About the Future of Work"):
        ("Oil & gas industry", "Workforce",
         "FoW upskilling/reskilling framework", "Practitioner framework",
         "Readiness varies by country, gender, generation; reskilling imperative (McKinsey 30-40%)",
         "Industry-specific", "Framework example"),

    # ---------------- RQ3: measurement & evaluation frameworks ----------------
    ("RQ3", "A study on the Development and Validity verification"):
        ("Korean university students", "Students",
         "AI literacy dimensions + questionnaire (domestic context)", "Survey validation",
         "Validity and reliability evidence",
         "Domestic (KR) context", "Instrument"),
    ("RQ3", "Teacher AI Literacy for Multilingual Learner Instruction"):
        ("Higher education", "Teachers",
         "Teacher AI literacy scale for ML instruction", "Scale development + factor analysis",
         "Factor structure; relation to responsible-use intentions and vignette decisions",
         "Convenience sample", "Instrument"),
    ("RQ3", "AI Literacy Assessment Instrument Dataset"):
        ("Scopus-indexed literature", "—",
         "Dataset of AI literacy assessment instruments (as of 2025-10-31)", "Dataset/registry",
         "Inventory of instruments", "Fetch error; verify", "★ instrument registry"),
    ("RQ3", "Evaluating AI Courses"):
        ("Undergraduate AI course", "Students",
         "SNAIL scale (non-experts' AI literacy)", "Course evaluation with validated instrument",
         "AI-learning gains measurement; quality assurance and comparability",
         "Single course", "★ instrument + gains"),
    ("RQ3", "Learning to Teach AI"):
        ("Non-university education", "Teachers",
         "5-dimension questionnaire on AI training quality", "Expert judgment + validation",
         "Knowledge/experience, benefits perception, training, expectations, practice impact",
         "National context", "Instrument"),
    ("RQ3", "GLAT"):
        ("Education", "Learners",
         "GLAT generative AI literacy assessment test", "TBD (abstract unavailable)",
         "TBD", "Abstract unavailable", "Journal: Computers and AI Education"),
    ("RQ3", "The EUIA scale"):
        ("Assessment contexts", "Students",
         "EUIA: 6 levels of GenAI interaction in assessment", "Case study + pilot",
         "Assignment instructions + design examples per level; digital skills overview",
         "Pilot-stage", "★ instrument + pedagogy"),
    ("RQ3", "The Scale of Artificial Intelligence Literacy for all"):
        ("Adults, any setting", "Adult population",
         "SAIL4ALL: 56 items, 4 themes", "Psychometric validation",
         "Themes usable independently: What is AI? What can AI do? How does AI work? How should AI be used?",
         "General adult scale", "★ instrument"),
    ("RQ3", "Standardized Assessment of Artificial Intelligence Literacy"):
        ("China, university students", "N=850",
         "MAIL-CS 32-item scale", "EFA/CFA split-sample",
         "4 factors (Foundational Knowledge & Ethics, Operational Skills, Critical Evaluation, Application & Innovation); α=.91 ω=.92",
         "Student sample; country-specific", "★ strong instrument for Guide 2"),
    ("RQ3", "Objective Measurement of AI Literacy"):
        ("Adults/general", "Scale development",
         "AICOS objective AI competency scale", "Validation study",
         "Objective measurement; integrates GenAI literacy dimension",
         "Abstract partial", "Complements self-report scales"),
    ("RQ3", "Multinational validation of the Arabic version"):
        ("Arab countries", "Adults",
         "Arabic AILS validation", "Abstract unavailable", "TBD",
         "—", "Verify via Cogent"),
    ("RQ3", "Exploring the Construction of an Standard AI Literacy Framework"):
        ("Middle school (China)", "Students",
         "Standard AI literacy framework", "Abstract unavailable", "TBD",
         "—", "Verify via ICAIE"),
    ("RQ3", "Navigating the Challenges of AI Literacy Assessment"):
        ("Rural educators (Western China)", "Educators",
         "AI literacy assessment for rural contexts", "Abstract unavailable", "TBD",
         "—", "Verify via L@S"),
    ("RQ3", "The Development and Validation of the Artificial Intelligence Literacy Scale"):
        ("Chinese college students", "Students",
         "AILS for Chinese college students", "Abstract unavailable", "TBD",
         "—", "Verify via IEEE Access"),
    ("RQ3", "Measuring How Students Rely on Generative AI"):
        ("Undergraduate academic writing", "Students",
         "GenAI-RTS: 20-item, 4 reliance types", "Development + validation",
         "Theoretically derived reliance types",
         "Writing context", "Instrument"),
    ("RQ3", "Charting Competence"):
        ("Adults", "Adults",
         "Holistic AI literacy scale (individual, interactive, sociocultural)", "Scale development",
         "Cognitive, behavioral, normative competencies",
         "—", "Instrument"),
    ("RQ3", "NAIL-G"):
        ("Nursing", "Nurses",
         "Nursing AI literacy + governance framework (socio-technical)", "Best-fit framework synthesis",
         "Discipline-specific literacy + patient safety/equity",
         "Synthesis-based", "Sector framework"),
    ("RQ3", "AI Literacy Assessment Revisited"):
        ("Workplace / occupations", "Non-STEM workers",
         "Task-oriented AI literacy assessment", "Position/study",
         "Occupation-aligned assessment over technical knowledge",
         "—", "★★ key for assessment spec"),
    ("RQ3", "Dimensions of Artificial Intelligence Literacy"):
        ("Education & workforce", "—",
         "Systematic review 2019-2024", "Qualitative synthesis",
         "6 dimensions: technical, ethical/societal, critical, ...",
         "Review", "★ synthesis for Guide 2"),
    ("RQ3", "Artificial intelligence literacy education in primary schools"):
        ("Primary schools", "Students",
         "Review of AI literacy education content", "Review",
         "Theoretical frameworks, pedagogy, content overview",
         "Review", "Synthesis input"),
    ("RQ3", "Artificial intelligence literacy: a proposed faceted taxonomy"):
        ("Education & research", "—",
         "Faceted taxonomy of AI literacy", "Facet analysis",
         "Taxonomy from literature + classification schemes",
         "Taxonomy proposal", "★ taxonomy"),

    # ---------------- RQ4: training → outcomes ----------------
    ("RQ4", "PAPER 9: THE PRODUCTIVITY REVOLUTION"):
        ("Organizations (RRC-AI)", "Practitioners",
         "RRC-AI System Writing implementation", "Economic analysis",
         "Per-practitioner training $12-25K → $150-300K productivity gains",
         "Self-published series; verify source quality", "Practitioner ROI model"),
    ("RQ4", "Return on Investment in Training and Performance Improvement Programs"):
        ("Organizations", "Trainees",
         "ROI methodology for training (Phillips-style)", "Framework (2012 book)",
         "ROI measurement approach for training programs",
         "Not AI-specific", "★ framework legacy for Guide 2"),
    ("RQ4", "Measuring the Return on Investment in Training"):
        ("Organizations", "Trainees",
         "ROI measurement in training", "Framework (2024 book chapter)",
         "ROI measurement approach",
         "Not AI-specific", "Framework legacy"),
    ("RQ4", "The impact of organizational adoption of Artificial Intelligence"):
        ("Workplaces", "N=303 employees",
         "Org AI adoption → employee learning behavior", "Survey + mediation analysis",
         "Job insecurity and job crafting chain-mediate AI adoption → self-directed learning",
         "Cross-sectional", "★ learning-behavior mechanism"),
    ("RQ4", "AI Adoption and Employee Outcomes"):
        ("Workplace employees", "Pooled studies",
         "Augmentation vs automation mechanisms", "Meta-analysis",
         "TBD — abstract unavailable", "Proceedings abstract",
         "Confirm effect sizes at full text"),
    ("RQ4", "Training for Obsolescence"):
        ("Education systems / policy", "Educational planner model",
         "Theoretical model + pre-registered pilot", "Theory (model)",
         "Over-investment in AI-teachable skills destined for obsolescence; policy caution",
         "Theory tier E; pilot correlation", "★ Guide 1 risk section — training trap"),
    ("RQ4", "Generative AI in Computer Science Education"):
        ("Professional training course", "N=86 adult learners",
         "ChatGPT in self-paced Python module (16-week course)", "Course evaluation",
         "Python learning outcomes with GenAI integration",
         "Single program", "Training evidence"),
    ("RQ4", "Employee Well-being in the Age of AI"):
        ("HR processes", "Employees",
         "AI in recruitment, performance, engagement", "Survey/analysis",
         "Well-being, job security, fairness, retention perceptions",
         "—", "Context"),
    ("RQ4", "RAG-PRISM"):
        ("4IR workforce (older workers)", "Workers",
         "Adaptive retrieval skill-mastery framework", "Framework",
         "Rapid cost-effective upskilling; persistence",
         "Framework", "Tool"),
    ("RQ4", "Personality-Aware Course Recommender System"):
        ("TVET education", "Students",
         "Personality-aware deep-learning recommender", "ML study",
         "Learning outcomes, ROI, dropout reduction",
         "—", "Tool"),
    ("RQ4", "The AI Skills Shift"):
        ("Labor market (O*NET)", "35 skills / 263 tasks",
         "SAFI index (4 LLMs, 1,052 model calls)", "Benchmark",
         "Skill automation feasibility; obsolescence mapping",
         "Model-based", "★ skill-shift evidence"),
    ("RQ4", "Emergent Learner Agency"):
        ("Collaborative learning", "Students",
         "Supportive vs contrarian AI personas (undisclosed teammate)", "Experiment",
         "Learner agency and group dynamics",
         "Lab setting", "Mechanism"),
    ("RQ4", "The Future of Food"):
        ("Food manufacturing", "Workforce",
         "AI adoption review", "Review",
         "Skills gap between data scientists and domain experts",
         "—", "Context"),
    ("RQ4", "Empa"):
        ("HPC education", "Students",
         "AI-powered virtual mentor (intercultural collaboration)", "Case study",
         "Global collaboration skills",
         "—", "Tool"),
    ("RQ4", "Cultivating Multidisciplinary AI Workforce Development"):
        ("University (iTiger GPU cluster)", "Researchers/students",
         "GPU cluster + computational support", "Case study",
         "Adoption broadening across disciplines",
         "—", "Infrastructure"),
    ("RQ4", "Personalized Education with Generative AI and Digital Twins"):
        ("4IR training (URM communities)", "Workers",
         "gAI-PT4I4 personalized tutor (VR, RAG)", "Case study",
         "Personalized experiential learning",
         "—", "Tool"),
    ("RQ4", "Contrasting Attitudes Towards Current and Future AI"):
        ("Healthcare (UK)", "Clinicians",
         "ECG interpretation AI interviews", "Qualitative interviews",
         "Trust, explainability needs",
         "—", "Attitudes"),
    ("RQ4", "Integration of AI Training in the Field of Higher Education"):
        ("Bulgarian HEIs", "163 BA + 239 MA programs",
         "AI training program availability evaluation", "Survey",
         "Program coverage in 4 professional fields",
         "—", "Landscape"),
    ("RQ4", "How Novice Programmers Use and Experience ChatGPT"):
        ("Introductory programming", "Students",
         "ChatGPT usage in exercises", "Study",
         "Use patterns; implications for assessment",
         "—", "Behavior"),
    ("RQ4", "AI-Assisted X-ray Fracture Detection in Residency Training"):
        ("Radiology residency", "4 residents / 200 radiographs",
         "AI-assisted fracture detection program", "Retrospective evaluation",
         "Resident performance in pediatric + adult trauma",
         "Retrospective", "Training evaluation"),
    ("RQ4", "Developing AI-powered Training Programs for Employee Upskilling"):
        ("Organizations", "Employees",
         "AI-powered training programs for upskilling/reskilling", "Abstract unavailable",
         "TBD", "—", "Verify via journal"),
    ("RQ4", "Upskilling or deskilling?"):
        ("Radiology residency", "8 residents / 150 CXRs",
         "AI-supported training (no-AI vs on-demand vs integrated AI)", "Within-subjects experiment",
         "Diagnostic scoring performance; upskilling vs deskilling measurable effect",
         "Small sample; single task", "★ strongest training-outcome design in RQ4"),
    ("RQ4", "AI-accelerated End-to-End Framework for Rapid Professional Upskilling"):
        ("Enterprise", "Workers",
         "5-stage AI-accelerated upskilling framework", "Framework",
         "Time-to-close skills gap (3d 2014 → 36d 2018); production + learning efficiency",
         "Industry validation pending", "★ framework"),
    ("RQ4", "The Impact of AI and Machine Learning on Recruitment"):
        ("Organizations", "Employees",
         "AI/ML in recruitment and performance management", "Abstract unavailable",
         "TBD", "—", "Verify via review journal"),
    ("RQ4", "The Impact of AI-driven Strategy on Salespeople Training"):
        ("Pharmaceutical sales (Pakistan)", "N=178 reps + managers",
         "AI-driven training solutions (customized instructional methods)", "SEM-PLS",
         "AI-driven training improves salesperson training and performance",
         "Single country/industry", "★ training→performance evidence"),

    # ---------------- RQ5: Art. 4 operationalization ----------------
    ("RQ5", "Three Frameworks, One System"):
        ("Enterprise AI governance", "Organizations",
         "EU AI Act + NIST AI RMF + (ISO) convergence toolkit", "Practitioner toolkit",
         "Governance crosswalk + implementation guidance",
         "Fetch error on abstract", "Practitioner reference"),
    ("RQ5", "EU AI Act: what could AI literacy mean for medical laboratories"):
        ("Medical laboratories", "Lab staff",
         "Article 4 training-curriculum development guidance", "Opinion paper (DGKL)",
         "Interpretation of 'sufficient' AI literacy; curriculum help",
         "Sector opinion", "★ sector operationalization"),
    ("RQ5", "AI literacy in healthcare organisations"):
        ("Healthcare organisations", "Clinical/admin/technical roles",
         "M-SHALF modular stratified framework", "Framework + case",
         "Literacy as governance infrastructure; role-specific knowledge needs",
         "Framework proposal", "★★ most concrete Art. 4 operationalization"),
    ("RQ5", "Artificial Intelligence Legislation Literacy"):
        ("Romanian healthcare", "N=109 professionals",
         "20-item AI Legislation Literacy measure + governance readiness", "Multicenter cross-sectional survey",
         "Confidence mediates legislation-literacy → adoption link; implementation phenotypes",
         "Cross-sectional; small N", "★★ empirical Art. 4-adjacent evidence"),
    ("RQ5", "The EU AI Act: implications and compliance guidance for healthcare"):
        ("Healthcare facilities", "Deployers",
         "Qualitative regulatory analysis (deployer obligations)", "Regulatory analysis",
         "Transition from legal theory to clinical compliance",
         "Sector-specific", "★ compliance guidance"),
    ("RQ5", "Human-as-Conductor"):
        ("Organizations (Art. 4)", "Users",
         "HaC framework: user as conductor of interactive AI", "Framework document",
         "Practical non-technical literacy framework for Art. 4",
         "Zenodo document", "Fetch via Zenodo API"),
    ("RQ5", "AI Literacy Under the AI Act"):
        ("EU law/policy", "Legislative text",
         "Analysis of Art. 4 evolution (May 2023 → trilogue)", "Legal analysis",
         "Art. 4 pared down from comprehensive obligation; efficacy concerns",
         "Legal analysis tier E", "★ compliance narrative"),
    ("RQ5", "AI Literacy and Other Obligations for the Employer"):
        ("EU employers", "Companies using AI",
         "Employment-relations obligations analysis", "Legal analysis",
         "Obligations timeline; employment perspective",
         "Tier E", "Compliance checklist input"),
    ("RQ5", "AI Literacy for Legal AI Systems"):
        ("Legal/judicial sector", "Deployers and providers",
         "AI literacy as compliance tool for legal AI systems", "Practical approach",
         "Literacy as legal requirement + ethical enabler",
         "Sector-specific", "Sector operationalization"),
    ("RQ5", "AI Act Evaluation Benchmark"):
        ("NLP compliance evaluation", "Organizations",
         "Open evaluation dataset for AI Act compliance", "Benchmark",
         "Semi-automated compliance evaluation",
         "Technical", "Technical compliance"),
    ("RQ5", "Position: EU AI Act's Research Exemptions"):
        ("AI research", "Researchers",
         "Research-exemption analysis", "Position paper",
         "Obligations may break publication norms",
         "Position", "Context"),
    ("RQ5", "The Dilemma of Uncertainty Estimation"):
        ("GPAI providers", "Providers",
         "Uncertainty estimation as compliance measure", "Analysis",
         "GPAI compliance solutions",
         "Technical", "Technical compliance"),
    ("RQ5", "Workforce Readiness and Article 4 AI Literacy Compliance"):
        ("Organizations", "Staff",
         "Art. 4 obligations + programme design analysis", "Analysis",
         "Workforce readiness gap: 46% of orgs (McKinsey 2025); Art. 26(2) interplay",
         "—", "★★ directly on point"),
    ("RQ5", "From Obligation to Specification"):
        ("Requirements engineering", "Organizations",
         "LLM-based validation tools for AI Act requirements", "Mixed-method exploratory",
         "Translation of obligations into testable requirements",
         "Exploratory", "Technical"),
    ("RQ5", "Bounding the Black Box"):
        ("High-risk AI", "—",
         "Statistical certification framework", "Theory",
         "Quantitative 'acceptable risk' definition",
         "Technical", "Technical"),
    ("RQ5", "Defining AI Models and AI Systems"):
        ("AI value chain", "—",
         "Model/system boundary framework (896 papers review)", "Systematic review",
         "Definitional lineages; provider/deployer obligations",
         "Review", "Context"),
    ("RQ5", "Responsible AI in Business"):
        ("SMEs", "SMEs",
         "Responsible AI: 4 focal areas (compliant, comprehensible, sustainable, data-sovereign)", "Framework",
         "Legally compliant AI operations for SMEs",
         "Framework", "★ SME governance"),
    ("RQ5", "Uncertainty-Calibrated Explainable AI"):
        ("Fetal ultrasound", "Clinicians",
         "XAI calibration review (78 studies)", "Systematic review",
         "Calibrated confidence for decision support",
         "Medical", "Technical"),
    ("RQ5", "Industrial AI Robustness Card"):
        ("Industrial time-series", "Practitioners",
         "IARC-TS robustness card protocol", "Protocol",
         "Drift/uncertainty/stress mapping to EU AI Act documentation",
         "Protocol", "Technical"),
    ("RQ5", "The notion of AI literacy in the context of employment"):
        ("Employers", "Workforce",
         "AI literacy obligation analysis (employment perspective)", "Analysis",
         "Upskilling + reskilling as multifaceted requirement",
         "—", "★★ employment literacy"),
    ("RQ5", "Futurity as Infrastructure"):
        ("AI lifecycle", "—",
         "Techno-philosophical AI Act interpretation", "Conceptual",
         "Recursive value chains in data lifecycle",
         "Conceptual", "Context"),
    ("RQ5", "Mapping Industry Practices to the EU AI Act's GPAI Code"):
        ("GPAI providers", "Leading AI companies",
         "GPAI Code of Practice Safety/Security comparison", "Report",
         "Commitments II.1-II.16 vs industry practice",
         "Report", "Technical"),
    ("RQ5", "Da Literacia às Práticas Proibidas"):
        ("EU law (Portuguese)", "—",
         "Art. 4 × Art. 5 articulation analysis", "Legal analysis",
         "TBD (abstract unavailable)", "Fetch error", "Verify via source"),
    ("RQ5", "Article 4 AI Act: AI Literacy"):
        ("EU law", "—",
         "Art. 4 analysis (SSRN)", "Legal analysis",
         "TBD — abstract unavailable", "—", "SSRN working paper"),
    ("RQ5", "Adapting to Regulation"):
        ("Dutch organizations", "Organizations",
         "EU AI Act influence on AI adoption", "Thesis (utupub)",
         "TBD — abstract unavailable", "—", "Verify via UTU Pub"),
}


def main():
    shorts = json.load(open(os.path.join(EXTRACTION_DIR, "final_shortlists.json"),
                            encoding="utf-8"))
    for rq, q in QUESTIONS.items():
        items = shorts["final"][rq]
        rows = []
        for i, e in enumerate(items, 1):
            sid = f"{rq}-{i:02d}"
            title = e["title"][:80]
            year = e["date"][:4] if e["date"] else "n.d."
            tier = e["tier"] or "TBD"
            vals = None
            for frag, v in EXTRACTION.items():
                if frag[0] == rq and frag[1].lower() in e["title"].lower():
                    vals = v
                    break
            if vals is None:
                vals = ("TBD",) * 7
            rows.append(f"| {sid} | {title} | {year} | {tier} | "
                        + " | ".join(vals) + " |")
        doc = f"""# Extraction Table — {rq}: {q}

**Protocol:** PROTOCOL.md §3-4 · {len(items)} papers · tiers provisional
(abstract-level) until full-text review · rows filled by
`tools/extract_rows.py` from fetched abstracts (arXiv API / CrossRef);
TBD cells await full-text extraction; drop rows that fail inclusion
criteria at full text (record reason in the last column).

| Study ID | Title | Year | Tier | Setting | Population | Construct/Intervention | Measures | Outcomes | Limitations | Notes |
|----------|-------|------|------|---------|------------|------------------------|----------|----------|-------------|-------|
"""
        doc += "\n".join(rows) + "\n"
        with open(os.path.join(EXTRACTION_DIR, f"{rq.lower()}.md"), "w",
                  encoding="utf-8") as f:
            f.write(doc)
        filled = sum(1 for e in items if any(
            frag[0] == rq and frag[1].lower() in e["title"].lower()
            for frag in EXTRACTION))
        print(f"Wrote {rq.lower()}.md ({len(rows)} rows, {filled} extracted)")


if __name__ == "__main__":
    main()
