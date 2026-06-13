import { useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { CheckCircle2, AlertCircle, Loader } from "lucide-react";

interface SetupStatus {
  admin_user: {
    email: string;
    is_admin: boolean;
  } | null;
  storage_buckets: string[];
  has_profile_photos_bucket: boolean;
  predictions_with_source: number;
}

export function SetupInitializer() {
  const [status, setStatus] = useState<SetupStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [making_admin, setMakingAdmin] = useState(false);
  const [creating_bucket, setCreatingBucket] = useState(false);
  const [init_source, setInitSource] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  // Load status on mount
  const fetchStatus = async () => {
    try {
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/setup/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.status === 'success') {
        setStatus(data.setup);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load setup status:', err);
      setLoading(false);
    }
  };

  const makeAdmin = async () => {
    try {
      setMakingAdmin(true);
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      const user = JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{}');

      if (!user.email) {
        toast.error("User email not found");
        return;
      }

      const response = await fetch(`${API_URL}/api/setup/make-admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: user.email,
          master_key: 'initial-setup-key'
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success(`✅ ${user.email} is now admin!`);
        await fetchStatus();
      } else {
        toast.error(data.message);
      }
    } catch (err) {
      console.error('Error:', err);
      toast.error("Failed to make admin");
    } finally {
      setMakingAdmin(false);
    }
  };

  const createBucket = async () => {
    try {
      setCreatingBucket(true);
      const response = await fetch(`${API_URL}/api/setup/create-storage-bucket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          master_key: 'initial-setup-key'
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success("✅ Storage bucket ready!");
        await fetchStatus();
      } else {
        toast.error(data.message);
      }
    } catch (err) {
      console.error('Error:', err);
      toast.error("Failed to create bucket");
    } finally {
      setCreatingBucket(false);
    }
  };

  const initializeSource = async () => {
    try {
      setInitSource(true);
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');

      const response = await fetch(`${API_URL}/api/setup/init-source-column`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success(`✅ ${data.updated_count} predictions updated!`);
        await fetchStatus();
      } else {
        toast.error(data.message);
      }
    } catch (err) {
      console.error('Error:', err);
      toast.error("Failed to initialize source");
    } finally {
      setInitSource(false);
    }
  };

  if (loading) {
    return null; // Don't show if still loading or not admin
  }

  if (!status || !status.admin_user?.is_admin) {
    return null;
  }

  const all_setup = status.has_profile_photos_bucket && status.predictions_with_source > 0;

  if (all_setup) {
    return null; // Everything is set up
  }

  return (
    <div className="fixed bottom-4 right-4 bg-card border border-border rounded-lg shadow-lg p-4 max-w-sm z-50">
      <div className="space-y-3">
        <h3 className="font-semibold flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-yellow-500" />
          System Setup
        </h3>

        {/* Admin Status */}
        <div className="flex items-center justify-between p-2 bg-background/50 rounded">
          <span className="text-sm">Admin Access</span>
          <CheckCircle2 className="w-4 h-4 text-green-500" />
        </div>

        {/* Storage Bucket */}
        <div className="flex items-center justify-between p-2 bg-background/50 rounded">
          <span className="text-sm">Photo Storage</span>
          {status.has_profile_photos_bucket ? (
            <CheckCircle2 className="w-4 h-4 text-green-500" />
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={createBucket}
              disabled={creating_bucket}
              className="h-7 text-xs"
            >
              {creating_bucket ? (
                <Loader className="w-3 h-3 animate-spin" />
              ) : (
                "Setup"
              )}
            </Button>
          )}
        </div>

        {/* Source Column */}
        <div className="flex items-center justify-between p-2 bg-background/50 rounded">
          <span className="text-sm">Data Sources</span>
          {status.predictions_with_source > 0 ? (
            <CheckCircle2 className="w-4 h-4 text-green-500" />
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={initializeSource}
              disabled={init_source}
              className="h-7 text-xs"
            >
              {init_source ? (
                <Loader className="w-3 h-3 animate-spin" />
              ) : (
                "Init"
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
