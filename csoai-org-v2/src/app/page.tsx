"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

function EmailCapture({ source }: { source: string }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("loading");
    const res = await fetch("/api/subscribe", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, source }) });
    if (res.ok) setStatus("success");
    else setStatus("error");
  };
  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 w-full max-w-md">
      <Input type="email" placeholder="Enter your email" value={email} onChange={(e) => setEmail(e.target.value)} className="bg-white/10 border-white/20 text-white placeholder:text-white/50" required />
      <Button type="submit" disabled={status === "loading"} className="bg-emerald-500 hover:bg-emerald-600 text-white">
        {status === "loading" ? "..." : "Get Early Access"}
      </Button>
      {status === "success" && <p className="text-emerald-400 text-sm">You are on the list. We will be in touch.</p>}
      {status === "error" && <p className="text-red-400 text-sm">Something went wrong. Please try again.</p>}
    </form>
  );
}

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">CSOAI</span>
            </div>
            <div className="hidden md:flex space-x-8">
              <a href="#pricing" className="text-sm text-slate-300 hover:text-white transition">Pricing</a>
              <a href="#frameworks" className="text-sm text-slate-300 hover:text-white transition">Frameworks</a>
              <a href="https://github.com/CSOAI-ORG" className="text-sm text-slate-300 hover:text-white transition">GitHub</a>
            </div>
            <div className="md:hidden">
              <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-white">
                {mobileMenuOpen ? "✕" : "☰"}
              </button>
            </div>
          </div>
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 space-y-2">
              <a href="#pricing" className="block text-slate-300 hover:text-white">Pricing</a>
              <a href="#frameworks" className="block text-slate-300 hover:text-white">Frameworks</a>
              <a href="https://github.com/CSOAI-ORG" className="block text-slate-300 hover:text-white">GitHub</a>
            </div>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-20 pb-32">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-slate-950 to-slate-950" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Badge className="mb-6 bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
            EU AI Act Article 50 — 91 Days Until Enforcement
          </Badge>
          <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-6">
            Hire a Compliance Agent for{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Less Than an Intern
            </span>
          </h1>
          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            AI compliance doesn't need a £360K/year governance team. Our MCP-powered agents handle risk classification, 
            audit generation, and regulatory tracking — 24/7, at 1/10th the cost of a human compliance officer.
          </p>
          <EmailCapture source="hero" />
          <p className="text-xs text-slate-500 mt-4">Join 50+ organisations preparing for August 2026</p>
        </div>
      </section>

      {/* Social Proof / Stats */}
      <section className="border-y border-white/5 bg-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-emerald-400">234+</div>
              <div className="text-sm text-slate-400 mt-1">MCP Servers</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-emerald-400">£40K</div>
              <div className="text-sm text-slate-400 mt-1">Avg. Savings</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-emerald-400">14hrs</div>
              <div className="text-sm text-slate-400 mt-1">vs 4-5 Weeks</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-emerald-400">MIT</div>
              <div className="text-sm text-slate-400 mt-1">Open Source</div>
            </div>
          </div>
        </div>
      </section>

      {/* Frameworks */}
      <section id="frameworks" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-4">One Agent. Every Framework.</h2>
          <p className="text-slate-400 text-center max-w-2xl mx-auto mb-12">
            Our compliance agents map to all major regulatory frameworks. No more siloed tools or manual cross-referencing.
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { title: "EU AI Act", desc: "Article 6 risk classification, FRIA generation, Article 50 transparency", badge: "91 days" },
              { title: "NIST AI RMF", desc: "All 19 functions mapped to automated MCP tools", badge: "US/UK" },
              { title: "DORA", desc: "Article 26 TLPT planning, ICT risk management", badge: "Financial" },
              { title: "ISO 42001", desc: "AI management system conformity assessment", badge: "Global" },
              { title: "CMMC / NIST 800-171", desc: "Defense contractor compliance automation", badge: "Defense" },
              { title: "UK AI Bill", desc: "Emerging UK framework alignment", badge: "Coming" },
            ].map((f) => (
              <Card key={f.title} className="bg-white/5 border-white/10 hover:border-emerald-500/30 transition">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{f.title}</CardTitle>
                    <Badge variant="outline" className="text-xs">{f.badge}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-400">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing — Agent-as-Employee Model */}
      <section id="pricing" className="py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-4">Agent-as-Employee Pricing</h2>
          <p className="text-slate-400 text-center max-w-2xl mx-auto mb-12">
            A junior compliance officer costs £3,000/month. Our agents cost £499/month and work 24/7 
            without sick days, holidays, or LinkedIn scrolling.
          </p>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="bg-white/5 border-white/10">
              <CardHeader>
                <CardTitle className="text-lg text-slate-300">Starter Agent</CardTitle>
                <div className="text-3xl font-bold text-white">£499<span className="text-sm font-normal text-slate-400">/mo</span></div>
                <p className="text-xs text-slate-500">vs £3,000/mo junior compliance officer</p>
              </CardHeader>
              <CardContent className="space-y-3">
                {["EU AI Act Article 6 classification", "Basic FRIA generation", "1 framework", "Email support", "100 compliance checks/mo"].map((item) => (
                  <div key={item} className="flex items-center text-sm text-slate-300">
                    <span className="text-emerald-400 mr-2">✓</span>{item}
                  </div>
                ))}
                <Button className="w-full mt-4 bg-white/10 hover:bg-white/20 text-white">Start Free Trial</Button>
              </CardContent>
            </Card>
            <Card className="bg-white/5 border-emerald-500/30 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <Badge className="bg-emerald-500 text-white">Most Popular</Badge>
              </div>
              <CardHeader>
                <CardTitle className="text-lg text-emerald-400">Professional Agent</CardTitle>
                <div className="text-3xl font-bold text-white">£1,999<span className="text-sm font-normal text-slate-400">/mo</span></div>
                <p className="text-xs text-slate-500">vs £6,500/mo senior compliance officer</p>
              </CardHeader>
              <CardContent className="space-y-3">
                {["Everything in Starter", "Multi-framework coverage (EU + NIST + DORA)", "HMAC-signed attestations", "Priority support", "Unlimited compliance checks", "SME self-assessment portal"].map((item) => (
                  <div key={item} className="flex items-center text-sm text-slate-300">
                    <span className="text-emerald-400 mr-2">✓</span>{item}
                  </div>
                ))}
                <Button className="w-full mt-4 bg-emerald-500 hover:bg-emerald-600 text-white">Start Free Trial</Button>
              </CardContent>
            </Card>
            <Card className="bg-white/5 border-white/10">
              <CardHeader>
                <CardTitle className="text-lg text-slate-300">Enterprise Agent Fleet</CardTitle>
                <div className="text-3xl font-bold text-white">Custom</div>
                <p className="text-xs text-slate-500">Replace an entire compliance team</p>
              </CardHeader>
              <CardContent className="space-y-3">
                {["Everything in Professional", "Custom framework development", "BSI/UKAS certification prep", "Dedicated account manager", "On-premise deployment option", "SLA with 99.9% uptime"].map((item) => (
                  <div key={item} className="flex items-center text-sm text-slate-300">
                    <span className="text-emerald-400 mr-2">✓</span>{item}
                  </div>
                ))}
                <Button className="w-full mt-4 bg-white/10 hover:bg-white/20 text-white">Contact Sales</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* ROI Calculator Teaser */}
      <section className="py-16 border-t border-white/5 bg-gradient-to-r from-emerald-900/10 to-cyan-900/10">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h3 className="text-2xl font-bold mb-4">Calculate Your Compliance Cost</h3>
          <p className="text-slate-400 mb-8">
            A typical 50-person fintech spends £360K/year on AI governance. 
            Our Professional Agent Fleet delivers the same coverage for £24K/year — 
            a 93% reduction with 10x faster turnaround.
          </p>
          <EmailCapture source="roi-teaser" />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-slate-500 text-sm">
              © 2026 CSOAI / MEOK AI Labs. MIT Licensed.
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="https://github.com/CSOAI-ORG" className="text-slate-500 hover:text-white text-sm">GitHub</a>
              <a href="https://meok.ai" className="text-slate-500 hover:text-white text-sm">MEOK AI</a>
              <a href="mailto:nicholas@csoai.org" className="text-slate-500 hover:text-white text-sm">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
