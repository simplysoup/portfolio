from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, HRFlowable, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'public'/'resume.pdf'
P.parent.mkdir(exist_ok=True,parents=True)
pdfmetrics.registerFont(TTFont('LiberationSans','/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSans-Bold','/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'))
pdfmetrics.registerFontFamily('LiberationSans',normal='LiberationSans',bold='LiberationSans-Bold')
INK=colors.HexColor('#1D2928'); MUTED=colors.HexColor('#425552'); RULE=colors.HexColor('#CED7D2')
base=ParagraphStyle('base', fontName='LiberationSans',fontSize=8.85,leading=11.65,textColor=INK,spaceAfter=2.3)
item=ParagraphStyle('item',parent=base,leftIndent=10,firstLineIndent=-7,spaceAfter=2.0)
heading=ParagraphStyle('heading',fontName='LiberationSans-Bold',fontSize=10.35,leading=14.0,textColor=INK,spaceBefore=7.4,spaceAfter=3.8)
job=ParagraphStyle('job',parent=base,fontName='LiberationSans-Bold',fontSize=9.2,leading=13,spaceBefore=4.2,spaceAfter=2.5)
small=ParagraphStyle('small',parent=base,fontSize=8.2,leading=11.5,textColor=MUTED)
name=ParagraphStyle('name',fontName='LiberationSans-Bold',fontSize=21,leading=24,textColor=INK,spaceAfter=3.5)
linkc='#235F5F'
def para(t,style=base):return Paragraph(t,style)
S=[]
S.append(para('Nicholas Bode',name))
S.append(para('Toronto, Ontario, Canada  ·  <link href="mailto:nickbode71@gmail.com" color="%s">nickbode71@gmail.com</link>  ·  <link href="https://github.com/simplysoup" color="%s">GitHub</link>  ·  <link href="https://www.linkedin.com/in/nicholas-bode-6a29ab1bb/" color="%s">LinkedIn</link>'%(linkc,linkc,linkc),small))
S.append(HRFlowable(width='100%',thickness=1,color=INK,spaceBefore=7,spaceAfter=6))
S.append(para('PROFILE',heading))
S.append(para('AI engineer focused on secure AI integrations, authorization, authenticated agent tools, evaluation workflows, and applied ML. Background in data-quality systems and original time-series research.'))
S.append(para('EXPERIENCE',heading))
S.append(para('Environics Analytics  ·  AI Engineer  |  April 2026–present',job))
for t in [
 'Implemented authorization enforcement for AI-connected search and tools, including hierarchy-aware access, audited administration, and access revocation.',
 'Designed and tested a remote agent-tool integration using OAuth2/PKCE, scoped access, and protected token storage; this work was a tested prototype, not a production launch.',
 'Contributed authenticated remote access and reporting SDK functionality to a team-owned agent-tool platform.',
 'Built human-review and evaluation workflows for model-assisted data matching and analytical changes, combining deterministic criteria, sample audits, and escalation.'
]:S.append(para('• '+t,item))
S.append(para('Environics Analytics  ·  Research Associate  |  February 2024–April 2026',job))
for t in [
 'Built recurring analytics quality checks, anomaly investigation tools, and release reporting workflows using Python and Snowflake.',
 'Compared data-product releases against external benchmarks and quality criteria, documented tradeoffs, and supported release recommendations.',
 'Investigated anomalous mobility trends by tracing upstream methodology and validation changes.'
]:S.append(para('• '+t,item))
S.append(para('EDUCATION & RESEARCH',heading))
S.append(para('<b>MSc, Computer Science — Ontario Tech University.</b> Thesis: <i>Discovery of Trend Dependencies Over Time-Series</i> (2023). Studied approximate and conditional relationships in noisy time-series data using symbolic regression, segmentation, and policy-gradient methods.'))
S.append(para('<b>BSc, Computer Science, Mathematics minor — Ontario Tech University</b> (2021).'))
S.append(para('<b>Publication:</b> Bode, N. &amp; Sukhai, M. (2024), <i>Automated Image Captioning for the Visually Impaired</i>, <i>Encyclopedia of Computer Graphics and Games</i>, Springer. <link href="https://doi.org/10.1007/978-3-031-23161-2_501" color="%s">DOI</link>.'%linkc))
S.append(para('SELECTED INDEPENDENT PROJECTS',heading))
S.append(para('<b>AgentShield — LLM Agent Security Evaluation Framework</b> — <link href="https://github.com/simplysoup/agent-shield" color="%s">github.com/simplysoup/agent-shield</link>'%linkc))
S.append(para('Built a paired prompt-injection evaluation framework for tool-using agents, with fixed attack replay, runtime tool-authorization checks, and structured audit traces.'))
S.append(para('<b>Evaluated RAG + Agentic System</b> — <link href="https://github.com/simplysoup/evaluated-rag-agentic" color="%s">github.com/simplysoup/evaluated-rag-agentic</link>'%linkc))
S.append(para('Synthetic-document retrieval benchmark comparing deterministic extraction with a tool-using agent; includes programmatic grounding checks, correction/abstention logic, and documented evaluation limitations.'))
S.append(para('TECHNICAL SKILLS',heading))
S.append(para('<b>Languages &amp; data:</b> Python, SQL, Snowflake, dbt, Pandas, scikit-learn, FastAPI. <b>AI systems:</b> MCP, LangGraph, OAuth2/PKCE, agent-tool infrastructure, LLM evaluation. <b>Engineering:</b> Azure, Docker, CI/CD, APIs, orchestration.'))
doc=SimpleDocTemplate(str(P),pagesize=letter,leftMargin=45,rightMargin=45,topMargin=31,bottomMargin=30,author='Nicholas Bode',title='Nicholas Bode — Résumé',subject='Public professional résumé')
doc.build(S)
print(P,P.stat().st_size)
