import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ArrowLeft, Save, User, Mail, Calendar, Upload, X } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: "Profile — PlaceReady" },
      { name: "description", content: "Manage your PlaceReady profile" },
    ],
  }),
  component: ProfilePage,
});

function ProfilePage() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    college: "",
    branch: "",
    cgpa: "",
    graduationYear: "",
    photo: "",
  });

  useEffect(() => {
    // Check if user is logged in
    if (!token || !user) {
      navigate({ to: "/auth", search: { mode: "login" } });
      return;
    }

    // Load user data
    setFormData((prev) => ({
      ...prev,
      name: user.name || "",
      email: user.email || "",
    }));

    // Fetch full profile data
    fetchProfile();
  }, [token, user, navigate]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:5000/api/auth/profile", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === "success") {
          setFormData((prev) => ({
            ...prev,
            ...data.profile,
          }));
          if (data.profile.photo) {
            setPhotoPreview(data.profile.photo);
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      toast.error("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Photo size must be less than 5MB");
        return;
      }

      // Validate file type
      if (!file.type.startsWith("image/")) {
        toast.error("Please select a valid image file");
        return;
      }

      setPhotoFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
    setFormData((prev) => ({
      ...prev,
      photo: "",
    }));
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error("Name is required");
      return;
    }

    setSaving(true);
    try {
      const response = await fetch("http://localhost:5000/api/auth/update-profile", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...formData,
          photo: photoPreview || formData.photo,
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        // Update localStorage with new user data including photo
        const updatedUser = { 
          ...user, 
          name: formData.name,
          photo: photoPreview || formData.photo,
        };
        localStorage.setItem("user", JSON.stringify(updatedUser));
        
        // Trigger a custom event to update AuthContext
        window.dispatchEvent(new CustomEvent('userProfileUpdated', { detail: updatedUser }));
        
        toast.success("Profile updated successfully!");
        setPhotoFile(null);
      } else {
        toast.error(data.message || "Failed to update profile");
      }
    } catch (err) {
      toast.error("Failed to update profile");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background">
      {/* Header */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate({ to: "/dashboard" })}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold">Profile</h1>
              <p className="text-sm text-muted-foreground">Manage your account information</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8">
          <form onSubmit={handleSaveProfile} className="space-y-8">
            {/* Photo Upload Section */}
            <div>
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                Profile Photo
              </h2>

              <div className="flex flex-col md:flex-row gap-8 items-start">
                {/* Photo Preview */}
                <div className="flex flex-col items-center gap-4">
                  <div className="w-32 h-32 rounded-full bg-secondary border-2 border-border overflow-hidden flex items-center justify-center">
                    {photoPreview ? (
                      <img
                        src={photoPreview}
                        alt="Profile"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="w-16 h-16 text-muted-foreground" />
                    )}
                  </div>

                  {photoPreview && (
                    <button
                      type="button"
                      onClick={removePhoto}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Remove Photo
                    </button>
                  )}
                </div>

                {/* Upload Area */}
                <div className="flex-1">
                  <label className="block">
                    <div className="border-2 border-dashed border-border rounded-lg p-8 hover:border-primary/50 transition-colors cursor-pointer bg-background/50">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handlePhotoChange}
                        className="hidden"
                      />
                      <div className="flex flex-col items-center gap-3 text-center">
                        <Upload className="w-8 h-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">Click to upload or drag and drop</p>
                          <p className="text-sm text-muted-foreground">PNG, JPG, GIF up to 5MB</p>
                        </div>
                      </div>
                    </div>
                  </label>
                  <p className="text-xs text-muted-foreground mt-3">
                    📸 Use a clear, professional photo for better placement chances
                  </p>
                </div>
              </div>
            </div>

            {/* Personal Information Section */}
            <div className="border-t border-border/50 pt-8">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                Personal Information
              </h2>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    disabled
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 opacity-60 cursor-not-allowed"
                  />
                  <p className="text-xs text-muted-foreground mt-1">Email cannot be changed</p>
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="Enter your phone number"
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                {/* College */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    College/University
                  </label>
                  <input
                    type="text"
                    name="college"
                    value={formData.college}
                    onChange={handleInputChange}
                    placeholder="Enter your college name"
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            {/* Academic Information Section */}
            <div className="border-t border-border/50 pt-8">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" />
                Academic Information
              </h2>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Branch */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Branch/Stream
                  </label>
                  <select
                    name="branch"
                    value={formData.branch}
                    onChange={handleInputChange}
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">Select your branch</option>
                    <option value="CSE">Computer Science & Engineering</option>
                    <option value="ECE">Electronics & Communication</option>
                    <option value="ME">Mechanical Engineering</option>
                    <option value="CE">Civil Engineering</option>
                    <option value="EE">Electrical Engineering</option>
                    <option value="IT">Information Technology</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* CGPA */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Current CGPA
                  </label>
                  <input
                    type="number"
                    name="cgpa"
                    value={formData.cgpa}
                    onChange={handleInputChange}
                    placeholder="e.g., 7.5"
                    step="0.01"
                    min="0"
                    max="10"
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                {/* Graduation Year */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Expected Graduation Year
                  </label>
                  <select
                    name="graduationYear"
                    value={formData.graduationYear}
                    onChange={handleInputChange}
                    className="w-full rounded-lg bg-background border border-border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">Select graduation year</option>
                    <option value="2024">2024</option>
                    <option value="2025">2025</option>
                    <option value="2026">2026</option>
                    <option value="2027">2027</option>
                    <option value="2028">2028</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="border-t border-border/50 pt-8 flex gap-4 justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate({ to: "/dashboard" })}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={saving}
                className="gap-2"
              >
                <Save className="w-4 h-4" />
                {saving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </div>

        {/* Info Box */}
        <div className="mt-8 rounded-lg bg-primary/10 border border-primary/20 p-4">
          <p className="text-sm text-foreground">
            💡 <strong>Tip:</strong> Keep your profile information up to date to get more accurate placement predictions and personalized recommendations.
          </p>
        </div>
      </div>
    </div>
  );
}
