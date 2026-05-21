import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Upload, Download, BarChart3, Users, TrendingUp, FileText } from "lucide-react";

interface StudentPrediction {
  _id: string;
  name?: string;
  email?: string;
  probability: number;
  tier: string;
  features: Record<string, number>;
  timestamp: string;
}

interface Analytics {
  totalStudents: number;
  tier1Count: number;
  tier2Count: number;
  tier3Count: number;
  belowTier3Count: number;
  averageProbability: number;
  averageCGPA: number;
}

export function AdminDashboard() {
  const [students, setStudents] = useState<StudentPrediction[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterTier, setFilterTier] = useState("all");
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchStudentData();
  }, []);

  const fetchStudentData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");

      const response = await fetch("http://localhost:5000/api/admin/students", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch student data");
      }

      const data = await response.json();
      setStudents(data.students || []);
      setAnalytics(data.analytics);
    } catch (err) {
      console.error("Error fetching student data:", err);
      toast.error("Failed to load student data");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:5000/api/admin/batch-predict", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to process file");
      }

      const data = await response.json();
      toast.success(`Processed ${data.processed} students successfully!`);
      fetchStudentData();
    } catch (err) {
      console.error("Error uploading file:", err);
      toast.error("Failed to process file");
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadExcel = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:5000/api/admin/export-excel", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to download file");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `students-predictions-${new Date().toISOString().split("T")[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("File downloaded successfully!");
    } catch (err) {
      console.error("Error downloading file:", err);
      toast.error("Failed to download file");
    }
  };

  const filteredStudents = students.filter((student) => {
    const matchesSearch =
      (student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email?.toLowerCase().includes(searchTerm.toLowerCase())) ??
      false;
    const matchesTier = filterTier === "all" || student.tier === filterTier;
    return matchesSearch && matchesTier;
  });

  const tierData = analytics
    ? [
        { name: "Tier-1", value: analytics.tier1Count, color: "#10b981" },
        { name: "Tier-2", value: analytics.tier2Count, color: "#3b82f6" },
        { name: "Tier-3", value: analytics.tier3Count, color: "#f59e0b" },
        { name: "Below Tier-3", value: analytics.belowTier3Count, color: "#ef4444" },
      ]
    : [];

  const cgpaDistribution = students.reduce(
    (acc, student) => {
      const cgpa = Math.floor(student.features["Current Academics Aggregate Marks"] || 0);
      const existing = acc.find((item) => item.cgpa === cgpa);
      if (existing) {
        existing.count += 1;
      } else {
        acc.push({ cgpa, count: 1 });
      }
      return acc;
    },
    [] as Array<{ cgpa: number; count: number }>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">Admin Dashboard</h1>
              <p className="mt-2 text-muted-foreground">
                Manage student predictions and view analytics
              </p>
            </div>
            <div className="flex gap-3">
              <label className="cursor-pointer">
                <Button disabled={uploading} className="gap-2">
                  <Upload className="h-4 w-4" />
                  {uploading ? "Uploading..." : "Upload Excel"}
                </Button>
                <input
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
              <Button onClick={handleDownloadExcel} variant="outline" className="gap-2">
                <Download className="h-4 w-4" />
                Download Data
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Stats Cards */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Students
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  <span className="text-3xl font-bold">{analytics.totalStudents}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Tier-1
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  <span className="text-3xl font-bold">{analytics.tier1Count}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {((analytics.tier1Count / analytics.totalStudents) * 100).toFixed(1)}%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Tier-2
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-500" />
                  <span className="text-3xl font-bold">{analytics.tier2Count}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {((analytics.tier2Count / analytics.totalStudents) * 100).toFixed(1)}%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Avg Probability
                </CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-3xl font-bold">
                  {(analytics.averageProbability * 100).toFixed(1)}%
                </span>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Avg CGPA
                </CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-3xl font-bold">
                  {analytics.averageCGPA.toFixed(2)}
                </span>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <Tabs defaultValue="analytics" className="space-y-6">
          <TabsList>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="students">Students</TabsTrigger>
          </TabsList>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tier Distribution Pie Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Tier Distribution</CardTitle>
                  <CardDescription>
                    Breakdown of students by placement tier
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {tierData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={tierData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {tierData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                      No data available
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* CGPA Distribution Bar Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>CGPA Distribution</CardTitle>
                  <CardDescription>
                    Number of students by CGPA range
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {cgpaDistribution.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={cgpaDistribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="cgpa" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                      No data available
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Probability Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Placement Probability Distribution</CardTitle>
                <CardDescription>
                  Trend of placement probabilities across all students
                </CardDescription>
              </CardHeader>
              <CardContent>
                {students.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart
                      data={students
                        .sort((a, b) => a.probability - b.probability)
                        .map((s, i) => ({
                          index: i,
                          probability: (s.probability * 100).toFixed(1),
                        }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="index" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="probability"
                        stroke="#10b981"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tier-wise Probability Comparison */}
            <Card>
              <CardHeader>
                <CardTitle>Average Probability by Tier</CardTitle>
                <CardDescription>
                  Comparison of average placement probability across tiers
                </CardDescription>
              </CardHeader>
              <CardContent>
                {students.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={[
                        {
                          tier: "Tier-1",
                          probability: (
                            (students
                              .filter((s) => s.tier === "Tier-1")
                              .reduce((sum, s) => sum + s.probability, 0) /
                              (students.filter((s) => s.tier === "Tier-1").length || 1)) *
                            100
                          ).toFixed(1),
                          count: students.filter((s) => s.tier === "Tier-1").length,
                        },
                        {
                          tier: "Tier-2",
                          probability: (
                            (students
                              .filter((s) => s.tier === "Tier-2")
                              .reduce((sum, s) => sum + s.probability, 0) /
                              (students.filter((s) => s.tier === "Tier-2").length || 1)) *
                            100
                          ).toFixed(1),
                          count: students.filter((s) => s.tier === "Tier-2").length,
                        },
                        {
                          tier: "Tier-3",
                          probability: (
                            (students
                              .filter((s) => s.tier === "Tier-3")
                              .reduce((sum, s) => sum + s.probability, 0) /
                              (students.filter((s) => s.tier === "Tier-3").length || 1)) *
                            100
                          ).toFixed(1),
                          count: students.filter((s) => s.tier === "Tier-3").length,
                        },
                        {
                          tier: "Below Tier-3",
                          probability: (
                            (students
                              .filter((s) => s.tier === "Below Tier-3")
                              .reduce((sum, s) => sum + s.probability, 0) /
                              (students.filter((s) => s.tier === "Below Tier-3").length || 1)) *
                            100
                          ).toFixed(1),
                          count: students.filter((s) => s.tier === "Below Tier-3").length,
                        },
                      ]}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="tier" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="probability" fill="#3b82f6" name="Avg Probability %" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Students Tab */}
          <TabsContent value="students" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Student Predictions</CardTitle>
                <CardDescription>
                  View and filter all student predictions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Filters */}
                <div className="flex gap-4 mb-6">
                  <Input
                    placeholder="Search by name or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="flex-1"
                  />
                  <Select value={filterTier} onValueChange={setFilterTier}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Filter by tier" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Tiers</SelectItem>
                      <SelectItem value="Tier-1">Tier-1</SelectItem>
                      <SelectItem value="Tier-2">Tier-2</SelectItem>
                      <SelectItem value="Tier-3">Tier-3</SelectItem>
                      <SelectItem value="Below Tier-3">Below Tier-3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Table */}
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">
                    Loading student data...
                  </div>
                ) : filteredStudents.length > 0 ? (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>CGPA</TableHead>
                          <TableHead>Probability</TableHead>
                          <TableHead>Tier</TableHead>
                          <TableHead>Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredStudents.map((student) => (
                          <TableRow key={student._id}>
                            <TableCell className="font-medium">
                              {student.name || "N/A"}
                            </TableCell>
                            <TableCell>{student.email || "N/A"}</TableCell>
                            <TableCell>
                              {(
                                student.features[
                                  "Current Academics Aggregate Marks"
                                ] || 0
                              ).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              <span className="font-semibold">
                                {(student.probability * 100).toFixed(1)}%
                              </span>
                            </TableCell>
                            <TableCell>
                              <span
                                className={`px-3 py-1 rounded-full text-sm font-medium ${
                                  student.tier === "Tier-1"
                                    ? "bg-green-100 text-green-800"
                                    : student.tier === "Tier-2"
                                      ? "bg-blue-100 text-blue-800"
                                      : student.tier === "Tier-3"
                                        ? "bg-amber-100 text-amber-800"
                                        : "bg-red-100 text-red-800"
                                }`}
                              >
                                {student.tier}
                              </span>
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {new Date(student.timestamp).toLocaleDateString()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No students found
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
