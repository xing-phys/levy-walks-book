#!/usr/bin/env julia
using Test
using Random
using Statistics
include(joinpath(@__DIR__, "simulate.jl"))

@testset "event-driven Lévy walk invariants and independent benchmarks" begin
    times = [0.0, 0.2, 1.0, 3.0, 20.0]
    x = zeros(length(times)); nr = zeros(Int, length(times)); nt = similar(nr)
    # A first flight longer than the experiment must be clipped exactly.
    sample_path!(x, nr, nt, times, Xoshiro(2), r -> Inf; v=2.0)
    @test abs.(x) == 2times
    @test all(iszero, nr)
    @test all(iszero, nt)

    # Every piecewise-linear path stays in its finite-speed cone.
    for γ in (0.5, 1.5, 2.5), seed in 1:100
        sample_path!(x, nr, nt, times, Xoshiro(seed), r -> lomax(r, γ); v=1.7)
        @test all(abs.(x) .<= 1.7times .+ 1e-12)
        @test all(diff(nr) .>= 0)
        @test all(diff(nt) .>= 0)
        @test all(nt .<= nr)
    end

    # Reusing a seed reproduces the positions and hidden renewal counts.
    x2=similar(x); nr2=similar(nr); nt2=similar(nt)
    sample_path!(x,nr,nt,times,Xoshiro(104),r -> lomax(r,1.5))
    sample_path!(x2,nr2,nt2,times,Xoshiro(104),r -> lomax(r,1.5))
    @test x == x2 && nr == nr2 && nt == nt2

    # Inverse-transform durations are tested against an analytic survival law.
    n = 200_000
    rng = Xoshiro(105)
    durations = [lomax(rng,1.5,2.0) for _ in 1:n]
    @test all(durations .>= 0)
    for t in (0.5,2.0,10.0)
        p = (1+t/2)^(-1.5)
        observed = count(>(t),durations) / n
        @test abs(observed-p) < 6sqrt(p*(1-p)/n)
    end

    # Exponential renewals with independent velocity redraw have covariance
    # v² exp[-λ|t-s|], so MSD=2v²[t/λ-(1-exp(-λt))/λ²]. The rate of
    # actual sign flips is λ/2; confusing redraw with forced flip fails here.
    ts = [0.1,1.0,4.0]
    xs=zeros(3); rs=zeros(Int,3); turns=zeros(Int,3)
    sx2=zeros(3); sx4=zeros(3); sx=zeros(3)
    λ=1.3; v=0.8; n=80_000
    rng=Xoshiro(106)
    for _ in 1:n
        sample_path!(xs,rs,turns,ts,rng,r -> randexp(r)/λ; v=v)
        @. sx += xs
        @. sx2 += xs^2
        @. sx4 += xs^4
    end
    for i in eachindex(ts)
        m2=sx2[i]/n
        se=sqrt(max(0,(sx4[i]/n-m2^2)/(n-1)))
        exact=2v^2*(ts[i]/λ+expm1(-λ*ts[i])/λ^2)
        @test abs(m2-exact) < 6se
        @test abs(sx[i]/n) < 6sqrt(m2/n)
    end
end
