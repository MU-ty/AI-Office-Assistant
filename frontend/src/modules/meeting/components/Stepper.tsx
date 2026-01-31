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
    <div className="space-y-3">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-start gap-3">
          <div className="flex flex-col items-center">
            {step.status === "completed" && (
              <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4 text-white" />
              </div>
            )}
            {step.status === "loading" && (
              <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-white animate-spin" />
              </div>
            )}
            {step.status === "waiting" && (
              <div className="w-6 h-6 rounded-full border-2 border-slate-300 bg-white" />
            )}
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "w-0.5 h-8 mt-1",
                  step.status === "completed" ? "bg-green-500" : "bg-slate-200",
                )}
              />
            )}
          </div>

          <div className="flex-1 pt-0.5">
            <span
              className={cn(
                "text-sm font-medium block",
                step.status === "waiting" ? "text-slate-400" : "text-slate-700",
              )}
            >
              {step.label}
            </span>
            {step.status === "loading" && (
              <span className="text-xs text-blue-600 mt-1 block">
                进行中...
              </span>
            )}
            {step.status === "completed" && (
              <span className="text-xs text-green-600 mt-1 block">已完成</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
