import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Search, Download, CheckCircle, XCircle, Loader2, ShieldCheck, FileText } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import ReactMarkdown from "react-markdown";


const agentSteps = [
  { key: "base", label: "Extracting paper", icon: "🔍" },
  { key: "grammar", label: "Analyzing grammar", icon: "✍️" },
  { key: "consistency", label: "Checking consistency", icon: "📊" },
  { key: "authenticity", label: "Assessing authenticity", icon: "🛡️" },
  { key: "fact", label: "Fact-checking claims", icon: "🔎" },
  { key: "novelty", label: "Evaluating novelty", icon: "💡" },
];


interface AnalysisResult {
  title: string;
  source: string;
  executive_summary: string;
  recommendation: string;
  consistency_score: number;
  novelty: string;
  grammar_rating: "high" | "medium" | "low";
  // grammar_details: { label: string; score: number }[];
  fact_check: { claim: string; verified: boolean; source?: string }[];
  authenticity_score: number;
  pass: boolean;
  pdf_path?: string;
}



const Index = () => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleEvaluate = async () => {
    if (!url.trim()) return;
  
    setLoading(true);
    setResult(null);
  
    try {
      const res = await fetch("http://127.0.0.1:8000/evaluate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });
  
      const json = await res.json();
  
      if (json.status !== "success") {
        throw new Error("Backend error");
      }
  
      const data = json.data;
  
      
      const mappedResult: AnalysisResult = {
        title: data.title || "Untitled Paper",
  
        source: "arXiv · AI Research",
  
        executive_summary:
          data.executive_summary || data.abstract || "No summary available",
  
        recommendation:
          data.recommendation || "No recommendation provided.",
  
        consistency_score: data.consistency_score ?? 0,
  
        novelty: data.novelty || "Novelty not analyzed.",
  
        grammar_rating: data.grammar_rating || "medium",
  
        // grammar_details: [
        //   { label: "Clarity", score: 80 },
        //   { label: "Technical precision", score: 75 },
        // ], 
  
        fact_check: data.fact_check || [],
  
        authenticity_score:
          typeof data.authenticity_score === "number"
            ? data.authenticity_score / 100
            : 0.8,
  
        pass: data.recommendation || "-",
        pdf_path: data.pdf_path,
      };
  
      setResult(mappedResult);
  
    } catch (err) {
      console.error(err);
      alert("Failed to evaluate paper");
    }
  
    setLoading(false);
  };

  const handleDownloadPDF = () => {
    if (!result?.pdf_path) {
      console.error("No PDF path found");
      return;
    }
  
    const file = result.pdf_path.split("/").pop();
  
    const url = `http://127.0.0.1:8000/report/${file}`;
  
    window.open(url, "_blank");
  };


  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!loading) return;

    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % agentSteps.length;
      setActiveStep(i);
    }, 1200); 

    return () => clearInterval(interval);
  }, [loading]);

  return (
    <div
      className="min-h-screen relative overflow-hidden"
      style={{ fontFamily: "Inter, system-ui, -apple-system, sans-serif" }}
    >
      {/* background gradient */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div
          className="absolute top-[-100px] right-[-0px] w-[700px] h-[700px] rounded-full blur-[140px]"
          style={{
            background:
              "radial-gradient(circle, rgba(67, 146, 112, 0.3) 90%, rgba(5, 93, 62, 0.1) 80%, transparent 0%)",
          }}
        />
      </div>
  
     
      <div
        className={`flex flex-col transition-all duration-500 ${
          result
            ? "justify-start pt-16"
            : "justify-center items-center min-h-screen"
        }`}
      >
        
        <div
          className={`w-full px-4 transition-all duration-500 ${
            result ? "max-w-3xl mx-auto" : "max-w-2xl text-center"
          }`}
        >
          {/* Header */}
          <div className={`mb-10 transition-all duration-500 ${result ? "text-left" : "text-center"}`}>
            <h1 className="text-3xl text-center font-semibold tracking-tight bg-gradient-to-r from-green-900 via-emerald-700 to-green-800 bg-clip-text text-transparent">
              Smart Research Analysis
            </h1>
  
            <p className={`text-l mt-4 text-muted-foreground text-center text-base ${result ? "" : "mx-auto"}`}>
              Save hours of manual review by instantly assessing a paper’s consistency, <br></br> factual accuracy, and originality.
            </p>
          </div>
  
          {/* Input */}
          <div className={`flex gap-3 mb-12 ${result ? "" : "justify-center"}`}>
            <div className="relative flex-1 max-w-xl">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter Arxiv URL "
                className="pl-10 h-12 bg-card/80 backdrop-blur-sm border-border/60 text-foreground placeholder:text-muted-foreground focus-visible:ring-primary/30"
                onKeyDown={(e) => e.key === "Enter" && handleEvaluate()}
              />
            </div>
  
            <Button
              onClick={handleEvaluate}
              disabled={loading || !url.trim()}
              className={`h-12 px-6 font-semibold text-white flex items-center gap-2
                bg-gradient-to-r from-emerald-800 via-emerald-700 to-emerald-700
                hover:from-emerald-700 hover:via-emerald-600 hover:to-emerald-600
                transition-all duration-200 shadow-md hover:shadow-lg
                ${loading ? "animate-pulse cursor-not-allowed opacity-90" : ""}
              `}
            >
              {loading ? (
                <>
                  <span className="animate-bounce">⚡</span>
                  <span>Analyzing...</span>
                </>
              ) : (
                "Evaluate"
              )}
            </Button>
          </div>
  
          {/* Results */}
          {result && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Title Card with Pass Badge & Download */}
              <Card className="p-5 border-border/60 shadow-sm bg-card/80 backdrop-blur-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <FileText className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                    <div className="min-w-0">
                      <h2 className="text-lg font-bold text-foreground leading-snug">{result.title}</h2>
                      <p className="text-xs text-muted-foreground mt-1">{result.source}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold ${result.pass ? 'bg-primary/10 text-primary' : 'bg-destructive/10 text-destructive'}`}>
                      <ShieldCheck className="h-4 w-4" />
                      {result.pass ? "PASS" : "FAIL"}
                    </div>
                    <Button onClick={handleDownloadPDF} size="sm" variant="outline" className="gap-1.5 border-primary/30 text-primary hover:bg-primary/5 text-xs">
                    <Download className="h-3.5 w-3.5" />
                    PDF
                  </Button>
                  </div>
                </div>
              </Card>

              {/* Executive Summary */}
              <Card className="p-5 border-border/60 shadow-sm bg-card/80 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-1 h-4 rounded-full bg-primary" />
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Executive Summary</h3>
                </div>
                <p className="text-sm leading-relaxed text-foreground">{result.executive_summary}</p>
              </Card>

              {/* Scores Row */}
              <div className="grid grid-cols-3 gap-4">

                {/* Consistency */}
                <Card className="p-5 border-border/60 bg-card/80">
                  <h3 className="text-xs uppercase text-muted-foreground mb-2">Consistency</h3>

                  <div className="flex items-center justify-between mb-2">
                    <span className="text-3xl font-bold">{result.consistency_score}</span>
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded ${
                        result.consistency_score > 80
                          ? "bg-green-100 text-green-700"
                          : result.consistency_score > 60
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {result.consistency_score > 80
                        ? "Strong"
                        : result.consistency_score > 60
                        ? "Moderate"
                        : "Weak"}
                    </span>
                  </div>

                  <Progress value={result.consistency_score} className="h-2 mt-2" />

                  <p className="text-xs text-muted-foreground mt-2">
                    Measures alignment between methodology and results
                  </p>
                </Card>

                {/* Grammar */}
                <Card className="p-5 border-border/60 bg-card/80">
                  <h3 className="text-xs uppercase text-muted-foreground mb-2">Grammar</h3>

                  <div
                    className={`inline-block px-3 py-1.5 rounded-md text-sm font-semibold ${
                      result.grammar_rating === "high"
                        ? "bg-green-100 text-green-700"
                        : result.grammar_rating === "medium"
                        ? "bg-orange-100 text-orange-700"
                        : "bg-red-100 text-red-600"
                    }`}
                  >
                    {result.grammar_rating.toUpperCase()}
                  </div>

                  <p className="text-xs text-muted-foreground mt-3">
                    Language quality assessment
                  </p>
                </Card>

                {/* Authenticity */}
                <Card className="p-5 border-border/60 bg-card/80">
                  <h3 className="text-xs uppercase text-muted-foreground mb-2">Authenticity</h3>

                  <div className="flex items-center justify-between mb-2">
                    <span className="text-3xl font-bold">
                      {Math.round(result.authenticity_score * 100)}
                    </span>

                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded ${
                        result.authenticity_score > 0.85
                          ? "bg-green-100 text-green-700"
                          : result.authenticity_score > 0.6
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {result.authenticity_score > 0.85
                        ? "High"
                        : result.authenticity_score > 0.6
                        ? "Moderate"
                        : "Low"}
                    </span>
                  </div>

                  <Progress value={result.authenticity_score * 100} className="h-2 mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">
                    Percentage of authenticity
                  </p>
                </Card>

              </div>

              {/*Novelty Row */}
              <Card className="p-5 border-border/60 bg-card/80">
                <h3 className="text-xs uppercase text-muted-foreground mb-3">Novelty</h3>

                <div className="prose prose-sm max-w-none text-foreground">
                  <ReactMarkdown>
                    {result.novelty}
                  </ReactMarkdown>
                </div>
              </Card>

              {/* Fact-Check List */}
              <Card className="p-5 border-border/60 bg-card/80">
                <h3 className="text-xs uppercase text-muted-foreground mb-4">
                  Verified Claims
                </h3>

                <div className="space-y-3">
                  {result.fact_check?.length > 0 ? (
                    result.fact_check.map((f, i) => (
                      <div className="flex items-start gap-3">
                        <div key={i} className="flex-shrink-0 mt-1">
                          {f.verified ? (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-500" />
                          )}
                        </div>

                        <p className="text-sm leading-relaxed text-gray-800">
                          {f.claim}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      No verified claims available
                    </p>
                  )}
                </div>
              </Card>

              <div className="h-8" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Index;
