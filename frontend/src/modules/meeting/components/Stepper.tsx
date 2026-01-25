"use client";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type StepStatus = "waiting" | "loading" | "completed";

interface StepItem {
  id: string;
  label: string;
  status: StepStatus;
}

interface MeetingStepperProps {
  steps: StepItem[];
  currentStep?: number;
}

export function MeetingStepper({ steps, currentStep }: MeetingStepperProps) {
  return (
    <div className="flex flex-col gap-4 w-full max-w-xs bg-white p-4 rounded-xl border shadow-sm">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
        执行工作流
      </h3>
      <div className="space-y-4">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-3">
            {step.status === "completed" && (
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            )}
            {step.status === "loading" && (
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            )}
            {step.status === "waiting" && (
              <Circle className="w-5 h-5 text-slate-300" />
            )}

            <span
              className={cn(
                "text-sm font-medium",
                step.status === "waiting" ? "text-slate-400" : "text-slate-700",
              )}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
