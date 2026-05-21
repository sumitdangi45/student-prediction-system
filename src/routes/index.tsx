import { createFileRoute, Link } from "@tanstack/react-router";
import hero from "@/assets/hero-student.jpg";
import group from "@/assets/students-group.jpg";
import s1 from "@/assets/student-1.jpg";
import s2 from "@/assets/student-2.jpg";
import interview from "@/assets/interview.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PlaceReady — Predict Your Placement with AI" },
      { name: "description", content: "AI placement prediction for students. Know your chances, fix your gaps, land the offer." },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="overflow-hidden">
      <Hero />
      <Marquee />
      <Wellbeing />
      <Steps />
      <Stats />
      <Testimonials />
      <CTA />
    </div>
  );
}

function Hero() {
  return (
    <section className="mx-auto max-w-7xl px-6 pt-8 pb-20">
      <div className="grid lg:grid-cols-[1.6fr_1fr] gap-6">
        {/* Main hero card */}
        <div className="relative overflow-hidden rounded-[2.5rem] bg-secondary p-10 lg:p-14 min-h-[560px]">
          <div className="absolute -right-32 -top-32 w-[480px] h-[480px] rounded-full bg-background/60 animate-blob" />
          <div className="absolute right-40 bottom-10 w-72 h-72 rounded-full bg-background/40 animate-blob" style={{ animationDelay: "2s" }} />
          <div className="relative grid lg:grid-cols-2 gap-6 items-end h-full">
            <div className="animate-fade-up">
              <h1 className="text-5xl md:text-6xl lg:text-7xl">
                Your Future <br />
                <span className="italic-accent">Placement</span> <br />
                Starts Here
              </h1>
              <p className="mt-6 text-muted-foreground max-w-md leading-relaxed">
                PlaceReady uses machine learning on thousands of student profiles to predict your placement chances — and show you exactly how to improve them.
              </p>
              <Link
                to="/predict"
                className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-7 py-4 font-medium hover:gap-4 transition-all"
              >
                Predict My Chances <span aria-hidden>↗</span>
              </Link>

              <div className="mt-10 flex flex-wrap gap-2">
                {["Skill Analysis", "CGPA Insights", "Mock Interviews", "Resume Score"].map((t) => (
                  <span key={t} className="inline-flex items-center gap-1.5 rounded-full bg-background px-4 py-2 text-sm">
                    <span className="text-accent">✦</span> {t}
                  </span>
                ))}
              </div>
            </div>
            <div className="relative h-full min-h-[400px]">
              <img
                src={hero}
                alt="Confident student with laptop"
                width={1024} height={1024}
                className="absolute inset-0 w-full h-full object-cover object-bottom rounded-2xl animate-float"
              />
            </div>
          </div>
        </div>

        {/* Right column */}
        <div className="flex flex-col gap-6">
          <div className="rounded-[2.5rem] bg-sage text-sage-foreground p-8 animate-fade-up delay-100">
            <div className="flex items-center justify-between mb-3">
              <div className="flex -space-x-2">
                {[s1, s2, group].map((src, i) => (
                  <img key={i} src={src} alt="" width={40} height={40} className="w-10 h-10 rounded-full border-2 border-sage object-cover" loading="lazy" />
                ))}
              </div>
              <span className="text-lg">★★★★★</span>
            </div>
            <p className="text-2xl font-display">4.9/5 — Student Rating</p>
            <p className="text-sm mt-2 opacity-80">
              Over 12,000 students trust PlaceReady to plan their placement season.
            </p>
          </div>
          <div className="rounded-[2.5rem] overflow-hidden h-56 animate-fade-up delay-200">
            <img src={interview} alt="Job interview" width={1024} height={768} className="w-full h-full object-cover hover:scale-105 transition-transform duration-700" loading="lazy" />
          </div>
          <div className="rounded-[2.5rem] bg-ink text-ink-foreground p-8 animate-fade-up delay-300">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-4xl font-display">94%</p>
                <p className="text-sm opacity-70 mt-2">Prediction accuracy on benchmark dataset.</p>
              </div>
              <div>
                <p className="text-4xl font-display">12k+</p>
                <p className="text-sm opacity-70 mt-2">Students placed using our insights.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Marquee() {
  const items = ["Google", "Microsoft", "Amazon", "Flipkart", "TCS", "Infosys", "Adobe", "Goldman Sachs", "Deloitte", "Wipro"];
  return (
    <section className="border-y border-border py-8 overflow-hidden bg-card">
      <div className="flex gap-16 animate-marquee whitespace-nowrap">
        {[...items, ...items].map((c, i) => (
          <span key={i} className="text-2xl font-display text-muted-foreground">{c}</span>
        ))}
      </div>
    </section>
  );
}

function Wellbeing() {
  const features = [
    { title: "Profile Score", desc: "A holistic score across academics, projects and skills.", img: s1 },
    { title: "Smart Prediction", desc: "ML model trained on real placement outcomes.", img: group },
    { title: "Gap Roadmap", desc: "Exact skills to learn to lift your placement odds.", img: s2 },
    { title: "Mock Interviews", desc: "AI-led mock rounds with instant feedback.", img: interview },
  ];
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <div className="flex flex-wrap items-end justify-between gap-6 mb-16">
        <h2 className="text-5xl md:text-6xl max-w-2xl">
          Your Career <span className="italic-accent">Compass</span>
        </h2>
        <p className="text-muted-foreground max-w-md">
          We provide private, data-driven sessions to help every student understand exactly where they stand.
        </p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((f, i) => (
          <div key={f.title} className="group rounded-3xl bg-card overflow-hidden hover:-translate-y-2 transition-transform duration-500" style={{ transitionDelay: `${i * 40}ms` }}>
            <div className="aspect-[4/5] overflow-hidden">
              <img src={f.img} alt="" width={768} height={960} loading="lazy" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
            </div>
            <div className="p-6">
              <h3 className="text-2xl">{f.title}</h3>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{f.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Steps() {
  const steps = [
    { n: "01", t: "Build your profile", d: "Add CGPA, skills, projects, internships in 2 minutes." },
    { n: "02", t: "Get your prediction", d: "Our model returns your placement probability and tier." },
    { n: "03", t: "Follow the roadmap", d: "Personal action plan: courses, projects, mocks." },
    { n: "04", t: "Land the offer", d: "Track applications and walk into interviews prepared." },
  ];
  return (
    <section className="bg-ink text-ink-foreground rounded-[3rem] mx-6 lg:mx-12 py-24 px-6 lg:px-16">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-5xl md:text-6xl max-w-3xl">
          From confusion to <span className="italic-accent">offer letter</span> — in four moves.
        </h2>
        <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((s) => (
            <div key={s.n} className="border-t border-ink-foreground/20 pt-6">
              <p className="text-accent text-sm tracking-widest">{s.n}</p>
              <h3 className="text-3xl mt-4">{s.t}</h3>
              <p className="text-ink-foreground/70 mt-3 text-sm leading-relaxed">{s.d}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Stats() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24 grid lg:grid-cols-2 gap-10 items-center">
      <div>
        <h2 className="text-5xl md:text-6xl">
          Numbers that <span className="italic-accent">speak</span> for our students.
        </h2>
        <p className="mt-6 text-muted-foreground max-w-md leading-relaxed">
          Built by IIT alumni and trained on placement data across 300+ Indian colleges.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {[
          { n: "12,000+", l: "Students predicted" },
          { n: "₹42 LPA", l: "Highest offer tracked" },
          { n: "300+", l: "Partner colleges" },
          { n: "94%", l: "Model accuracy" },
        ].map((s) => (
          <div key={s.l} className="rounded-3xl bg-card p-8">
            <p className="text-4xl md:text-5xl font-display">{s.n}</p>
            <p className="text-sm text-muted-foreground mt-3">{s.l}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Testimonials() {
  const ts = [
    { q: "PlaceReady told me my Tier-1 chance was 38%. Three months of their roadmap later — I cracked Microsoft.", n: "Ananya R.", r: "NIT Trichy, '24" },
    { q: "Honest, data-backed feedback I never got from college. The gap analysis was scary accurate.", n: "Rohan S.", r: "VIT, '25" },
    { q: "Mock interviews on PlaceReady felt harder than the real Amazon round. That's exactly why I cleared it.", n: "Priya M.", r: "BITS Pilani, '24" },
  ];
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <h2 className="text-5xl md:text-6xl mb-16 max-w-3xl">
        Loved by students, <span className="italic-accent">trusted</span> by colleges.
      </h2>
      <div className="grid md:grid-cols-3 gap-6">
        {ts.map((t, i) => (
          <figure key={i} className="rounded-3xl bg-card p-8 flex flex-col justify-between min-h-[320px]">
            <blockquote className="text-xl font-display leading-snug">"{t.q}"</blockquote>
            <figcaption className="mt-6">
              <p className="font-medium">{t.n}</p>
              <p className="text-sm text-muted-foreground">{t.r}</p>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="mx-6 lg:mx-12 my-24">
      <div className="relative overflow-hidden rounded-[3rem] bg-secondary p-12 md:p-20 text-center">
        <div className="absolute -left-20 -top-20 w-80 h-80 rounded-full bg-accent/20 animate-blob" />
        <div className="absolute -right-20 -bottom-20 w-96 h-96 rounded-full bg-primary/15 animate-blob" style={{ animationDelay: "3s" }} />
        <div className="relative">
          <h2 className="text-5xl md:text-7xl">
            Stop guessing. <br />
            <span className="italic-accent">Start predicting.</span>
          </h2>
          <p className="mt-6 text-muted-foreground max-w-xl mx-auto">
            Your first prediction is free. No credit card. No college email needed.
          </p>
          <Link to="/predict" className="mt-10 inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-8 py-4 font-medium hover:gap-4 transition-all">
            Predict My Placement <span aria-hidden>↗</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
