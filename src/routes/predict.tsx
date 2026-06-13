import { useState } from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { CheckCircle2, AlertCircle, TrendingUp, Award, Info } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useProtectedRoute } from '@/hooks/useProtectedRoute';

function PredictPage() {
  const navigate = useNavigate();
  const { token, user, loading: authLoading } = useAuth();
  const { loading: isProtecting } = useProtectedRoute();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('academic');
  const [showSkillsHover, setShowSkillsHover] = useState(false);
  const [formData, setFormData] = useState({
    cgpa: '',
    '12th_marks': '',
    '10th_marks': '',
    '12th_board': 'CBSE',
    '10th_board': 'CBSE',
    closed_backlogs: '0',
    live_backlogs: '0',
    academic_trend: '0',
    has_experience: '0',
    num_companies: '0',
    has_internship: '0',
    skills_count: '0',
    projects_count: '0',
    certifications_count: '0',
    is_female: '0',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePredict = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!formData.cgpa || !formData['12th_marks'] || !formData['10th_marks']) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    // Validate CGPA range (0-10)
    const cgpa = parseFloat(formData.cgpa);
    if (cgpa < 0 || cgpa > 10) {
      toast.error('CGPA must be between 0 and 10');
      return;
    }
    
    // Validate marks range (0-100)
    const marks12 = parseFloat(formData['12th_marks']);
    const marks10 = parseFloat(formData['10th_marks']);
    if (marks12 < 0 || marks12 > 100 || marks10 < 0 || marks10 > 100) {
      toast.error('12th and 10th marks must be between 0 and 100');
      return;
    }
    
    // Validate backlogs (non-negative)
    const closedBacklogs = parseInt(formData.closed_backlogs);
    const liveBacklogs = parseInt(formData.live_backlogs);
    if (closedBacklogs < 0 || liveBacklogs < 0) {
      toast.error('Backlogs cannot be negative');
      return;
    }
    
    // Validate companies count (non-negative)
    const numCompanies = parseInt(formData.num_companies);
    if (numCompanies < 0) {
      toast.error('Number of companies cannot be negative');
      return;
    }

    setLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      // Add token if user is authenticated
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          cgpa: parseFloat(formData.cgpa),
          marks_12: parseFloat(formData['12th_marks']),
          marks_10: parseFloat(formData['10th_marks']),
          closed_backlogs: parseInt(formData.closed_backlogs),
          live_backlogs: parseInt(formData.live_backlogs),
          num_companies: parseInt(formData.num_companies),
          has_experience: parseInt(formData.has_experience),
        }),
      });

      if (!response.ok) {
        throw new Error('Prediction failed');
      }

      const data = await response.json();
      if (data.status === 'error') {
        throw new Error(data.message || 'Prediction failed');
      }
      
      // Format response with percentage and recommendation
      const formattedResult = {
        ...data,
        percentage: `${(data.probability * 100).toFixed(1)}%`,
        timestamp: new Date().toISOString(),
        recommendation: generateRecommendation(data.tier, data.probability, parseFloat(formData.cgpa))
      };
      
      setResult(formattedResult);
      toast.success('Prediction completed!');
      
      // Check if profile is complete - if not, redirect to profile
      // Profile is incomplete if name is empty
      if (!user?.name || user.name.trim() === '') {
        toast.info('Please complete your profile to continue');
        setTimeout(() => {
          navigate({ to: '/profile' });
        }, 1500);
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to get prediction');
    } finally {
      setLoading(false);
    }
  };

  // Helper function to generate recommendation
  const generateRecommendation = (tier: string, probability: number, cgpa: number): string => {
    if (tier === 'Tier-1') {
      return 'Excellent! You have a very high chance of placement. Focus on polishing your interview skills and domain expertise.';
    } else if (tier === 'Tier-2') {
      return 'Great! You have a good chance of placement. Work on building projects and gaining practical experience.';
    } else if (tier === 'Tier-3') {
      return 'Good opportunity ahead! Improve your technical skills, solve coding problems, and build more projects.';
    } else {
      return 'Keep improving! Focus on CGPA, gain work experience, and develop in-demand skills. Consider internships and open-source contributions.';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary to-background py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 mb-4 px-4 py-2 rounded-full bg-primary/10 text-primary">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-medium">AI-Powered Prediction</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-display mb-4">
            Predict Your <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Placement</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Enter your academic details and let our machine learning model predict your placement chances with 63.64% accuracy.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 shadow-lg">
              {/* Tabs */}
              <div className="flex gap-2 mb-8 border-b border-border/50">
                <button
                  onClick={() => setActiveTab('academic')}
                  className={cn(
                    'px-4 py-3 font-medium text-sm transition-all border-b-2 -mb-[2px]',
                    activeTab === 'academic'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  )}
                >
                  📚 Academic
                </button>
                <button
                  onClick={() => setActiveTab('experience')}
                  className={cn(
                    'px-4 py-3 font-medium text-sm transition-all border-b-2 -mb-[2px]',
                    activeTab === 'experience'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  )}
                >
                  💼 Experience
                </button>
                <button
                  onClick={() => setActiveTab('skills')}
                  className={cn(
                    'px-4 py-3 font-medium text-sm transition-all border-b-2 -mb-[2px]',
                    activeTab === 'skills'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  )}
                >
                  ⭐ Skills
                </button>
              </div>

              <form onSubmit={handlePredict} className="space-y-6">
                {/* Academic Tab */}
                {activeTab === 'academic' && (
                  <div className="space-y-6 animate-in fade-in duration-300">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-semibold mb-2">CGPA *</label>
                        <div className="relative">
                          <Input
                            type="number"
                            name="cgpa"
                            placeholder="7.5"
                            step="0.01"
                            min="0"
                            max="10"
                            value={formData.cgpa}
                            onChange={handleChange}
                            required
                            className="pr-8"
                          />
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">/10</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">12th Marks *</label>
                        <div className="relative">
                          <Input
                            type="number"
                            name="12th_marks"
                            placeholder="85"
                            step="0.1"
                            min="0"
                            max="100"
                            value={formData['12th_marks']}
                            onChange={handleChange}
                            required
                            className="pr-8"
                          />
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">/100</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">12th Board</label>
                        <select
                          name="12th_board"
                          value={formData['12th_board']}
                          onChange={handleChange}
                          className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground"
                        >
                          <option value="CBSE">CBSE</option>
                          <option value="ICSE">ICSE</option>
                          <option value="State Board">State Board</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">10th Marks *</label>
                        <div className="relative">
                          <Input
                            type="number"
                            name="10th_marks"
                            placeholder="90"
                            step="0.1"
                            min="0"
                            max="100"
                            value={formData['10th_marks']}
                            onChange={handleChange}
                            required
                            className="pr-8"
                          />
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">/100</span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">10th Board</label>
                        <select
                          name="10th_board"
                          value={formData['10th_board']}
                          onChange={handleChange}
                          className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground"
                        >
                          <option value="CBSE">CBSE</option>
                          <option value="ICSE">ICSE</option>
                          <option value="State Board">State Board</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">Closed Backlogs</label>
                        <Input
                          type="number"
                          name="closed_backlogs"
                          placeholder="0"
                          min="0"
                          value={formData.closed_backlogs}
                          onChange={handleChange}
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">Live Backlogs</label>
                        <Input
                          type="number"
                          name="live_backlogs"
                          placeholder="0"
                          min="0"
                          value={formData.live_backlogs}
                          onChange={handleChange}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold mb-2">Academic Trend</label>
                      <p className="text-xs text-muted-foreground mb-2">Improvement from 1st to 8th semester (positive = improving)</p>
                      <Input
                        type="number"
                        name="academic_trend"
                        placeholder="0.5"
                        step="0.1"
                        value={formData.academic_trend}
                        onChange={handleChange}
                      />
                    </div>
                  </div>
                )}

                {/* Experience Tab */}
                {activeTab === 'experience' && (
                  <div className="space-y-6 animate-in fade-in duration-300">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-semibold mb-3">Professional Experience</label>
                        <div className="flex gap-3">
                          {['0', '1'].map((val) => (
                            <button
                              key={val}
                              type="button"
                              onClick={() => setFormData(prev => ({ ...prev, has_experience: val }))}
                              className={cn(
                                'flex-1 py-2 px-4 rounded-lg font-medium transition-all',
                                formData.has_experience === val
                                  ? 'bg-primary text-primary-foreground'
                                  : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                              )}
                            >
                              {val === '0' ? 'No' : 'Yes'}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">Number of Companies</label>
                        <Input
                          type="number"
                          name="num_companies"
                          placeholder="0"
                          min="0"
                          value={formData.num_companies}
                          onChange={handleChange}
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-3">Internship Experience</label>
                        <div className="flex gap-3">
                          {['0', '1'].map((val) => (
                            <button
                              key={val}
                              type="button"
                              onClick={() => setFormData(prev => ({ ...prev, has_internship: val }))}
                              className={cn(
                                'flex-1 py-2 px-4 rounded-lg font-medium transition-all',
                                formData.has_internship === val
                                  ? 'bg-primary text-primary-foreground'
                                  : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                              )}
                            >
                              {val === '0' ? 'No' : 'Yes'}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-3">Gender</label>
                        <div className="flex gap-3">
                          {[
                            { val: '0', label: 'Male' },
                            { val: '1', label: 'Female' }
                          ].map(({ val, label }) => (
                            <button
                              key={val}
                              type="button"
                              onClick={() => setFormData(prev => ({ ...prev, is_female: val }))}
                              className={cn(
                                'flex-1 py-2 px-4 rounded-lg font-medium transition-all',
                                formData.is_female === val
                                  ? 'bg-primary text-primary-foreground'
                                  : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                              )}
                            >
                              {label}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Skills Tab */}
                {activeTab === 'skills' && (
                  <div className="space-y-6 animate-in fade-in duration-300">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-semibold mb-2 flex items-center gap-2">
                          Skills Listed
                          <div className="relative group">
                            <Info className="w-4 h-4 text-muted-foreground cursor-help" />
                            <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block bg-popover text-popover-foreground text-xs p-2 rounded border border-border whitespace-nowrap z-10">
                              Enter number of skills you have listed
                            </div>
                          </div>
                        </label>
                        <Input
                          type="number"
                          name="skills_count"
                          placeholder="0"
                          min="0"
                          max="50"
                          value={formData.skills_count}
                          onChange={handleChange}
                        />
                        <p className="text-xs text-muted-foreground mt-1">e.g., JavaScript, Python, React, etc.</p>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">Projects Count</label>
                        <Input
                          type="number"
                          name="projects_count"
                          placeholder="0"
                          min="0"
                          max="50"
                          value={formData.projects_count}
                          onChange={handleChange}
                        />
                        <p className="text-xs text-muted-foreground mt-1">Number of projects you've completed</p>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold mb-2">Certifications Count</label>
                        <Input
                          type="number"
                          name="certifications_count"
                          placeholder="0"
                          min="0"
                          max="50"
                          value={formData.certifications_count}
                          onChange={handleChange}
                        />
                        <p className="text-xs text-muted-foreground mt-1">Number of certifications you have</p>
                      </div>
                    </div>

                    <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                      <p className="text-sm text-blue-900 dark:text-blue-100">
                        💡 <strong>Tip:</strong> More skills, projects, and certifications increase your placement chances!
                      </p>
                    </div>
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={loading}
                  size="lg"
                  className="w-full mt-8 h-12 text-base font-semibold"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin mr-2">⚙️</span>
                      Analyzing Your Profile...
                    </>
                  ) : (
                    <>
                      <Award className="w-5 h-5 mr-2" />
                      Get My Prediction
                    </>
                  )}
                </Button>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-1">
            {result ? (
              <div className="rounded-2xl border border-border/50 bg-gradient-to-br from-primary/10 to-accent/10 backdrop-blur-sm p-8 shadow-lg sticky top-8">
                <div className="space-y-6">
                  {/* Probability */}
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground mb-2">Placement Probability</p>
                    <div className="text-6xl font-display bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                      {result.percentage}
                    </div>
                  </div>

                  {/* Tier Badge */}
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground mb-2">Placement Tier</p>
                    <div className={cn(
                      'inline-block px-6 py-2 rounded-full font-semibold text-sm',
                      result.tier === 'Tier-1' ? 'bg-green-100 text-green-800' :
                      result.tier === 'Tier-2' ? 'bg-blue-100 text-blue-800' :
                      result.tier === 'Tier-3' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    )}>
                      {result.tier}
                    </div>
                  </div>

                  {/* Status Icon */}
                  <div className="flex justify-center">
                    {parseFloat(result.percentage) >= 50 ? (
                      <CheckCircle2 className="w-16 h-16 text-green-500" />
                    ) : (
                      <AlertCircle className="w-16 h-16 text-yellow-500" />
                    )}
                  </div>

                  {/* Recommendation */}
                  <div className="bg-background/50 rounded-lg p-4">
                    <p className="text-sm font-semibold mb-2">💡 Recommendation</p>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {result.recommendation}
                    </p>
                  </div>

                  {/* View Roadmap Button */}
                  <a
                    href={`/recommendations?tier=${encodeURIComponent(result.tier)}&cgpa=${formData.cgpa}&probability=${result.percentage}`}
                    className="block w-full"
                  >
                    <Button
                      type="button"
                      size="lg"
                      className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    >
                      <TrendingUp className="w-5 h-5 mr-2" />
                      View Your Roadmap
                    </Button>
                  </a>

                  {/* Timestamp */}
                  <div className="pt-4 border-t border-border/50 text-center">
                    <p className="text-xs text-muted-foreground">
                      Predicted at {new Date(result.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm p-8 shadow-lg sticky top-8">
                <div className="text-center space-y-4">
                  <Award className="w-12 h-12 text-primary/50 mx-auto" />
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Fill in your details across the tabs and click "Get My Prediction" to see your placement chances.
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

export const Route = createFileRoute('/predict')({
  component: PredictPage,
});
