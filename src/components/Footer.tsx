import { Link } from "@tanstack/react-router";
import logo from "@/assets/logo.png";

export function Footer() {
  return (
    <footer className="mt-32 bg-ink text-ink-foreground rounded-t-[3rem]">
      <div className="mx-auto max-w-7xl px-6 py-20">
        <div className="grid gap-12 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <img src={logo} alt="" width={40} height={40} />
              <span className="text-3xl font-display">PlaceReady</span>
            </div>
            <p className="text-ink-foreground/70 max-w-sm leading-relaxed">
              AI-powered placement prediction built for students who refuse to leave their career to chance.
            </p>
          </div>
          <div>
            <h4 className="text-sm uppercase tracking-widest text-ink-foreground/50 mb-4">Explore</h4>
            <ul className="space-y-3">
              <li><Link to="/about" className="hover:text-accent transition-colors">About</Link></li>
              <li><Link to="/services" className="hover:text-accent transition-colors">Services</Link></li>
              <li><Link to="/predict" className="hover:text-accent transition-colors">Predict</Link></li>
              <li><Link to="/contact" className="hover:text-accent transition-colors">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm uppercase tracking-widest text-ink-foreground/50 mb-4">Contact</h4>
            <ul className="space-y-3 text-ink-foreground/80">
              <li>hello@placeready.app</li>
              <li>+91 98765 43210</li>
              <li>Bengaluru, India</li>
            </ul>
          </div>
        </div>
        <div className="mt-16 pt-8 border-t border-ink-foreground/10 flex flex-col md:flex-row justify-between gap-4 text-sm text-ink-foreground/50">
          <p>© {new Date().getFullYear()} PlaceReady. All rights reserved.</p>
          <p className="font-display text-lg italic-accent">Predict. Prepare. Place.</p>
        </div>
      </div>
    </footer>
  );
}
