import { useState } from "react";

type StepStatus = "waiting" | "loading" | "completed";

export function useMeeting() {
  const [currentStep, setCurrentStep] = useState(0);
  const [content, setContent] = useState("");
  const [isStarted, setIsStarted] = useState(false);

  function getStatus(index: number): StepStatus {
    if (currentStep > index) return "completed";
    if (currentStep === index && isStarted) return "loading";
    return "waiting";
  }

  const steps = [
    { id: "1", label: "音视频切片转录 (2.1.1)", status: getStatus(0) },
    { id: "2", label: "语义角色标注 (2.1.2)", status: getStatus(1) },
    { id: "3", label: "核心议程提取 (2.1.3)", status: getStatus(2) },
    { id: "4", label: "生成纪要文档 (2.1.4)", status: getStatus(3) },
  ];

  const startWorkflow = async () => {
    setIsStarted(true);

    // 模拟每一步的耗时
    for (let i = 0; i < 3; i++) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setCurrentStep((prev) => prev + 1);
    }

    // 最后一步开始流式出字
    simulateStreaming();
  };

  const simulateStreaming = () => {
    const text =
      "# 会议纪要\n\n- **时间**: 2026-01-25\n- **结论**: 架构迁移完成...";
    let j = 0;
    const timer = setInterval(() => {
      setContent((prev) => prev + text[j]);
      j++;
      if (j >= text.length - 1) {
        clearInterval(timer);
        setCurrentStep(4); // 全部完成
      }
    }, 30);
  };

  return { steps, content, startWorkflow, isStarted, currentStep };
}
