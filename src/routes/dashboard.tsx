import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { LogOut, User, BarChart3, BookOpen, Settings } from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

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
  const [predictions, setPredictions] = useState<any[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [stats, setStats] = useState({
    totalPredictions: 0,
    tier1Count: 0,
    tier2Count: 0,
    tier3Count: 0,
    belowTier3Count: 0,
    averageProbability: 0
  });

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token") || sessionStorage.getItem("token");
    const userData = localStorage.getItem("user") || sessionStorage.getItem("user");

    if (!token || !userData) {
      navigate({ to: "/auth", search: { mode: "login" } });
      return;
    }

    try {
      setUser(JSON.parse(userData));
      fetchUserPredictions(token);
    } catch (err) {
      navigate({ to: "/auth", search: { mode: "login" } });
    } finally {
      setLoading(false);
    }

    // Auto-refresh predictions every 3 seconds
    const interval = setInterval(() => {
      const currentToken = localStorage.getItem("token") || sessionStorage.getItem("token");
      if (currentToken) {
        fetchUserPredictions(currentToken);
      }
    }, 3000);

    // Also refresh when user comes back to this tab/window
    const handleFocus = () => {
      console.log('🔄 Dashboard regained focus, refreshing...');
      const currentToken = localStorage.getItem("token") || sessionStorage.getItem("token");
      if (currentToken) {
        fetchUserPredictions(currentToken);
      }
    };

    window.addEventListener('focus', handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', handleFocus);
    };
  }, [navigate]);

  const fetchUserPredictions = async (token: string) => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      console.log('📊 Fetching predictions from:', API_URL);
      
      const response = await fetch(`${API_URL}/api/user/predictions`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        console.error('❌ Failed to fetch predictions:', response.status);
        throw new Error("Failed to fetch predictions");
      }

      const data = await response.json();
      console.log('✅ Predictions received:', data.predictions?.length || 0);
      
      if (data.status === 'success' && data.predictions) {
        setPredictions(data.predictions);
        
        // Calculate stats
        const total = data.predictions.length;
        const tier1 = data.predictions.filter((p: any) => p.tier === 'Tier-1').length;
        const tier2 = data.predictions.filter((p: any) => p.tier === 'Tier-2').length;
        const tier3 = data.predictions.filter((p: any) => p.tier === 'Tier-3').length;
        const belowTier3 = data.predictions.filter((p: any) => p.tier === 'Below Tier-3').length;
        const avgProb = total > 0 ? data.predictions.reduce((sum: number, p: any) => sum + p.probability, 0) / total : 0;

        setStats({
          totalPredictions: total,
          tier1Count: tier1,
          tier2Count: tier2,
          tier3Count: tier3,
          belowTier3Count: belowTier3,
          averageProbability: avgProb
        });
        
        setLastUpdated(new Date().toLocaleTimeString());
        console.log('📈 Stats updated:', { total, tier1, tier2, tier3, belowTier3, avgProb: (avgProb * 100).toFixed(1) + '%' });
      }
    } catch (err) {
      console.error("Error fetching predictions:", err);
      // Don't show error toast, just continue with empty data
    }
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      
      if (token) {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
      }
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      sessionStorage.removeItem("token");
      sessionStorage.removeItem("user");
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
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {/* Predictions Made */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Predictions Made</h3>
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <p className="text-4xl font-bold">{stats.totalPredictions}</p>
            <p className="text-xs text-muted-foreground mt-2">Total predictions</p>
          </div>

          {/* Average Probability */}
          <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Avg. Probability</h3>
              <BookOpen className="w-5 h-5 text-primary" />
            </div>
            <p className="text-4xl font-bold">{(stats.averageProbability * 100).toFixed(1)}%</p>
            <p className="text-xs text-muted-foreground mt-2">Average placement chance</p>
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

        {/* Refresh Note */}
        {stats.totalPredictions > 0 && (
          <div className="mb-6 text-sm text-muted-foreground text-center">
            Last updated: {lastUpdated} • Auto-refreshing every 3 seconds
          </div>
        )}

        {/* Performance Graphs */}
        {stats.totalPredictions > 0 && (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold">Performance Analytics</h3>

            {/* Tier Distribution Pie Chart */}
            <div className="grid lg:grid-cols-2 gap-6">
              <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
                <h4 className="font-semibold mb-4">Tier Distribution</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Tier-1', value: stats.tier1Count, color: '#10b981' },
                        { name: 'Tier-2', value: stats.tier2Count, color: '#3b82f6' },
                        { name: 'Tier-3', value: stats.tier3Count, color: '#f59e0b' },
                        { name: 'Below Tier-3', value: stats.belowTier3Count, color: '#ef4444' },
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      <Cell fill="#10b981" />
                      <Cell fill="#3b82f6" />
                      <Cell fill="#f59e0b" />
                      <Cell fill="#ef4444" />
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Tier Breakdown Bar Chart */}
              <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
                <h4 className="font-semibold mb-4">Tier Breakdown</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { tier: 'T-1', count: stats.tier1Count },
                    { tier: 'T-2', count: stats.tier2Count },
                    { tier: 'T-3', count: stats.tier3Count },
                    { tier: 'Below', count: stats.belowTier3Count },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="tier" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Probability Trend */}
            <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
              <h4 className="font-semibold mb-4">Placement Probability Trend</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={predictions.map((p: any, i: number) => ({
                  index: i + 1,
                  probability: (p.probability * 100).toFixed(1),
                  tier: p.tier,
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" />
                  <YAxis />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload[0]) {
                        return (
                          <div className="bg-card border border-border rounded p-2 text-sm">
                            <p>Prediction #{payload[0].payload.index}</p>
                            <p className="text-primary">{payload[0].value}%</p>
                            <p className="text-muted-foreground">{payload[0].payload.tier}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="probability" 
                    stroke="#10b981" 
                    dot={{ fill: '#10b981', r: 4 }}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
