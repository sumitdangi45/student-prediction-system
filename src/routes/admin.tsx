import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { AdminDashboard } from "../components/AdminDashboard";

export const Route = createFileRoute("/admin")({
  head: () => ({
    meta: [
      { title: "Admin Dashboard — PlaceReady" },
      { name: "description", content: "Admin dashboard for managing student predictions and analytics." },
    ],
  }),
  component: AdminPage,
});

function AdminPage() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      toast.error("Please login first");
      navigate({ to: "/auth" });
      return;
    }

    if (user.is_admin) {
      setIsAdmin(true);
    } else {
      toast.error("You don't have admin access");
      navigate({ to: "/dashboard" });
    }
  }, [user, authLoading, navigate]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return <AdminDashboard />;
}
