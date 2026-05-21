import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/services")({
  head: () => ({
    meta: [
      { title: "Services — PlaceReady" },
      { name: "description", content: "Placement prediction, resume scoring, mock interviews and personalised roadmaps." },
    ],
  }),
  component: Services,
});

const services = [
  { n: "01", t: "Placement Prediction", d: "Get a probability score and predicted offer tier from our ML model — trained on thousands of real placement outcomes." },
  { n: "02", t: "Resume Score", d: "Line-by-line feedback on what recruiters scan first and what to cut." },
  { n: "03", t: "Skill Gap Analysis", d: "We compare your profile to placed seniors and tell you the exact skills to build." },
  { n: "04", t: "AI Mock Interviews", d: "Live coding and HR mocks with instant rubric-based feedback." },
  { n: "05", t: "Roadmap Coaching", d: "A week-by-week plan, written by mentors who placed in top product companies." },
  { n: "06", t: "Company Targeting", d: "Match your profile to companies most likely to shortlist you." },
];

function Services() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-20">
      <p className="text-sm tracking-widest text-accent uppercase">What we do</p>
      <h1 className="mt-4 text-6xl md:text-8xl max-w-4xl">
        Six tools, one <span className="italic-accent">outcome</span>.
      </h1>
      <p className="mt-6 max-w-xl text-muted-foreground text-lg">
        Each service plugs into your PlaceReady profile and updates your prediction in real time.
      </p>

      <div className="mt-20 grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((s) => (
          <article key={s.n} className="group rounded-3xl bg-card p-8 min-h-[260px] flex flex-col justify-between hover:bg-ink hover:text-ink-foreground transition-colors duration-500">
            <p className="text-accent text-sm tracking-widest">{s.n}</p>
            <div>
              <h3 className="text-3xl mt-6">{s.t}</h3>
              <p className="mt-3 text-muted-foreground group-hover:text-ink-foreground/70 transition-colors">{s.d}</p>
            </div>
          </article>
        ))}
      </div>

      <div className="mt-24 rounded-[2.5rem] bg-sage text-sage-foreground p-12 text-center">
        <h2 className="text-4xl md:text-5xl">Everything you need is bundled in the free tier.</h2>
        <Link to="/predict" className="mt-8 inline-flex rounded-full bg-ink text-ink-foreground px-7 py-4 hover:opacity-90">
          Start free prediction ↗
        </Link>
      </div>
    </div>
  );
}
