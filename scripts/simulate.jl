#!/usr/bin/env julia
#=
Exact event-driven simulations for the Lévy walks learning book.

Uses Julia standard libraries only. Run from any directory:
    julia scripts/simulate.jl
The process starts with a fresh flight at x=0. At each renewal its velocity is
redrawn independently from {-v,+v}, including the previous value.
=#
using Random
using Statistics
using TOML

const BOOK_ROOT = normpath(joinpath(@__DIR__, ".."))

"Lomax flight time: Ψ(t)=(1+t/τ₀)^(-γ). log1p/expm1 avoid cancellation."
lomax(rng::AbstractRNG, γ::Real, τ₀::Real=1.0) =
    τ₀ * expm1(-log1p(-rand(rng)) / γ)

"""
    sample_path!(x, renewals, turns, times, rng, duration; v=1.0)

Sample a piecewise-linear path at increasing observation times, without a time
mesh. `duration(rng)` supplies positive iid flight durations. A renewal redraws
the velocity independently; `turns` counts actual sign changes. The unfinished
last flight is evaluated at the observation time rather than completed early.
Observation times must be sorted, nonnegative, and finite; v must be positive.
"""
function sample_path!(x, renewals, turns, times, rng, duration; v=1.0)
    tstart = 0.0
    xstart = 0.0
    velocity = rand(rng, Bool) ? v : -v
    τ = duration(rng)
    nr = 0
    nt = 0
    for (i, tobs) in pairs(times)
        while tstart + τ <= tobs
            xstart += velocity * τ
            tstart += τ
            nr += 1
            next_velocity = rand(rng, Bool) ? v : -v
            nt += (next_velocity != velocity)
            velocity = next_velocity
            τ = duration(rng)
        end
        x[i] = xstart + velocity * (tobs - tstart)
        renewals[i] = nr
        turns[i] = nt
    end
    return x
end

function write_csv(path, header, rows)
    open(path, "w") do io
        println(io, join(header, ','))
        for row in rows
            println(io, join(row, ','))
        end
    end
end

function generate_data(; outdir=joinpath(BOOK_ROOT, "data"))
    mkpath(outdir)
    # Small path ensemble. Renewals and turns are both saved for auditing.
    trajectory_seed = 20261020
    rng = Xoshiro(trajectory_seed)
    times = collect(range(0.0, 80.0, length=801))
    x = zeros(length(times)); nr = zeros(Int, length(times)); nt = similar(nr)
    trajectory_rows = Tuple{Float64,Int,Float64,Int,Int}[]
    for path in 1:6
        sample_path!(x, nr, nt, times, rng, r -> lomax(r, 1.2))
        append!(trajectory_rows, [(times[i], path, x[i], nr[i], nt[i]) for i in eachindex(times)])
    end
    write_csv(joinpath(outdir, "trajectories.csv"),
        ["time", "path", "position", "renewals", "turns"], trajectory_rows)

    # Every path is sampled at every time: these are correlated-time ensemble
    # estimates, not independent error bars across observation times.
    msd_seed = 20261021
    msd_n = 30_000
    times = 10.0 .^ collect(range(-1.0, 3.0, length=57))
    x = zeros(length(times)); nr = zeros(Int, length(times)); nt = similar(nr)
    msd_rows = Tuple{Float64,Float64,Float64,Float64,Float64,Float64,Int}[]
    for γ in (0.5, 1.5, 2.5)
        rng = Xoshiro(msd_seed + round(Int, 10γ))
        sx = zeros(length(times)); sx2 = similar(sx) .= 0
        sx4 = similar(sx) .= 0; snr0 = zeros(Int, length(times))
        for _ in 1:msd_n
            sample_path!(x, nr, nt, times, rng, r -> lomax(r, γ))
            @. sx += x
            @. sx2 += x^2
            @. sx4 += x^4
            @. snr0 += (nr == 0)
        end
        for i in eachindex(times)
            mean2 = sx2[i] / msd_n
            se2 = sqrt(max(0, (sx4[i] / msd_n - mean2^2) / (msd_n - 1)))
            push!(msd_rows, (γ, times[i], sx[i] / msd_n, mean2, se2,
                snr0[i] / msd_n, msd_n))
        end
    end
    write_csv(joinpath(outdir, "msd.csv"),
        ["gamma", "time", "mean_x", "msd", "msd_se", "no_renewal_mass", "n"], msd_rows)

    # A mixed probability law: an interior histogram plus explicit atoms at
    # x/(vt)=±1. Do not smear front probabilities into density bins.
    propagator_seed = 20261022
    propagator_n = 160_000
    tprop = 100.0
    nbins = 100
    edges = collect(range(-1.0, 1.0, length=nbins+1))
    prop_rows = Tuple{Float64,Float64,Float64,Float64,Float64,Int,Int}[]
    atom_rows = Tuple{Float64,Float64,Int,Int,Int,Int,Int}[]
    x = zeros(1); nr = zeros(Int, 1); nt = similar(nr)
    for γ in (0.5, 1.5, 2.5)
        rng = Xoshiro(propagator_seed + round(Int, 10γ))
        counts = zeros(Int, nbins)
        frontminus = 0; frontplus = 0; freshminus = 0; freshplus = 0
        for _ in 1:propagator_n
            sample_path!(x, nr, nt, [tprop], rng, r -> lomax(r, γ))
            z = x[1] / tprop
            if nt[1] == 0
                frontminus += (z < 0)
                frontplus += (z > 0)
                freshminus += (z < 0 && nr[1] == 0)
                freshplus += (z > 0 && nr[1] == 0)
            else
                bin = clamp(searchsortedlast(edges, z), 1, nbins)
                counts[bin] += 1
            end
        end
        for i in 1:nbins
            width = edges[i+1]-edges[i]
            density = counts[i] / (propagator_n*width)
            se = sqrt(counts[i] / propagator_n * (1-counts[i] / propagator_n) / propagator_n) / width
            push!(prop_rows, (γ, edges[i], edges[i+1], density, se, counts[i], propagator_n))
        end
        push!(atom_rows, (γ, tprop, frontminus, frontplus, freshminus, freshplus, propagator_n))
        @assert sum(counts) + frontminus + frontplus == propagator_n
    end
    write_csv(joinpath(outdir, "propagators.csv"),
        ["gamma", "left", "right", "density_z", "density_se", "count", "n"], prop_rows)
    write_csv(joinpath(outdir, "front_masses.csv"),
        ["gamma", "time", "front_minus", "front_plus", "no_renewal_minus", "no_renewal_plus", "n"], atom_rows)

    # Bin-integrated arcsine comparison. Exact bin masses, rather than values
    # at bin centres, handle the integrable endpoint singularities correctly.
    lamperti_seed = 20261023
    lamperti_n = 140_000
    tlamperti = 10_000.0
    rng = Xoshiro(lamperti_seed)
    nbin = 60
    edges = collect(range(-1.0, 1.0, length=nbin+1))
    counts = zeros(Int, nbin)
    nfront = 0; nnorenewal = 0
    for _ in 1:lamperti_n
        sample_path!(x, nr, nt, [tlamperti], rng, r -> lomax(r, 0.5))
        z = x[1] / tlamperti
        counts[clamp(searchsortedlast(edges, z), 1, nbin)] += 1
        nfront += (nt[1] == 0)
        nnorenewal += (nr[1] == 0)
    end
    lamperti_rows = [(edges[i], edges[i+1], counts[i] / lamperti_n,
        (asin(edges[i+1])-asin(edges[i])) / π, counts[i], lamperti_n) for i in 1:nbin]
    write_csv(joinpath(outdir, "lamperti.csv"),
        ["left", "right", "empirical_probability", "asymptotic_probability", "count", "n"], lamperti_rows)

    meta = Dict(
        "julia_version" => string(VERSION),
        "generator" => "scripts/simulate.jl",
        "velocity_rule" => "iid symmetric redraw at every renewal; repeat signs allowed",
        "initialization" => "fresh flight at time zero, x=0, initial velocity symmetric",
        "duration_survival" => "(1+t/tau0)^(-gamma)",
        "speed" => 1.0, "tau0" => 1.0,
        "trajectories" => Dict("seed"=>trajectory_seed, "gamma"=>1.2, "n"=>6, "time"=>80.0),
        "msd" => Dict("base_seed"=>msd_seed, "seed_rule"=>"base_seed + round(Int,10gamma)", "n_per_gamma"=>msd_n, "gammas"=>[0.5,1.5,2.5], "max_time"=>1000.0),
        "propagators"=>Dict("base_seed"=>propagator_seed,"seed_rule"=>"base_seed + round(Int,10gamma)","n_per_gamma"=>propagator_n,"time"=>tprop,"bins"=>nbins),
        "lamperti"=>Dict("seed"=>lamperti_seed,"gamma"=>0.5,"n"=>lamperti_n,"time"=>tlamperti,"bins"=>nbin,"front_mass"=>nfront/lamperti_n,"no_renewal_mass"=>nnorenewal/lamperti_n),
        "error_bars"=>"Standard errors across independent paths; observation times on each path are correlated.")
    open(joinpath(outdir,"metadata.toml"), "w") do io
        TOML.print(io, meta; sorted=true)
    end
    println("Wrote data to ", outdir)
    return meta
end

if abspath(PROGRAM_FILE) == @__FILE__
    generate_data()
end
