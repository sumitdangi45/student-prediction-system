import { createFileRoute } from "@tanstack/react-router";
import group from "@/assets/students-group.jpg";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — PlaceReady" },
      { name: "description", content: "Why PlaceReady exists, who built it, and how we help students decode the placement process." },
    ],
  }),
  component: About,
});

function About() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-20">
      <p className="text-sm tracking-widest text-accent uppercase">About</p>
      <h1 className="mt-4 text-6xl md:text-8xl max-w-4xl">
        Built for the student who <span className="italic-accent">refuses</span> to guess.
      </h1>

      <div className="mt-16 grid lg:grid-cols-2 gap-10 items-start">
        <img src={group} alt="Students collaborating" width={1024} height={1024} loading="lazy" className="rounded-[2rem] w-full h-[460px] object-cover" />
        <div className="space-y-6 text-lg text-muted-foreground leading-relaxed">
          <p>
            PlaceReady started in a hostel room in 2023, when three friends realised every senior gave them different placement advice — and none of it was data.
          </p>
          <p>
            Today we are a small team of engineers, ex-recruiters and data scientists building the most honest placement prediction engine in India.
          </p>
          <p>
            We don't sell dreams. We give you the numbers, the gaps, and the roadmap. The work is still yours.
          </p>
        </div>
      </div>

      <div className="mt-24 grid md:grid-cols-3 gap-6">
        {[
          { t: "Honest", d: "We will tell you a 12% chance is 12%. Then we'll show you how to make it 60%." },
          { t: "Data-first", d: "Every prediction is backed by anonymised outcomes from real students." },
          { t: "Student-built", d: "Designed by people who sat in those interview chairs last year." },
        ].map((v) => (
          <div key={v.t} className="rounded-3xl bg-card p-8">
            <h3 className="text-3xl">{v.t}</h3>
            <p className="mt-3 text-muted-foreground">{v.d}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
