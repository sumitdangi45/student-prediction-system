import { useState, useEffect } from 'react';
import { createFileRoute, useSearch, useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { Lightbulb, BookOpen, Code, Target, Calendar, Award, ArrowLeft } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

function RecommendationsPage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const search = useSearch({ from: '/recommendations' });
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [predictionData, setPredictionData] = useState<any>(null);
  const [formData, setFormData] = useState({
    tier: 'Tier-2',
    cgpa: '7.5',
    skills: 'JavaScript, React',
    experience: 'No',
    timeline: '3 months'
  });

  // Auto-fill form if coming from predict page or from user profile
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tier = params.get('tier');
    const cgpa = params.get('cgpa');
    const probability = params.get('probability');
    
    if (tier && cgpa) {
      setFormData(prev => ({
        ...prev,
        tier: tier,
        cgpa: cgpa
      }));
      setPredictionData({ tier, cgpa, probability });
      // Don't auto-generate - wait for user to click button
    } else if (token) {
      // Fetch user profile to get CGPA
      fetchUserProfile();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/profile', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.profile.cgpa) {
          setFormData(prev => ({
            ...prev,
            cgpa: data.profile.cgpa,
          }));
        }
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const generateRecommendationsAuto = async (tier: string, cgpa: string) => {
    setLoading(true);
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      // Add token if user is authenticated
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('http://localhost:5000/api/recommendations', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          tier: tier,
          cgpa: cgpa,
          skills: formData.skills,
          experience: formData.experience,
          timeline: formData.timeline
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate recommendations');
      }

      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to generate recommendations');
    } finally {
      setLoading(false);
    }
  };

  const generateRecommendations = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    setLoading(true);
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      // Add token if user is authenticated
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('http://localhost:5000/api/recommendations', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          tier: formData.tier,
          cgpa: formData.cgpa,
          skills: formData.skills,
          experience: formData.experience,
          timeline: formData.timeline
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate recommendations');
      }

      const data = await response.json();
      setRecommendations(data);
      toast.success('Recommendations generated!');
    } catch (error) {
      console.error('Error:', error);
      toast.error('Failed to generate recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 mb-4 px-4 py-2 rounded-full bg-primary/10 text-primary">
            <Lightbulb className="w-4 h-4" />
            <span className="text-sm font-medium">Personalized Roadmap</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-display mb-4">
            Your <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Placement Roadmap</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Get a personalized action plan to improve your placement chances and land your dream job.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Form */}
          <div className="lg:col-span-1">
            <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 shadow-lg sticky top-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-display">Your Profile</h2>
                {predictionData && (
                  <div className="text-xs bg-green-500/20 text-green-700 px-2 py-1 rounded">
                    From Prediction
                  </div>
                )}
              </div>
              
              {predictionData && (
                <div className="mb-6 p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                  <p className="text-sm text-green-700 font-semibold mb-2">📊 Prediction Result</p>
                  <p className="text-xs text-green-600">
                    Tier: <span className="font-bold">{predictionData.tier}</span> | 
                    Probability: <span className="font-bold">{predictionData.probability}</span>
                  </p>
                </div>
              )}
              
              <form onSubmit={generateRecommendations} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">Placement Tier</label>
                  <select
                    name="tier"
                    value={formData.tier}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background"
                  >
                    <option value="Tier-1">Tier-1</option>
                    <option value="Tier-2">Tier-2</option>
                    <option value="Tier-3">Tier-3</option>
                    <option value="Below Tier-3">Below Tier-3</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Current CGPA</label>
                  <Input
                    type="number"
                    name="cgpa"
                    placeholder="7.5"
                    step="0.1"
                    min="0"
                    max="10"
                    value={formData.cgpa}
                    onChange={handleChange}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Current Skills</label>
                  <Input
                    type="text"
                    name="skills"
                    placeholder="e.g., JavaScript, React"
                    value={formData.skills}
                    onChange={handleChange}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Professional Experience</label>
                  <select
                    name="experience"
                    value={formData.experience}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background"
                  >
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Available Timeline</label>
                  <select
                    name="timeline"
                    value={formData.timeline}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background"
                  >
                    <option value="1 month">1 month</option>
                    <option value="3 months">3 months</option>
                    <option value="6 months">6 months</option>
                    <option value="1 year">1 year</option>
                  </select>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  size="lg"
                  className="w-full mt-6"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin mr-2">⚙️</span>
                      Generating...
                    </>
                  ) : (
                    <>
                      <Target className="w-5 h-5 mr-2" />
                      Generate Roadmap
                    </>
                  )}
                </Button>
              </form>
            </div>
          </div>

          {/* Recommendations */}
          <div className="lg:col-span-2">
            {recommendations ? (
              <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 shadow-lg">
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Award className="w-6 h-6 text-primary" />
                    <h2 className="text-2xl font-display">Your Personalized Roadmap</h2>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Tier: <span className="font-semibold text-foreground">{recommendations.tier}</span> | 
                    CGPA: <span className="font-semibold text-foreground">{recommendations.cgpa}</span>
                  </p>
                </div>

                <div className="prose prose-invert max-w-none">
                  <div className="space-y-4 text-sm leading-relaxed whitespace-pre-wrap text-muted-foreground">
                    {recommendations.content}
                  </div>
                </div>

                <div className="mt-8 pt-8 border-t border-border/50">
                  <p className="text-xs text-muted-foreground">
                    Generated at {new Date(recommendations.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 shadow-lg">
                <div className="text-center space-y-4">
                  <BookOpen className="w-12 h-12 text-primary/50 mx-auto" />
                  <p className="text-muted-foreground">
                    {predictionData 
                      ? 'Loading your personalized roadmap...' 
                      : 'Fill in your profile details and click "Generate Roadmap" to get personalized recommendations.'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute('/recommendations')({
  component: RecommendationsPage,
});
