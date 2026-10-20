#!/usr/bin/env python3
"""Plot original figures from Julia output (NumPy + Matplotlib only).

    python scripts/plot_figures.py

The PNG and vector PDF have the same basename, so Quarto can select the most
appropriate format from an extensionless image reference.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGS = ROOT / "figs"
FIGS.mkdir(exist_ok=True)
TEAL, ORANGE, PURPLE = "#167d8d", "#c06636", "#6863ad"
INK, MUTED, GRID = "#1d3345", "#61717c", "#d9e2e5"
COLORS = [TEAL, ORANGE, PURPLE]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": "#b4c0c5", "axes.spines.top": False,
    "axes.spines.right": False, "axes.titleweight": "bold",
    "axes.titlesize": 11.5, "axes.labelsize": 10.5,
    "legend.frameon": False, "savefig.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})


def load(name):
    return np.genfromtxt(DATA / name, delimiter=",", names=True)


def save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def trajectories():
    d = load("trajectories.csv")
    fig, ax = plt.subplots(figsize=(8.2, 4.3), layout="constrained")
    t = np.linspace(0, 80, 100)
    ax.fill_between(t, -t, t, color=TEAL, alpha=.045)
    ax.plot(t, t, "--", color=MUTED, lw=1)
    ax.plot(t, -t, "--", color=MUTED, lw=1)
    palette = [TEAL, ORANGE, PURPLE, "#b09526", "#8f556e", "#527a4f"]
    for n, color in zip(range(1, 7), palette):
        a = d[d["path"] == n]
        ax.plot(a["time"], a["position"], lw=1.6, color=color)
    ax.text(78, 76, r"$x=vt$", ha="right", va="top", color=MUTED)
    ax.text(78, -76, r"$x=-vt$", ha="right", va="bottom", color=MUTED)
    ax.set(xlabel=r"Time $t/\tau_0$", ylabel=r"Position $x/(v\tau_0)$",
           xlim=(0, 80), ylim=(-83, 83),
           title=r"Long flights, finite speed: six independent walks ($\gamma=1.2$)")
    ax.grid(axis="y", color=GRID, lw=.6)
    save(fig, "trajectories")


def schematic():
    fig, ax = plt.subplots(figsize=(8.2, 3.7), layout="constrained")
    ts = np.array([0, 1.1, 3.3, 4.1, 6.8])
    xs = np.array([0, 1.1, 3.3, 2.5, 5.2])
    ax.plot(ts, xs, color=TEAL, lw=2.6, zorder=3)
    ax.scatter(ts[1:4], xs[1:4], color=ORANGE, s=42, zorder=4)
    ax.scatter(ts[-1], xs[-1], marker="s", color=PURPLE, s=55, zorder=4)
    ax.plot([6.8, 7.8], [5.2, 6.2], "--", color=TEAL, lw=2, alpha=.6)
    ax.axvline(6.8, color=PURPLE, lw=1, ls=":")
    ax.annotate("Renewal, same velocity", xy=(1.1, 1.1), xytext=(.2, 4.1),
                arrowprops={"arrowstyle": "->", "color": MUTED}, fontsize=10)
    ax.annotate("Renewal and turn", xy=(3.3, 3.3), xytext=(2.6, 5.6),
                arrowprops={"arrowstyle": "->", "color": MUTED}, fontsize=10)
    ax.annotate("Observation inside\nthe final flight", xy=(6.8, 5.2),
                xytext=(4.7, 1.0),
                arrowprops={"arrowstyle": "->", "color": MUTED}, fontsize=10)
    ax.text(7.35, 6.15, "Future", color=MUTED, ha="center", fontsize=9)
    for i in range(4):
        mid = (ts[i] + ts[i+1]) / 2
        ax.annotate("", xy=(ts[i+1], -.6), xytext=(ts[i], -.6),
                    arrowprops={"arrowstyle": "|-|", "color": MUTED})
        label = rf"$\tau_{i+1}$" if i < 3 else r"observed age $a$"
        ax.text(mid, -.9, label, ha="center", va="top", fontsize=10)
    ax.set(xlim=(-.1, 8), ylim=(-1.55, 6.8), xlabel="Time", ylabel="Position",
           title="An observation ends the record; it does not end the flight")
    ax.set_yticks([0, 2, 4, 6])
    ax.grid(axis="y", color=GRID, lw=.6)
    save(fig, "renewal-schematic")


def propagators():
    d = load("propagators.csv")
    f = load("front_masses.csv")
    fig, axs = plt.subplots(2, 3, figsize=(10.2, 6.0),
                            gridspec_kw={"height_ratios": [2.6, 1.15]},
                            layout="constrained")
    for j, (gamma, color) in enumerate(zip([.5, 1.5, 2.5], COLORS)):
        a = d[d["gamma"] == gamma]
        z = (a["left"] + a["right"]) / 2
        axs[0, j].stairs(a["density_z"], np.r_[a["left"], a["right"][-1]],
                         fill=True, color=color, alpha=.22, lw=1.5)
        axs[0, j].plot(z, a["density_z"], color=color, lw=1.1)
        axs[0, j].set(xlim=(-1.03, 1.03), ylim=(0, None),
                      xlabel=r"$z=x/(vt)$", title=rf"$\gamma={gamma}$")
        axs[0, j].grid(axis="y", color=GRID, lw=.6)
        row = f[f["gamma"] == gamma][0]
        p = np.array([row["front_minus"], row["front_plus"]]) / row["n"]
        p0 = np.array([row["no_renewal_minus"], row["no_renewal_plus"]]) / row["n"]
        axs[1, j].bar([0, 1], p, color=color, alpha=.55, width=.55)
        axs[1, j].bar([0, 1], p0, facecolor="none", edgecolor=INK, hatch="///", width=.55, lw=.8)
        axs[1, j].set_xticks([0, 1], [r"$z=-1$", r"$z=+1$"])
        axs[1, j].set_ylim(0, max(p.max()*1.5, 2/row["n"]))
        axs[1, j].ticklabel_format(axis="y", style="sci", scilimits=(-2, 2), useMathText=True)
        for xi, pi in enumerate(p):
            axs[1, j].annotate(f"{pi:.3g}", (xi, pi), xytext=(0, 4),
                               textcoords="offset points", ha="center", fontsize=9)
    axs[0, 0].set_ylabel("Interior probability density")
    axs[1, 0].set_ylabel("Atom probability")
    fig.suptitle(r"One law contains an interior density and front atoms ($t/\tau_0=100$)",
                 fontsize=13, fontweight="bold")
    fig.legend(handles=[Patch(facecolor=MUTED, alpha=.55, label="All walks with no velocity turn"),
                        Patch(facecolor="none", edgecolor=INK, hatch="///", label="Subset with no renewal")],
               loc="outside lower center", ncol=2, fontsize=9.5)
    save(fig, "propagators")


def msd():
    d = load("msd.csv")
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.25), layout="constrained")
    for gamma, power, color in zip([.5, 1.5, 2.5], [2, 1.5, 1], COLORS):
        a = d[d["gamma"] == gamma]
        t, m, se = a["time"], a["msd"], a["msd_se"]
        axs[0].loglog(t, m, color=color, lw=2, label=rf"$\gamma={gamma}$")
        axs[0].fill_between(t, np.maximum(m-2*se, 1e-12), m+2*se, color=color, alpha=.18)
        if gamma == .5:
            asymptote = .5 * t**2
        elif gamma == 1.5:
            asymptote = 2*(gamma-1)/((3-gamma)*(2-gamma))*t**(3-gamma)
        else:
            asymptote = 2/(gamma-2)*t
        axs[0].loglog(t[t>=30], asymptote[t>=30], "--", color=color, lw=1.2)
        # Three-interval secant on logarithmic times reduces visual noise.
        k=3
        slope=(np.log(m[k:])-np.log(m[:-k]))/(np.log(t[k:])-np.log(t[:-k]))
        middle=np.sqrt(t[k:]*t[:-k])
        axs[1].semilogx(middle, slope, color=color, lw=1.7)
        axs[1].axhline(power, color=color, lw=.9, ls="--", alpha=.8)
        axs[1].text(1200, power, str(power), color=color, ha="left", va="center")
    axs[0].set(xlabel=r"Time $t/\tau_0$", ylabel=r"MSD $\langle x^2\rangle/(v\tau_0)^2$",
                title="Ensemble MSD and asymptotic guides")
    axs[0].legend(loc="upper left", fontsize=10)
    axs[1].set(xlabel=r"Time $t/\tau_0$", ylabel=r"Local logarithmic slope",
                ylim=(.8,2.1), xlim=(.1,1800), title="Finite-time slopes approach gradually")
    for ax in axs:
        ax.grid(color=GRID, which="major", lw=.6)
    save(fig, "msd-regimes")


def lamperti():
    d = load("lamperti.csv")
    z=(d["left"]+d["right"])/2
    width=d["right"]-d["left"]
    fig, axs=plt.subplots(1, 2, figsize=(10.2,4.2), layout="constrained",
                         gridspec_kw={"width_ratios":[1.6,1]})
    axs[0].stairs(d["empirical_probability"]/width,
                  np.r_[d["left"],d["right"][-1]], fill=True, alpha=.22,
                  color=TEAL, label=r"Simulation, $t/\tau_0=10^4$")
    axs[0].plot(z,d["asymptotic_probability"]/width,"o",ms=3.3,
                color=ORANGE,label="Arcsine law, bin averages")
    axs[0].set(xlabel=r"Scaled position $z=x/(vt)$",ylabel="Probability density",
                title=r"Ballistic scaling at $\gamma=1/2$",xlim=(-1.03,1.03),ylim=(0,None))
    axs[0].legend(loc="upper center",fontsize=9)
    empirical_cdf=np.cumsum(d["empirical_probability"])
    exact_cdf=np.cumsum(d["asymptotic_probability"])
    axs[1].plot(d["right"],empirical_cdf,color=TEAL,lw=2,label="Simulation")
    axs[1].plot(d["right"],exact_cdf,"--",color=ORANGE,lw=1.5,label="Arcsine limit")
    axs[1].set(xlabel=r"$z=x/(vt)$",ylabel="Cumulative probability",
                title="Check the integrated law",xlim=(-1,1),ylim=(0,1))
    for ax in axs:
        ax.grid(axis="y",color=GRID,lw=.6)
    save(fig,"lamperti")


if __name__ == "__main__":
    trajectories()
    schematic()
    propagators()
    msd()
    lamperti()
    print(f"Wrote five PDF/PNG figure pairs to {FIGS}")
