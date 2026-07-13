import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, File, X, Sparkles, Check, Loader2, ArrowRight, Shield, Zap, FileText } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { API_BASE_URL } from "@/services/api";

const PIPELINE_STAGES = [
  { id: 1, label: "Document Ingest & Type Detection", desc: "PyMuPDF analyzing layout types" },
  { id: 2, label: "OCR Text Extraction", desc: "PaddleOCR engine parsing scanned pixels" },
  { id: 3, label: "Generative AI Semantic Mapping", desc: "Gemini structuring raw text fields" },
  { id: 4, label: "Deterministic Policy Verification", desc: "Validating vendor matching & mathematical equations" }
];

export default function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeStage, setActiveStage] = useState(0);
  const [uploadResult, setUploadResult] = useState<any>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;
    
    setIsProcessing(true);
    setActiveStage(1);
    
    const formData = new FormData();
    formData.append("file", file);

    // Simulate stepping through stages for visual demo effect
    const stageIntervals = [1200, 2000, 2500, 1000];
    
    let currentStage = 1;
    const runStages = () => {
      if (currentStage < 4) {
        setTimeout(() => {
          currentStage += 1;
          setActiveStage(currentStage);
          runStages();
        }, stageIntervals[currentStage - 1]);
      }
    };
    runStages();

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/invoices/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) throw new Error("Upload failed");
      
      const data = await response.json();
      
      // Keep displaying success validation state briefly before redirect
      setTimeout(() => {
        toast.success("Validation pipeline completed successfully");
        setUploadResult(data);
      }, 7000); // match total simulation time approximately
      
    } catch (error) {
      console.error(error);
      toast.error("Pipeline crashed during processing");
      setIsProcessing(false);
      setActiveStage(0);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
          Upload Center
        </h2>
        <p className="text-sm text-slate-400 mt-1.5 flex items-center gap-1.5 font-medium">
          <Sparkles className="w-4 h-4 text-primary animate-pulse" />
          Ingest new documents into the autonomous policy matching loop
        </p>
      </div>

      <div className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-8 shadow-xl relative overflow-hidden backdrop-blur-md">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/2 filter blur-3xl pointer-events-none" />

        <AnimatePresence mode="wait">
          {!isProcessing ? (
            <motion.div
              key="dropzone"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {!file ? (
                <div 
                  {...getRootProps()} 
                  className={`border-2 border-dashed rounded-2xl p-16 text-center transition-all cursor-pointer flex flex-col items-center justify-center min-h-[350px] relative overflow-hidden group ${
                    isDragActive 
                      ? "border-primary bg-primary/5 scale-[1.01] shadow-[0_0_30px_-5px_rgba(168,85,247,0.25)]" 
                      : "border-slate-800 hover:border-primary/40 hover:bg-slate-900/10"
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className={`p-4.5 rounded-2xl bg-slate-900/60 border border-slate-800 text-primary mb-5 group-hover:scale-110 group-hover:border-primary/30 transition-all duration-300 ${isDragActive ? "animate-bounce" : ""}`}>
                    <UploadCloud className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">
                    {isDragActive ? "Drop documents here" : "Drag & drop files here"}
                  </h3>
                  <p className="text-slate-400 text-sm max-w-sm mb-6 leading-relaxed">
                    Select a single PDF, JPEG, or PNG invoice. Max size 10MB.
                  </p>
                  <button className="h-11 px-7 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-all shadow-lg hover:shadow-primary/20">
                    Browse File
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="flex items-center gap-4.5 p-5 border border-slate-850 rounded-2xl bg-slate-950/40 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-primary/2 filter blur-2xl pointer-events-none" />
                    <div className="w-14 h-14 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0 border border-primary/20">
                      <File className="w-6.5 h-6.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-white truncate">{file.name}</p>
                      <p className="text-xs text-slate-400 font-medium mt-0.5">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <button 
                      onClick={() => setFile(null)}
                      className="p-2.5 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-rose-400 transition-colors shrink-0"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="flex justify-end gap-3 pt-6 border-t border-slate-800/60">
                    <button 
                      onClick={() => setFile(null)}
                      className="h-11 px-5 rounded-xl border border-slate-850 text-slate-300 text-sm font-semibold hover:bg-slate-900 transition-colors"
                    >
                      Reset
                    </button>
                    <button 
                      onClick={handleUpload}
                      className="h-11 px-8 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-all shadow-lg hover:shadow-primary/20 flex items-center gap-2"
                    >
                      Start Ingest Pipeline
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          ) : uploadResult ? (
            <motion.div
              key="summary"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="py-4"
            >
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <Check className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Pipeline Complete</h3>
                    <p className="text-sm text-slate-400">Document successfully ingested and validated.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-850">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-primary" /> Type
                    </div>
                    <div className="font-bold text-white text-sm">{uploadResult.pipeline_summary?.document_type || "Digital"}</div>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-850">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-primary" /> Fields
                    </div>
                    <div className="font-bold text-white text-sm">{uploadResult.pipeline_summary?.fields_extracted || 0} extracted</div>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-850">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1 flex items-center gap-1.5">
                      <Shield className="w-3.5 h-3.5 text-primary" /> Rules
                    </div>
                    <div className="font-bold text-white text-sm">
                      <span className="text-emerald-400">{uploadResult.pipeline_summary?.rules_passed || 0}✓</span> / <span className="text-rose-400">{uploadResult.pipeline_summary?.rules_failed || 0}✗</span>
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-850">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1 flex items-center gap-1.5">
                      <Check className="w-3.5 h-3.5 text-primary" /> Decision
                    </div>
                    <div className="font-bold text-white text-sm truncate">{uploadResult.pipeline_summary?.decision || "N/A"}</div>
                  </div>
                </div>

                <div className="flex justify-end gap-3">
                  <button 
                    onClick={() => {
                      setUploadResult(null);
                      setFile(null);
                      setIsProcessing(false);
                      setActiveStage(0);
                    }}
                    className="h-11 px-5 rounded-xl border border-slate-800 text-slate-300 text-sm font-semibold hover:bg-slate-800/50 transition-colors"
                  >
                    Upload Another
                  </button>
                  <button 
                    onClick={() => navigate(`/invoice/${uploadResult.data.id}`)}
                    className="h-11 px-6 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-all flex items-center gap-2 shadow-lg hover:shadow-primary/20"
                  >
                    View Details Report
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="pipeline"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="py-6 space-y-8"
            >
              <div className="text-center max-w-md mx-auto space-y-3">
                <div className="inline-flex p-3 bg-primary/10 rounded-2xl text-primary border border-primary/20 mb-2">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
                <h3 className="text-xl font-bold text-white">Running Policy Pipeline</h3>
                <p className="text-xs text-slate-400 leading-normal">
                  Our hybrid processing engine is validating the document. Each stage must pass code validations.
                </p>
              </div>

              {/* Progress Stepper */}
              <div className="max-w-xl mx-auto space-y-4">
                {PIPELINE_STAGES.map((stage) => {
                  const isDone = activeStage > stage.id;
                  const isActive = activeStage === stage.id;

                  return (
                    <div 
                      key={stage.id} 
                      className={`flex items-start gap-4 p-4.5 rounded-2xl border transition-all duration-300 ${
                        isActive 
                          ? "bg-slate-900/60 border-primary/30 glow-primary scale-[1.01]" 
                          : isDone 
                            ? "bg-slate-950/20 border-emerald-500/10 opacity-70"
                            : "bg-slate-950/20 border-slate-850 opacity-40"
                      }`}
                    >
                      <div className="mt-0.5 shrink-0">
                        {isDone ? (
                          <div className="w-6 h-6 rounded-full bg-emerald-500/15 border border-emerald-500/35 text-emerald-400 flex items-center justify-center">
                            <Check className="w-3.5 h-3.5" />
                          </div>
                        ) : isActive ? (
                          <div className="w-6 h-6 rounded-full bg-primary/15 border border-primary/35 text-primary flex items-center justify-center">
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          </div>
                        ) : (
                          <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-slate-400 text-xs font-bold flex items-center justify-center">
                            {stage.id}
                          </div>
                        )}
                      </div>
                      <div>
                        <div className={`text-sm font-bold ${isActive ? "text-white" : isDone ? "text-slate-300" : "text-slate-500"}`}>
                          {stage.label}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1 font-medium leading-relaxed">
                          {stage.desc}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
