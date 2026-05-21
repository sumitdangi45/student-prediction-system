import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { LogOut, User, BarChart3, BookOpen, Settings } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — PlaceReady" },
      { name: "description", content: "Your PlaceReady dashboard" },
    ],
  }),
  component: DashboardPage,
});

function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");

    if (!token || !userData) {
      navigate({ to: "/auth", search: { mode: "login" } });
      return;
    }

    try {
      setUser(JSON.parse(userData));
    } catch (err) {
      navigate({ to: "/auth", search: { mode: "login" } });
    } finally {
      setLoading(false);
    }
  }, [navigate]);

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
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      toast.success("Logged out successfully!");
      navigate({ to: "/auth", search: { mode: "login" } });
    } catch (err) {
      toast.error("Logout failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background">
      {/* Header */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">PlaceReady</h1>
            <p className="text-sm text-muted-foreground">Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user?.email}</p>
              <p className="text-xs text-muted-foreground">
                {user?.is_new_user ? "New User" : "Returning User"}
              </p>
            </div>
            <Button
              onClick={handleLogout}
              variant="outline"
              size="sm"
              className="gap-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h2 className="text-4xl font-bold mb-2">
            Welcome back, <span className="text-primary">{user?.email?.split("@")[0]}</span>!
          </h2>
          <p className="text-lg text-muted-foreground">
            Here's your placement preparation dashboard
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {/* Predict Card */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-6 hover:border-primary/50 transition-all cursor-pointer group"
            onClick={() => navigate({ to: "/predict" })}>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
              <BarChart3 className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Get Prediction</h3>
            <p className="text-sm text-muted-foreground">
              Predict your placement chances
            </p>
          </div>

          {/* Roadmap Card */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-6 hover:border-primary/50 transition-all cursor-pointer group"
            onClick={() => navigate({ to: "/recommendations" })}>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
              <BookOpen className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">View Roadmap</h3>
            <p className="text-sm text-muted-foreground">
              Get personalized preparation roadmap
            </p>
          </div>

          {/* Profile Card */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-6 hover:border-primary/50 transition-all cursor-pointer group"
            onClick={() => navigate({ to: "/profile" })}>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
              <User className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Profile</h3>
            <p className="text-sm text-muted-foreground">
              Update your profile information
            </p>
          </div>

          {/* Settings Card */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-6 hover:border-primary/50 transition-all cursor-pointer group"
            onClick={() => navigate({ to: "/settings" })}>
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
              <Settings className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Settings</h3>
            <p className="text-sm text-muted-foreground">
              Manage your account settings
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Predictions Made */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Predictions Made</h3>
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <p className="text-4xl font-bold">0</p>
            <p className="text-xs text-muted-foreground mt-2">This month</p>
          </div>

          {/* Roadmaps Generated */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Roadmaps Generated</h3>
              <BookOpen className="w-5 h-5 text-primary" />
            </div>
            <p className="text-4xl font-bold">0</p>
            <p className="text-xs text-muted-foreground mt-2">This month</p>
          </div>

          {/* Account Status */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Account Status</h3>
              <User className="w-5 h-5 text-primary" />
            </div>
            <p className="text-4xl font-bold">Active</p>
            <p className="text-xs text-muted-foreground mt-2">All systems operational</p>
          </div>
        </div>
      </div>
    </div>
  );
}
