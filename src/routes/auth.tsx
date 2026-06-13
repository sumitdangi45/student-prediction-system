import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { z } from "zod";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";

export const Route = createFileRoute("/auth")({
  head: () => ({
    meta: [
      { title: "Login or Sign Up — PlaceReady" },
      { name: "description", content: "Login or create your PlaceReady account to get personalised placement predictions." },
    ],
  }),
  validateSearch: (s: Record<string, unknown>) => ({
    mode: (s.mode === "signup" ? "signup" : "login") as "login" | "signup",
  }),
  component: AuthPage,
});

const emailSchema = z.object({
  email: z.string().trim().email("Enter a valid email").max(255),
});

const otpSchema = z.object({
  otp: z.string().length(6, "OTP must be 6 digits"),
});

function AuthPage() {
  const { mode } = Route.useSearch();
  const navigate = useNavigate();
  const { isAuthenticated, loading: authLoading, refreshAuth } = useAuth();
  const [tab, setTab] = useState<"login" | "signup">(mode);
  const [step, setStep] = useState<"email" | "otp">("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      navigate({ to: "/dashboard" });
    }
  }, [isAuthenticated, authLoading, navigate]);

  const switchTab = (t: "login" | "signup") => {
    setTab(t);
    setStep("email");
    setEmail("");
    setOtp("");
    navigate({ to: "/auth", search: { mode: t }, replace: true });
  };

  async function handleSendOtp(e: React.FormEvent) {
    e.preventDefault();
    const parsed = emailSchema.safeParse({ email });
    if (!parsed.success) {
      toast.error(parsed.error.issues[0].message);
      return;
    }
    setLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/api/auth/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: parsed.data.email }),
      });
      const data = await response.json();
      if (data.status === "success") {
        toast.success("OTP sent to your email!");
        setStep("otp");
      } else {
        toast.error(data.message || "Failed to send OTP");
      }
    } catch (err) {
      toast.error("Failed to send OTP");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOtp(e: React.FormEvent) {
    e.preventDefault();
    const parsedOtp = otpSchema.safeParse({ otp });
    if (!parsedOtp.success) {
      toast.error(parsedOtp.error.issues[0].message);
      return;
    }

    setLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/api/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp: parsedOtp.data.otp }),
      });
      const data = await response.json();
      if (data.status === "success") {
        // Clear old data first
        sessionStorage.clear();
        localStorage.clear();
        
        // Store NEW token in both sessionStorage AND localStorage
        sessionStorage.setItem("token", data.token);
        localStorage.setItem("token", data.token);
        
        const userData = data.user || {
          id: data.user_id,
          email: data.email,
          is_admin: data.is_admin,
          is_new_user: data.is_new_user
        };
        sessionStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("user", JSON.stringify(userData));
        
        console.log("✅ Auth: Token stored - User logged in:", userData.email, "is_new_user:", userData.is_new_user);
        toast.success(data.message);
        
        // Refresh auth context with new token/user
        await refreshAuth();
        
        // Redirect after small delay to ensure state is updated
        setTimeout(() => {
          // NEW users go to HOME, RETURNING users go to DASHBOARD
          const redirectPath = userData.is_new_user ? "/" : "/dashboard";
          navigate({ to: redirectPath });
        }, 100);
      } else {
        toast.error(data.message || "Invalid OTP");
      }
    } catch (err) {
      toast.error("Failed to verify OTP");
    } finally {
      setLoading(false);
    }
  }

  // Show loading while checking auth state
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-16">
      <div className="grid lg:grid-cols-2 gap-8 items-stretch">
        {/* Left visual */}
        <div className="relative overflow-hidden rounded-[2.5rem] bg-secondary p-12 hidden lg:flex flex-col justify-between min-h-[600px]">
          <div className="absolute -right-32 -top-32 w-[480px] h-[480px] rounded-full bg-background/60 animate-blob" />
          <div className="absolute right-20 -bottom-20 w-72 h-72 rounded-full bg-background/40 animate-blob" style={{ animationDelay: "2s" }} />
          <div className="relative">
            <p className="text-sm tracking-widest text-accent uppercase">PlaceReady</p>
            <h1 className="mt-6 text-6xl leading-none">
              Your next <br />
              <span className="italic-accent">offer letter</span> <br />
              starts with login.
            </h1>
          </div>
          <p className="relative text-muted-foreground max-w-sm">
            Join 12,000+ students using PlaceReady to predict and prepare for their placement season.
          </p>
        </div>

        {/* Right form */}
        <div className="rounded-[2.5rem] bg-card p-8 md:p-12 min-h-[600px] flex flex-col">
          <div className="flex gap-2 p-1 bg-secondary rounded-full self-start">
            {(["login", "signup"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => switchTab(t)}
                className={`px-5 py-2 rounded-full text-sm font-medium transition-colors ${
                  tab === t ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t === "login" ? "Login" : "Sign Up"}
              </button>
            ))}
          </div>

          <h2 className="mt-8 text-4xl md:text-5xl">
            {tab === "login" ? <>Welcome <span className="italic-accent">back</span>.</> : <>Create your <span className="italic-accent">account</span>.</>}
          </h2>
          <p className="mt-3 text-muted-foreground">
            {tab === "login" ? "Login to access your predictions and roadmap." : "Sign up free. No card. No college email required."}
          </p>

          {step === "email" ? (
            <form onSubmit={handleSendOtp} className="mt-8 space-y-5 flex-1 flex flex-col">
              <label className="block">
                <span className="text-sm text-muted-foreground">Email</span>
                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@college.edu"
                  className="mt-2 w-full rounded-xl bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </label>

              <button
                type="submit"
                disabled={loading}
                className="mt-4 w-full rounded-full bg-primary text-primary-foreground px-7 py-4 font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
              >
                {loading ? "Sending OTP…" : "Send OTP ↗"}
              </button>

              <p className="text-center text-sm text-muted-foreground mt-auto pt-6">
                {tab === "login" ? (
                  <>New here? <button type="button" onClick={() => switchTab("signup")} className="text-accent hover:underline">Create an account</button></>
                ) : (
                  <>Already have an account? <button type="button" onClick={() => switchTab("login")} className="text-accent hover:underline">Login</button></>
                )}
              </p>
              <p className="text-center text-xs text-muted-foreground">
                By continuing you agree to our Terms. <Link to="/" className="hover:underline">Back home</Link>
              </p>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} className="mt-8 space-y-5 flex-1 flex flex-col">
              <div>
                <p className="text-sm text-muted-foreground mb-4">
                  We sent a 6-digit OTP to <span className="font-semibold text-foreground">{email}</span>
                </p>
                <button
                  type="button"
                  onClick={() => setStep("email")}
                  className="text-sm text-accent hover:underline"
                >
                  Change email
                </button>
              </div>

              <label className="block">
                <span className="text-sm text-muted-foreground">Enter OTP</span>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  placeholder="000000"
                  className="mt-2 w-full rounded-xl bg-background border border-border px-4 py-3 text-center text-2xl tracking-widest focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </label>

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="mt-4 w-full rounded-full bg-primary text-primary-foreground px-7 py-4 font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
              >
                {loading ? "Verifying…" : "Verify OTP ↗"}
              </button>

              <p className="text-center text-xs text-muted-foreground mt-auto pt-6">
                Didn't receive OTP? <button type="button" onClick={() => { setStep("email"); setOtp(""); }} className="text-accent hover:underline">Resend</button>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
