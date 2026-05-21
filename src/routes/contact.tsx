import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact — PlaceReady" },
      { name: "description", content: "Talk to the PlaceReady team about partnerships, college plans or general questions." },
    ],
  }),
  component: Contact,
});

function Contact() {
  const [sent, setSent] = useState(false);
  return (
    <div className="mx-auto max-w-7xl px-6 py-20">
      <p className="text-sm tracking-widest text-accent uppercase">Contact</p>
      <h1 className="mt-4 text-6xl md:text-8xl max-w-3xl">
        Let's <span className="italic-accent">talk</span>.
      </h1>

      <div className="mt-16 grid lg:grid-cols-[1fr_1.2fr] gap-10">
        <div className="space-y-8">
          <div>
            <p className="text-sm uppercase tracking-widest text-muted-foreground">Email</p>
            <p className="text-2xl font-display mt-2">hello@placeready.app</p>
          </div>
          <div>
            <p className="text-sm uppercase tracking-widest text-muted-foreground">Phone</p>
            <p className="text-2xl font-display mt-2">+91 98765 43210</p>
          </div>
          <div>
            <p className="text-sm uppercase tracking-widest text-muted-foreground">Office</p>
            <p className="text-2xl font-display mt-2">HSR Layout, Bengaluru<br />Karnataka, India</p>
          </div>
          <div className="rounded-3xl bg-sage text-sage-foreground p-6">
            <p className="font-display text-xl">College partnerships</p>
            <p className="text-sm mt-2 opacity-80">Bulk plans for placement cells available. Reply within 24 hours.</p>
          </div>
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); setSent(true); }}
          className="rounded-[2rem] bg-card p-8 md:p-10 space-y-5"
        >
          {sent ? (
            <div className="text-center py-20 animate-fade-up">
              <p className="text-6xl">✦</p>
              <h2 className="text-3xl font-display mt-4">Message sent</h2>
              <p className="text-muted-foreground mt-2">We'll get back to you within 24 hours.</p>
            </div>
          ) : (
            <>
              <Input label="Your name" />
              <Input label="Email" type="email" />
              <Input label="College / Company" />
              <label className="block">
                <span className="text-sm text-muted-foreground">Message</span>
                <textarea rows={5} required className="mt-2 w-full rounded-xl bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-ring" />
              </label>
              <button className="w-full rounded-full bg-primary text-primary-foreground px-7 py-4 font-medium hover:bg-primary/90">
                Send message ↗
              </button>
            </>
          )}
        </form>
      </div>
    </div>
  );
}

function Input({ label, type = "text" }: { label: string; type?: string }) {
  return (
    <label className="block">
      <span className="text-sm text-muted-foreground">{label}</span>
      <input type={type} required className="mt-2 w-full rounded-xl bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-ring" />
    </label>
  );
}
