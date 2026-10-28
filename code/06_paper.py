"""Step 6: fill code/paper_template.tex from data/results.json, write release/paper/Hotham_Takeaways.tex and
compile it with xelatex (figures from step 5). Run: python3 code/06_paper.py
"""
import json, os, re, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Takeaways"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "f0": return f"{v:.0f}"
    if f == "f1": return f"{v:,.1f}"
    if f == "f2": return f"{v:.2f}".replace("-", "$-$")
    return tex(v)


def sub(m):
    path, _, f = m.group(1).partition("|")
    return fmt(get(path.strip()), f.strip() or "raw")


A = R["accuracy"]
rows = ""
for lab, key, fm in [("Names checked", "n", "n"), ("Sorted by the rules", "n_classified", "np"), ("Sorted right (precision)", "precision_pct", "p"),
                     ("Names that say the food", "n_known", "nk"), ("Caught by the rules (recall)", "recall_pct", "p")]:
    cells = []
    for s in "AB":
        for g in ("T", "R", "all"):
            d = A[s][g]
            cells.append(f"{d[key]:,}" if fm == "n" else f"{d[key]:,} ({d['classified_pct']:.0f}\\%)" if fm == "np" else f"{d[key]:,} ({d['known_pct']:.0f}\\%)" if fm == "nk" else f"{d[key]:.1f}\\%")
    rows += lab + " & " + " & ".join(cells) + "\\\\\n"
TA = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Hand checks of the name rules. Sample A was used while writing the rules; sample B was drawn after "
      "they were fixed and is the held-out test. T takeaways, R restaurants.}\\label{tab:acc}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{lrrrrrr}\\toprule & \\multicolumn{3}{c}{Sample A (development)} & \\multicolumn{3}{c}{Sample B (held out)}\\\\"
      " & T & R & All & T & R & All\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(HERE, "paper_template.tex")).read()
t = re.sub(r"\{\{(?!TABLE_)(.+?)\}\}", sub, t).replace("{{TABLE_ACC}}", TA)
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w").write(t)
for _ in range(2):
    subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, stdout=subprocess.DEVNULL)
shutil.copy(os.path.join(OUT, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
for ext in (".aux", ".log", ".out", ".pdf"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
print("paper written")
