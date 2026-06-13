import { Link } from "@tanstack/react-router";
import logo from "@/assets/logo.png";
import { Mail, Phone, MapPin, Github, Linkedin, ExternalLink } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    {
      name: "GitHub",
      icon: Github,
      url: "https://github.com/sumitdangi45",
      label: "GitHub Profile"
    },
    {
      name: "LinkedIn",
      icon: Linkedin,
      url: "https://www.linkedin.com/in/sumit-dangi-780aa5333/",
      label: "LinkedIn Profile"
    },
    {
      name: "Portfolio",
      icon: ExternalLink,
      url: "https://sumitdangiportfolio.netlify.app/",
      label: "Portfolio Website"
    }
  ];

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
            {/* Social Links */}
            <div className="flex gap-4 mt-6">
              {socialLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <a
                    key={link.name}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={link.label}
                    className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-ink-foreground/10 hover:bg-accent/20 transition-colors"
                  >
                    <Icon className="w-5 h-5 text-accent hover:text-accent" />
                  </a>
                );
              })}
            </div>
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
            <h4 className="text-sm uppercase tracking-widest text-ink-foreground/50 mb-4">Get in Touch</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-3 text-ink-foreground/80 hover:text-accent transition-colors">
                <Mail className="w-4 h-4 flex-shrink-0" />
                <a href="mailto:sumitdangi84552@gmail.com">sumitdangi84552@gmail.com</a>
              </li>
              <li className="flex items-center gap-3 text-ink-foreground/80 hover:text-accent transition-colors">
                <Phone className="w-4 h-4 flex-shrink-0" />
                <a href="tel:+917974135629">+91 79741 35629</a>
              </li>
              <li className="flex items-center gap-3 text-ink-foreground/80">
                <MapPin className="w-4 h-4 flex-shrink-0" />
                <span>Bengaluru, India</span>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-16 pt-8 border-t border-ink-foreground/10 flex flex-col md:flex-row justify-between gap-4 text-sm text-ink-foreground/50">
          <p>© {currentYear} PlaceReady. All rights reserved.</p>
          <p className="font-display text-lg italic-accent">Predict. Prepare. Place.</p>
        </div>
      </div>
    </footer>
  );
}
