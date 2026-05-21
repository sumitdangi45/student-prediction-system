import { Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import logo from "@/assets/logo.png";
import avatar1 from "@/assets/student-1.jpg";
import avatar2 from "@/assets/student-2.jpg";
import { useAuth } from "@/contexts/AuthContext";
import { User, LogOut, Settings, LayoutDashboard, Shield } from "lucide-react";

const nav = [
  { to: "/", label: "Home" },
  { to: "/about", label: "About" },
  { to: "/services", label: "Services" },
  { to: "/predict", label: "Predict" },
  { to: "/contact", label: "Contact" },
] as const;

export function Header() {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  console.log('🎨 Header: Render state', { loading, isAuthenticated, user: user?.email });

  // Don't render until auth state is loaded
  if (loading) {
    return (
      <header className="sticky top-0 z-50 backdrop-blur-md bg-background/70 border-b border-border/50">
        <div className="mx-auto max-w-7xl px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <img src={logo} alt="PlaceReady" width={36} height={36} className="transition-transform group-hover:rotate-12" />
            <span className="text-2xl font-display tracking-tight">PlaceReady</span>
          </Link>
        </div>
      </header>
    );
  }

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("token");
      if (token) {
        await fetch("http://localhost:5000/api/auth/logout", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
      }
    } catch (err) {
      console.error("Logout error:", err);
    }
    logout();
    toast.success("Logged out successfully!");
    navigate({ to: "/" });
    setDropdownOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-background/70 border-b border-border/50">
      <div className="mx-auto max-w-7xl px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <img src={logo} alt="PlaceReady" width={36} height={36} className="transition-transform group-hover:rotate-12" />
          <span className="text-2xl font-display tracking-tight">PlaceReady</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm">
          {nav.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className="text-muted-foreground hover:text-foreground transition-colors"
              activeProps={{ className: "text-foreground font-medium" }}
              activeOptions={{ exact: n.to === "/" }}
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center hover:bg-primary/30 transition-colors overflow-hidden"
              >
                {user.photo ? (
                  <img
                    src={user.photo}
                    alt={user.name || user.email}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-5 h-5 text-primary" />
                )}
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-lg bg-card border border-border/50 shadow-lg overflow-hidden">
                  <div className="px-4 py-3 border-b border-border/50">
                    <p className="text-sm font-medium truncate">{user.email}</p>
                    <p className="text-xs text-muted-foreground">
                      {user.is_new_user ? "New User" : "Member"}
                    </p>
                  </div>

                  <div className="py-2">
                    <button
                      onClick={() => {
                        navigate({ to: "/dashboard" });
                        setDropdownOpen(false);
                      }}
                      className="w-full px-4 py-2 text-sm text-left hover:bg-secondary/50 transition-colors flex items-center gap-2"
                    >
                      <LayoutDashboard className="w-4 h-4" />
                      Dashboard
                    </button>

                    {user.is_admin && (
                      <button
                        onClick={() => {
                          navigate({ to: "/admin" });
                          setDropdownOpen(false);
                        }}
                        className="w-full px-4 py-2 text-sm text-left hover:bg-secondary/50 transition-colors flex items-center gap-2 text-amber-600"
                      >
                        <Shield className="w-4 h-4" />
                        Admin Panel
                      </button>
                    )}

                    <button
                      onClick={() => {
                        navigate({ to: "/profile" });
                        setDropdownOpen(false);
                      }}
                      className="w-full px-4 py-2 text-sm text-left hover:bg-secondary/50 transition-colors flex items-center gap-2"
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </button>

                    <button
                      onClick={() => {
                        navigate({ to: "/settings" });
                        setDropdownOpen(false);
                      }}
                      className="w-full px-4 py-2 text-sm text-left hover:bg-secondary/50 transition-colors flex items-center gap-2"
                    >
                      <Settings className="w-4 h-4" />
                      Settings
                    </button>
                  </div>

                  <div className="border-t border-border/50 py-2">
                    <button
                      onClick={handleLogout}
                      className="w-full px-4 py-2 text-sm text-left hover:bg-red-500/10 text-red-600 transition-colors flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4" />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link
                to="/auth"
                search={{ mode: "login" }}
                className="hidden sm:inline-flex items-center text-sm font-medium text-foreground hover:text-accent transition-colors px-4 py-2"
              >
                Login
              </Link>
              <Link
                to="/auth"
                search={{ mode: "signup" }}
                className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground pl-2 pr-5 py-2 text-sm font-medium hover:bg-primary/90 transition-all hover:gap-3"
              >
                <span className="flex -space-x-2">
                  <img src={avatar1} alt="" width={28} height={28} className="w-7 h-7 rounded-full border-2 border-primary object-cover" />
                  <img src={avatar2} alt="" width={28} height={28} className="w-7 h-7 rounded-full border-2 border-primary object-cover" />
                </span>
                Sign Up <span aria-hidden>↗</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
