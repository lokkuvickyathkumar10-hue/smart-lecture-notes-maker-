import streamlit as st, sqlite3, re, io
from pathlib import Path
from datetime import datetime

DB = Path(__file__).with_name("notes.db")
st.set_page_config(page_title="Smart Lecture Notes Maker", page_icon="✦", layout="wide")

def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
with conn() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, title TEXT, subject TEXT, method TEXT, content TEXT, created TEXT)""")

def get_notes():
    with conn() as c: return [dict(x) for x in c.execute("SELECT * FROM notes ORDER BY id DESC")]
def save(title,subject,method,content):
    with conn() as c: c.execute("INSERT INTO notes(title,subject,method,content,created) VALUES(?,?,?,?,?)",(title,subject,method,content,datetime.now().strftime("%d %b %Y %H:%M")))
def delete(nid):
    with conn() as c: c.execute("DELETE FROM notes WHERE id=?",(nid,))

def generate(title,subject,text,method):
    sents=[x.strip(" •-\t") for x in re.split(r'(?<=[.!?])\s+|\n+',text) if x.strip(" •-\t")]
    stop=set("the a an and or but is are was were be been of to in on for with by from as at this that it its".split())
    freq={}
    for w in re.findall(r"[a-zA-Z][a-zA-Z'-]+",text.lower()):
        if w not in stop and len(w)>3: freq[w]=freq.get(w,0)+1
    ranked=sorted(sents,key=lambda s:sum(freq.get(w,0) for w in re.findall(r"[a-zA-Z][a-zA-Z'-]+",s.lower()))/max(len(s.split()),1),reverse=True)
    points=ranked[:min(6,len(ranked))]
    defs=[s for s in sents if re.search(r'\b(is defined as|means|refers to|is called|are called)\b',s,re.I)]
    qs=[]
    for s in points[:5]:
        m=re.match(r'(.{2,55}?)\s+(?:is defined as|means|refers to|is called)\s+(.+)',s,re.I)
        qs.append("What is "+m.group(1).strip()+"?" if m else "Explain: "+ " ".join(s.split()[:5])+" …?")
    summary=" ".join(points[:3])
    if method=="Cornell Method":
        body="## Cue / Revision Questions\n"+"\n".join("- "+q for q in qs)+"\n\n## Lecture Notes\n"+"\n".join("- "+s for s in points)
    elif method=="Outline Method":
        body="## Main Ideas\n"+"\n".join(f"### {i}. {s}" for i,s in enumerate(points,1))+"\n\n## Revision Questions\n"+"\n".join(f"{i}. {q}" for i,q in enumerate(qs,1))
    elif method=="Mind Mapping":
        body="## Central Topic: "+title+"\n### Main Branches\n"+"\n".join(f"- Branch {i}: {s}" for i,s in enumerate(points,1))+"\n\n### Revision Branch\n"+"\n".join("- "+q for q in qs)
    else:
        body="## Lecture Chart\n| Point | Explanation |\n|---|---|\n"+"\n".join(f"| {i} | {s.replace('|','/')} |" for i,s in enumerate(points,1))+"\n\n## Revision Questions\n"+"\n".join(f"{i}. {q}" for i,q in enumerate(qs,1))
    return f"# {title}\n**Subject:** {subject}\n**Method:** {method}\n\n{body}\n\n## Key Definitions\n"+("\n".join("- "+d for d in defs) if defs else "- No clear definition phrase detected; review the main ideas.")+"\n\n## Short Summary\n"+summary

def make_pdf(text):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4); styles=getSampleStyleSheet(); story=[]
    for line in text.splitlines():
        safe=line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if not safe: story.append(Spacer(1,6))
        elif safe.startswith("# "): story.append(Paragraph(safe[2:],styles["Title"]))
        elif safe.startswith("## "): story.append(Paragraph(safe[3:],styles["Heading2"]))
        elif safe.startswith("### "): story.append(Paragraph(safe[4:],styles["Heading3"]))
        else: story.append(Paragraph(safe.replace("**",""),styles["BodyText"]))
    doc.build(story); return b.getvalue()

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Manrope:wght@600;700;800&display=swap');
.stApp{background:linear-gradient(135deg,#faf8ff,#f2edff,#fff);font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Manrope',sans-serif;color:#28194a}
.block-container{max-width:1150px;padding-top:1.5rem}
.hero{padding:2rem;border-radius:24px;color:white;background:linear-gradient(120deg,#48218a,#7546d2,#a78bfa);box-shadow:0 12px 30px #6d42c722}
.hero h1{color:white;font-size:clamp(2rem,5vw,3.2rem)}.hero p{color:#f4edff;font-size:1.05rem}
.card{background:white;border:1px solid #e9e0fa;border-radius:18px;padding:1rem;box-shadow:0 5px 18px #39245c0c}
div.stButton>button{border-radius:12px;font-weight:700;border-color:#d9ccf4}
div.stButton>button[kind=primary]{background:#7045c6;color:white;border:0}
[data-testid=stSidebar]{background:#f0eaff}
</style>""",unsafe_allow_html=True)

st.sidebar.markdown("## ✦ Smart Notes")
st.sidebar.caption("LECTURE NOTES MAKER")
page=st.sidebar.radio("MENU",["Home","Create Notes","My Notes","How It Works"])
st.sidebar.caption("Student-friendly study workspace")

if page=="Home":
    st.markdown('<div class="hero"><h1>Turn Every Lecture<br>into Smart Notes.</h1><p>Transform lecture content into clear, structured notes that are easier to understand, revise and remember.</p></div>',unsafe_allow_html=True)
    st.write("")
    if st.button("✦ Start Making Notes",type="primary",use_container_width=True): st.session_state.page="Create Notes"; st.rerun()
    st.subheader("Everything you need for better revision")
    cols=st.columns(3)
    for col,icon,title,desc in zip(cols,["🧠","🗂️","📥"],["Content-based notes","Four note methods","Save & download"],["Organize the lecture text you provide.","Cornell, Outline, Mind Mapping and Chart.","Save, search, edit and export notes."]):
        col.markdown(f'<div class="card"><h2>{icon}</h2><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
    notes=get_notes(); st.metric("Your saved notes",len(notes))
    st.markdown("**How it works:** Paste content → Choose a method → Generate → Edit & save → Revise.")
elif page=="Create Notes":
    st.subheader("Create your smart notes")
    title=st.text_input("Lecture title",placeholder="Introduction to Semiconductors")
    subject=st.text_input("Subject name",placeholder="Engineering Physics")
    raw=st.text_area("Paste lecture content",height=230,placeholder="Paste your class notes or lecture transcript here...")
    method=st.selectbox("Note-making method",["Cornell Method","Outline Method","Mind Mapping","Chart Method"])
    if st.button("✦ Generate Notes",type="primary",use_container_width=True):
        if not title.strip() or not subject.strip() or len(raw.strip())<40: st.error("Enter a title, subject and at least 40 characters of lecture content.")
        else:
            st.session_state.generated=generate(title.strip(),subject.strip(),raw.strip(),method)
            st.session_state.gtitle=title.strip(); st.session_state.gsubject=subject.strip(); st.session_state.gmethod=method
    if st.session_state.get("generated"):
        st.divider(); st.subheader("Review and edit generated notes")
        edited=st.text_area("Editable notes",value=st.session_state.generated,height=350,key="edit_generated")
        a,b=st.columns(2)
        if a.button("💾 Save Notes",type="primary",use_container_width=True):
            save(st.session_state.gtitle,st.session_state.gsubject,st.session_state.gmethod,edited); st.success("Notes saved in your library.")
        b.download_button("⬇ Download TXT",edited,file_name="smart_lecture_notes.txt",mime="text/plain",use_container_width=True)
        st.download_button("⬇ Download PDF",make_pdf(edited),file_name="smart_lecture_notes.pdf",mime="application/pdf",use_container_width=True)
        st.caption("Copy: select the note text above and use Copy from your phone's text-selection menu.")
elif page=="My Notes":
    st.subheader("Your saved notes")
    q=st.text_input("🔍 Search by title or subject")
    notes=[n for n in get_notes() if q.lower() in (n["title"]+" "+n["subject"]).lower()]
    st.caption(f"{len(notes)} note(s) found")
    if not notes: st.info("No notes found. Create and save a note first.")
    for n in notes:
        with st.expander(f"📘 {n['title']} · {n['subject']} · {n['created']}"):
            st.caption("Method: "+n["method"])
            edited=st.text_area("Edit note",n["content"],height=260,key=f"note_{n['id']}")
            c1,c2=st.columns(2)
            c1.download_button("Download TXT",edited,file_name=f"note_{n['id']}.txt",mime="text/plain",use_container_width=True)
            c2.download_button("Download PDF",make_pdf(edited),file_name=f"note_{n['id']}.pdf",mime="application/pdf",use_container_width=True)
            if st.button("Save edits",key=f"save_{n['id']}"):
                with conn() as c: c.execute("UPDATE notes SET content=? WHERE id=?",(edited,n["id"]))
                st.success("Changes saved."); st.rerun()
            if st.button("Delete note",key=f"del_{n['id']}"):
                delete(n["id"]); st.rerun()
else:
    st.subheader("How it works")
    for heading,desc in [
        ("1. Enter lecture content","Type a lecture title and subject, then paste your lecture material."),
        ("2. Select a method","Choose Cornell, Outline, Mind Mapping or Chart format."),
        ("3. Generate organized notes","Python text-processing logic ranks important sentences, detects definition phrases, creates revision prompts and summarizes the content."),
        ("4. Edit and save","Correct or expand the notes, then save them to your library."),
        ("5. Revise and download","Search saved notes and export them as TXT or PDF.")]:
        st.markdown(f'<div class="card"><h3>{heading}</h3><p>{desc}</p></div>',unsafe_allow_html=True); st.write("")
    st.info("This version uses real, rule-based Python text processing. No AI API is connected, so it does not pretend to use AI.")
st.divider()
st.caption("Smart Lecture Notes Maker · College project · SQLite local storage")
