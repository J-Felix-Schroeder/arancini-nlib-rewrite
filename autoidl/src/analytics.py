_events = {}
_current = None
_tables = []

def record(event):
    _events[event] = _events.get(event, 0) + 1

def start():
    global _current
    _current = {"reasons": {}}
    _tables.append(_current)

def fill(field, value):
    _current[field] = value

def fill_record(field):
    _current["reasons"][field] = _current["reasons"].get(field, 0) + 1

def percent(part, whole):
    return str(round(100 * part / whole, 1)) + "%"

def sorted_reasons(reasons):
    ordered = []
    for name in reasons:
        ordered.append((reasons[name], name))
    ordered.sort(reverse=True)
    return ordered

def summarize():
    total = 0
    described = 0
    supported = 0
    for t in _tables:
        total += t["total_fn_count"]
        described += t["described_fn_count"]
        supported += t["supported_fn_count"]

    print("\ntotals")
    print("attempted libs:", _events.get("libs_attempted", 0))
    print("libs with dwarf available:", len(_tables))
    print("total exported functions:", total)
    print("functions with dwarf (described):", described)
    print("supported functions:", supported)
    if described:
        print("signature support (supported/described):", percent(supported, described))
    if total:
        print("dwarf completeness (described/total):", percent(described, total))
        print("overall intercepted (supported/total):", percent(supported, total))

    covs = []
    covsum = 0
    for t in _tables:
        if not t["described_fn_count"]:
            continue
        cov = 100 * t["supported_fn_count"] / t["described_fn_count"]
        covs.append((cov, t["soname"], t["reasons"]))
        covsum += cov

    if covs:
        print("average signature support (per lib):", percent(covsum, 100 * len(covs)))
        covs.sort()
        print("\nflop 25 signature support")
        for cov, soname, reasons in covs[:25]:
            print("  " + percent(cov, 100) + "  " + soname)
            for count, name in sorted_reasons(reasons):
                print("      ", count, name)

    holes = []
    total_missing = 0
    complete = 0
    for t in _tables:
        tot = t["total_fn_count"]
        desc = t["described_fn_count"]
        if not tot:
            continue
        total_missing += tot - desc
        if desc >= tot:
            complete += 1
            continue
        holes.append((100 * desc / tot, desc, tot, t["soname"]))

    print("\ndwarf holes (functions exported but missing from dwarf)")
    print("total exported functions missing from dwarf:", total_missing)
    print("libs fully described (100%, no holes):", complete)
    print("libs with holes (>=1 function missing):", len(holes))
    holes.sort()
    print("flop 25 dwarf completeness")
    for comp, desc, tot, soname in holes[:25]:
        print("  " + percent(desc, tot) + " dwarf  (" + str(desc) + "/" + str(tot) + " described, " + str(tot - desc) + " missing)  " + soname)

    reasons = {}
    for t in _tables:
        for name in t["reasons"]:
            reasons[name] = reasons.get(name, 0) + t["reasons"][name]
    print("\ntop unsupported reasons (functions blocked)")
    for count, name in sorted_reasons(reasons):
        print("  ", count, name)
