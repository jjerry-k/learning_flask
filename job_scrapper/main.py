from flask import Flask, render_template, request, redirect, send_file

from extractors.remoteok import extract_remoteok_jobs
from extractors.wework import extract_weworkremotely_jobs

from file import save_to_file

app = Flask("JobScrapper")
db = {}
historys = []


@app.route("/")
def home():
    return render_template("home.html", name="jerry", history=historys)


@app.route("/search")
def search():
    keyword = request.args.get("keyword")

    if not keyword:
        return redirect("/")

    if keyword in db:
        jobs = db[keyword]
    else:
        remoteok = extract_remoteok_jobs(
            keyword) if keyword not in db else db["keywork"]
        weworkremotely = extract_weworkremotely_jobs(
            keyword) if keyword not in db else db["keywork"]
        jobs = remoteok + weworkremotely
        db[keyword] = jobs

    if keyword not in historys:
        historys.insert(0, keyword)
    if len(historys) > 5:
        historys.pop()
    
    return render_template("search.html", keyword=keyword, jobs=jobs)


@app.route("/export")
def export():
    keyword = request.args.get("keyword")

    if not keyword:
        return redirect("/")

    if keyword not in db:
        return redirect(f"/search?keyword={keyword}")
    save_to_file(keyword, db[keyword])
    return send_file(f"{keyword}.csv", as_attachment=True)


app.run("0.0.0.0", debug=True, port=5001)
