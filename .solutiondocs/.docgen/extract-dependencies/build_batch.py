import json, re, subprocess, datetime, os

ROOT = r"C:\Users\sodeshpa\.copilot\repos\copilot-worktrees\ContosoUniversityTemp1\sodeshpa-animated-spoon"
OUT = os.path.join(ROOT, ".solutiondocs", ".docgen", "extract-dependencies")
APP = "application:sodeshpa-animated-spoon"
COMP = "component:contosouniversity"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def blob(rel):
    return subprocess.check_output(["git", "-C", ROOT, "hash-object", rel]).decode().strip()

def lines(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8-sig") as f:
        return f.read().splitlines()

PKG = "ContosoUniversity/packages.config"
CSPROJ = "ContosoUniversity/ContosoUniversity.csproj"
WEBCFG = "ContosoUniversity/Web.config"
srcs = {
    "packages-config": (PKG, "NuGet packages.config"),
    "csproj": (CSPROJ, "Project file"),
    "web-config": (WEBCFG, "Web.config"),
}
ops = []
def add(rec):
    ops.append({"record": rec, "expected_revision": 0})

def base(kind, id_):
    return {"id": id_, "record_kind": kind, "application_id": APP}

ev = {}
for key, (rel, nm) in srcs.items():
    sid = f"source_artifact:contosouniversity-{key}"
    r = base("node", sid)
    r.update(type="source_artifact", name=f"{nm} ({rel.split('/')[-1]})", status="active",
             properties={"location": rel, "revision": blob(rel), "source_type": "dependency_manifest" if key != "web-config" else "configuration"})
    add(r)
    ev[key] = sid

seen_ev = set()
def evidence(key, locator, method="dependency-manifest"):
    eid = "evidence:contosouniversity-deps-" + re.sub(r"[^a-z0-9]+", "-", (key + "-" + "-".join(map(str, locator.values()))).lower()).strip("-")
    if eid not in seen_ev:
        seen_ev.add(eid)
        r = base("evidence", eid)
        r.update(status="active", source_id=ev[key], locator=locator, method=method,
                 source_revision=blob(srcs[key][0]), observed_at=NOW, scope_id=COMP)
        add(r)
    return eid

csproj_lines = lines(CSPROJ)
pk = []
for i, l in enumerate(lines(PKG), 1):
    m = re.search(r'<package id="([^"]+)" version="([^"]+)" targetFramework="([^"]+)"', l)
    if m:
        pk.append((i, m.group(1), m.group(2), m.group(3)))

def csproj_line(pid):
    for i, l in enumerate(csproj_lines, 1):
        if re.search(r'Reference Include="%s[,"]' % re.escape(pid), l) or ("packages\\%s." % pid) in l:
            return i
    return None

FRAMEWORK = {"Microsoft.AspNet.Mvc", "Microsoft.AspNet.Razor", "Microsoft.AspNet.WebPages", "Microsoft.EntityFrameworkCore",
             "Microsoft.AspNet.Web.Optimization", "NETStandard.Library"}
BUILD = {"Microsoft.EntityFrameworkCore.Analyzers", "Microsoft.EntityFrameworkCore.Tools"}
TOOL = BUILD | {"Microsoft.CodeDom.Providers.DotNetCompilerPlatform"}
dep_ids = {}
for line, pid, ver_, tf in pk:
    did = "dependency:contosouniversity-nuget-" + re.sub(r"[^a-z0-9]+", "-", pid.lower()).strip("-")
    slug = did.split("nuget-")[1]
    dep_ids[pid] = did
    e = evidence("packages-config", {"file": PKG, "line": line})
    dtype = "framework" if pid in FRAMEWORK else ("tool" if pid in TOOL else "library")
    scope = "build" if pid in BUILD else "runtime"
    d = base("node", did)
    d.update(type="dependency", name=pid, qualified_name=f"nuget:{pid}", status="active", scope_id=COMP,
             properties={"version": ver_, "dependency_type": dtype, "scope": scope})
    add(d)
    c = base("claim", "claim:contosouniversity-deps-declared-" + slug)
    c.update(subject=did, predicate="declared_version", value=ver_, derivation="observation", status="candidate",
             confidence=1.0, evidence_ids=[e], applicability={"source_revision": blob(PKG), "target_framework": tf}, scope_id=COMP)
    add(c)
    cl = csproj_line(pid)
    evs = [e]
    if cl:
        evs.append(evidence("csproj", {"file": CSPROJ, "line": cl}))
    c2 = base("claim", "claim:contosouniversity-deps-csproj-ref-" + slug)
    c2.update(subject=did, predicate="referenced_in_csproj", value=bool(cl), derivation="observation", status="candidate",
              confidence=0.95, evidence_ids=evs, applicability={"source_revision": blob(CSPROJ)}, scope_id=COMP)
    add(c2)
    c3 = base("claim", "claim:contosouniversity-deps-edge-" + slug)
    c3.update(subject=COMP, predicate="depends_on", target=did, derivation="observation", status="candidate",
              confidence=1.0, evidence_ids=[e], applicability={"source_revision": blob(PKG)}, scope_id=COMP)
    add(c3)
    rel = base("relationship", "relationship:contosouniversity-depends-on-" + slug)
    rel.update(type="depends_on", status="active", properties={}, claim_ids=[c3["id"]], scope_id=COMP)
    rel["from"] = COMP
    rel["to"] = did
    add(rel)

ver = {p: v for _, p, v, _ in pk}
e_pkg_ef = evidence("packages-config", {"file": PKG, "line": next(i for i, p, _, _ in pk if p == "Microsoft.EntityFrameworkCore")})
e_tfm = evidence("csproj", {"file": CSPROJ, "line": next(i for i, l in enumerate(csproj_lines, 1) if "TargetFrameworkVersion" in l)})
e_cfg = evidence("web-config", {"file": WEBCFG, "line": next(i for i, l in enumerate(lines(WEBCFG), 1) if 'compilation debug' in l)})
e_jq = evidence("csproj", {"file": CSPROJ, "line": next(i for i, l in enumerate(csproj_lines, 1) if "jquery-3.4.1.js" in l)})

comp = json.load(open(os.path.join(OUT, "component-current.json"), encoding="utf-8-sig"))
rev = comp.pop("revision")
for k in ("created_at", "updated_at"):
    comp.pop(k, None)
comp["properties"]["tech_stack"] = {
    "languages": [{"name": "C#"}],
    "frameworks": [
        {"name": "ASP.NET MVC", "version": ver["Microsoft.AspNet.Mvc"]},
        {"name": "Entity Framework Core", "version": ver["Microsoft.EntityFrameworkCore"]},
        {"name": ".NET Framework", "version": "4.8"},
    ],
    "build_tool": "MSBuild (legacy .csproj, NuGet packages.config)",
}
comp["properties"]["technology_obsolescence"] = [
    dict(name="Microsoft.EntityFrameworkCore", current_version=ver["Microsoft.EntityFrameworkCore"], eol_date="2022-12-13", eol_status="long_eol",
         security_updates=False, upgrade_breaking_changes=True, vendor_support_status="none",
         upgrade_path="Move to a supported EF Core release (requires a modern .NET runtime)"),
    dict(name="Microsoft.Extensions.* (Caching, Configuration, DependencyInjection, Logging, Options, Primitives)", current_version="3.1.32",
         eol_date="2022-12-13", eol_status="long_eol", security_updates=False, upgrade_breaking_changes=True, vendor_support_status="none"),
    dict(name="Microsoft.Data.SqlClient", current_version=ver["Microsoft.Data.SqlClient"], eol_status="eol", security_updates=False,
         upgrade_breaking_changes=False, vendor_support_status="none"),
    dict(name="Microsoft.Identity.Client", current_version=ver["Microsoft.Identity.Client"], eol_status="eol", security_updates=False,
         upgrade_breaking_changes=False, vendor_support_status="none"),
    dict(name="Modernizr", current_version=ver["Modernizr"], eol_status="long_eol", security_updates=False, vendor_support_status="community_only"),
    dict(name="Antlr", current_version=ver["Antlr"], eol_status="long_eol", security_updates=False, vendor_support_status="none"),
    dict(name="WebGrease", current_version=ver["WebGrease"], eol_status="long_eol", security_updates=False, vendor_support_status="none"),
    dict(name=".NET Framework", current_version="4.8", eol_status="current", security_updates=True, vendor_support_status="extended",
         upgrade_path="Supported with the Windows OS lifecycle; no new features"),
]

def pclaim(slug, pred, val, evs, conf, deriv="observation", subj=COMP):
    c = base("claim", "claim:contosouniversity-deps-" + slug)
    c.update(subject=subj, predicate=pred, value=val, derivation=deriv, status="candidate", confidence=conf,
             evidence_ids=evs, applicability={"source_revision": blob(PKG)}, scope_id=COMP)
    add(c)

pclaim("tech-stack-frameworks", "tech_stack.frameworks", comp["properties"]["tech_stack"]["frameworks"], [e_tfm, e_cfg, e_pkg_ef], 0.95)
pclaim("tech-stack-language", "tech_stack.languages", comp["properties"]["tech_stack"]["languages"], [e_tfm], 0.9, "static_inference")
pclaim("tech-stack-build-tool", "tech_stack.build_tool", comp["properties"]["tech_stack"]["build_tool"], [e_tfm], 0.9, "static_inference")
pclaim("technology-obsolescence", "technology_obsolescence", [o["name"] for o in comp["properties"]["technology_obsolescence"]],
       [e_pkg_ef, e_tfm], 0.85, "heuristic")
pclaim("target-framework-drift", "target_framework_declaration",
       "csproj TargetFrameworkVersion v4.8 and Web.config targetFramework 4.8, but packages.config targets net482", [e_tfm, e_cfg, e_pkg_ef], 0.95)
pclaim("jquery-version-drift", "declared_vs_shipped_version",
       "packages.config declares jQuery 3.7.1 while the csproj content list and Scripts folder ship jquery-3.4.1", [e_jq, e_pkg_ef], 0.9, "static_inference",
       subj=dep_ids["jQuery"])

debts = [
    ("eol-efcore-3-1", "End-of-life Entity Framework Core 3.1 and Microsoft.Extensions 3.1 stack", "high", "maintainability", "L",
     ["Microsoft.EntityFrameworkCore 3.1.32", "Microsoft.Extensions.* 3.1.32", "Support ended 2022-12-13"],
     "Data access and logging/DI run on an out-of-support stack with no vendor patches; blocks adopting current EF Core and .NET.", True,
     "Plan upgrade to a supported EF Core/.NET release together with host-framework modernization.", [e_pkg_ef]),
    ("outdated-sqlclient-identity", "Outdated SqlClient 2.1.4 and Identity.Client 4.21.1", "medium", "security", "M",
     ["Microsoft.Data.SqlClient 2.1.4", "Microsoft.Identity.Client 4.21.1", "Version-age indicator only; no advisory assessed here"],
     "Old data-access/auth client libraries; advisory status is assessed separately by dependency-vulnerability-analysis.", None,
     "Upgrade to supported releases compatible with the chosen EF Core version.", [e_pkg_ef]),
    ("abandoned-frontend-bundling", "Unmaintained Antlr 3.4.1, WebGrease 1.5.2 and Modernizr 2.6.2", "medium", "maintainability", "M",
     ["Antlr 3.4.1.9004", "WebGrease 1.5.2", "Modernizr 2.6.2", "Legacy ASP.NET bundling/minification chain"],
     "Dependencies of the legacy bundling pipeline have no active upstream.", None,
     "Replace with a maintained bundling/minification approach.", [e_pkg_ef]),
    ("manifest-drift", "Dependency manifest drift (jQuery version, target framework moniker)", "low", "maintainability", "S",
     ["packages.config jQuery 3.7.1 vs shipped jquery-3.4.1", "packages.config net482 vs csproj/Web.config 4.8"],
     "Declared and shipped versions disagree, so the effective client library versions are uncertain.", None,
     "Align packages.config, csproj and shipped static assets.", [e_jq, e_tfm, e_pkg_ef]),
]
for slug, title, sev, cat, eff, ind, imp, blocks, res, evs in debts:
    tid = "technical_debt:contosouniversity-" + slug
    t = base("node", tid)
    props = {"title": title, "severity": sev, "category": cat, "effort_size": eff, "extracted_indicators": ind,
             "business_impact": imp, "resolution_approach": res}
    if blocks is not None:
        props["blocks_modernisation"] = blocks
    t.update(type="technical_debt", name=title, status="active", scope_id=COMP, properties=props)
    add(t)
    c = base("claim", "claim:contosouniversity-deps-debt-" + slug)
    c.update(subject=tid, predicate="severity", value=sev, derivation="heuristic", status="candidate", confidence=0.8,
             evidence_ids=evs, applicability={"source_revision": blob(PKG)}, scope_id=COMP)
    add(c)
    c2 = base("claim", "claim:contosouniversity-deps-debt-edge-" + slug)
    c2.update(subject=COMP, predicate="has_debt", target=tid, derivation="heuristic", status="candidate", confidence=0.8,
              evidence_ids=evs, applicability={"source_revision": blob(PKG)}, scope_id=COMP)
    add(c2)
    r = base("relationship", "relationship:contosouniversity-has-debt-" + slug)
    r.update(type="has_debt", status="active", properties={}, claim_ids=[c2["id"]], scope_id=COMP)
    r["from"] = COMP
    r["to"] = tid
    add(r)

gaps = [
    ("transitive-tree", "structure", "documentable", "P2",
     "packages.config is flat and no packages.lock.json exists: which packages are direct versus transitive, and the dependency paths between them, cannot be established from the repository. Provide a restored package graph or confirm direct references.",
     [e_pkg_ef]),
    ("licenses-latest", "quality", "documentable", "P3",
     "License and latest-available version are not declared in packages.config/csproj and were not populated (no registry access). Obtain from NuGet metadata.",
     [e_pkg_ef]),
    ("client-asset-versions", "build_devops", "documentable", "P3",
     "packages.config declares jQuery 3.7.1/bootstrap 5.3.3 but the csproj and Scripts folder ship jquery-3.4.1 and an unversioned bootstrap.js; which version is actually served is unconfirmed.",
     [e_jq, e_pkg_ef]),
]
for slug, dom, gt, pr, prompt, evs in gaps:
    g = base("gap", "gap:contosouniversity-deps-" + slug)
    g.update(status="open", subject=COMP, domain=dom, knowledge_gap_type="unknown_unknown", gap_type=gt, priority=pr,
             prompt=prompt, owner_ids=[], evidence_ids=evs, scope_id=COMP)
    add(g)

ops.append({"record": comp, "expected_revision": rev})
json.dump(ops, open(os.path.join(OUT, "batch.json"), "w", encoding="utf-8"), indent=1)
print(len(ops), "ops;", len(pk), "deps")
