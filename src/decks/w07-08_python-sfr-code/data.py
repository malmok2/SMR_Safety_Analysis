"""이 덱의 그래프 자료(05_data.html)를 만든다.

교재 「파이썬으로 만드는 SFR 안전해석 코드」의 실습 코드 minisfr 를 직접 돌린다.
실행: python3 data.py "<Documents>/THINK Lab 파이썬으로 만드는 SFR 안전해석 코드 Rev1.0/code"
build.py 는 *.html 만 읽으므로 이 파일은 덱에 들어가지 않는다.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, sys.argv[1])
from minisfr import kinetics, scenarios, solver  # noqa: E402
from minisfr.params import Design  # noqa: E402
from minisfr.plant import Plant  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def pick(t, cols, t_max, n=160, log=False):
    """시각 배열을 n 점으로 줄인다(log 이면 로그 간격)."""
    t = np.asarray(t)
    if log:
        grid = np.concatenate(([0.0], np.logspace(0, np.log10(t_max), n)))
    else:
        grid = np.linspace(0.0, t_max, n)
    return [[round(float(g), 4)] + [round(float(np.interp(g, t, c)), 5)
                                   for c in cols] for g in grid]


out = {}
# 사고 4종 (run.py 와 같은 설정)
for name, t_end, dtm in [("plof", 600.0, 5.0), ("ulof", 600.0, 5.0),
                         ("utop", 1000.0, 5.0), ("ulohs", 72 * 3600.0, 60.0)]:
    p = getattr(scenarios, name)()
    ts, ys = solver.run(p.rhs, p.y0(), t_end, 0.01, theta=0.5, dt_max=dtm)
    P = p.power(ys)
    d = p.d
    tca = 0.5 * (ys[:, 15] + ys[:, 17])
    rf = d.a_fuel * (ys[:, 14] - p.tf0)
    rc = d.a_cool * (tca - p.tca0)
    rg = d.a_grid * (ys[:, 17] - d.t_in0)
    re = np.array([p.rho_ext(t) for t in ts])
    cols = [P, ys[:, 18] / p.m0, ys[:, 14], ys[:, 15], ys[:, 17],
            rf, rc, rg, re]
    out[name] = pick(ts, cols, t_end, 180 if name != "ulohs" else 400)
# 계단 반응도 (s09b 와 같은 설정)
beta, gen = 330e-5, 4.0e-7
steps = {}
for dol in [0.3, 0.1, -1.0]:
    rho = dol * beta

    def f(t, y, rho=rho):
        dn, dc = kinetics.rhs(y[0], y[1:], rho, beta, gen)
        return np.concatenate(([dn], dc))

    y0 = np.concatenate(([1.0], kinetics.c_steady(1.0, beta, gen)))
    ts, ys = solver.run(f, y0, 10.0, 1.0e-4, dt_max=0.05)
    steps[str(dol)] = pick(ts, [ys[:, 0]], 10.0, 120)
out["steps"] = steps
# B4 ULOHS 풀 배율
b4 = {}
for s in [1.0, 10.0, 100.0]:
    p = Plant(Design(), h_fixed=True, decay_heat=False)
    p.mc_h *= s
    p.mc_k *= s
    p.ua_rv = 0.0
    u0 = p.ua_ihx0
    p.ua_ihx = lambda t, u0=u0: u0 * max(1.0 - t / 10.0, 0.0)
    ts, ys = solver.run(p.rhs, p.y0(), 20000.0 * s, 0.01, dt_max=20.0 * s)
    b4[str(int(s))] = pick(ts / s, [ys[:, 17]], 20000.0, 120, log=True)
out["b4"] = b4
# B5 오차 (T(100 s))
p = scenarios.ulof()
y0 = p.y0()
te = np.linspace(0, 200, 2001)
ref = solve_ivp(p.rhs, (0, 200), y0, method="Radau", t_eval=te,
                rtol=1e-10, atol=1e-8)
b5 = {}
for th, nm in [(1.0, "BE"), (0.5, "CN")]:
    e = []
    for dt in [0.4, 0.2, 0.1, 0.05]:
        ts, ys = solver.run(p.rhs, y0, 200.0, dt, th)
        e.append(float(abs(np.interp(100.0, ts, ys[:, 15])
                           - ref.y[15][1000])))
    b5[nm] = e
out["b5"] = b5
js = "<script>\n/* 자동 생성 — data.py. 손으로 고치지 않는다. */\n"
js += "const PYD=" + json.dumps(out, separators=(",", ":")) + ";\n</script>\n"
open(os.path.join(HERE, "05_data.html"), "w").write(js)
print("05_data.html", len(js) // 1024, "KB")
