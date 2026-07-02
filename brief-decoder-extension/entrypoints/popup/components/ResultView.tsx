import { Check, Copy, RotateCcw } from 'lucide-react';
import { useState } from 'react';
import type { BriefDecodeResult, RiskItem } from '../lib/types';

interface ResultViewProps {
  result: BriefDecodeResult;
  onCopy: () => void;
  onReset: () => void;
}

const SEVERITY_STYLES: Record<RiskItem['severity'], string> = {
  low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  medium: 'bg-amber-50 text-amber-700 border-amber-200',
  high: 'bg-red-50 text-red-700 border-red-200',
};

function Section({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <div className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-400">{title}</div>
      <ul className="list-inside list-disc space-y-1 text-sm text-gray-800">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ResultView({ result, onCopy, onReset }: ResultViewProps) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="max-h-[420px] space-y-3 overflow-y-auto pr-1">
      <div>
        <div className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-400">Summary</div>
        <p className="text-sm text-gray-800">{result.summary}</p>
      </div>

      <Section title="Goals" items={result.goals} />
      <Section title="Deliverables" items={result.deliverables} />
      <Section title="Constraints" items={result.constraints} />

      {result.risks.length > 0 && (
        <div>
          <div className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-400">Risks</div>
          <div className="space-y-1.5">
            {result.risks.map((risk, i) => (
              <div key={i} className={`rounded-md border p-2 text-xs ${SEVERITY_STYLES[risk.severity]}`}>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{risk.risk}</span>
                  <span className="shrink-0 text-[10px] font-semibold uppercase">{risk.severity}</span>
                </div>
                <div className="mt-0.5 opacity-80">{risk.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <Section title="Clarifying questions" items={result.clarifying_questions} />

      <div className="rounded-md border border-gray-200 bg-gray-50 p-2.5">
        <div className="mb-1 text-xs font-medium uppercase tracking-wide text-gray-400">Next action</div>
        <p className="text-sm text-gray-800">{result.recommended_next_action}</p>
      </div>

      <div className="flex gap-2 pt-1">
        <button
          type="button"
          className="flex flex-1 items-center justify-center gap-2 rounded-md border border-gray-200 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          onClick={handleCopy}
        >
          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          {copied ? 'Copied' : 'Copy result'}
        </button>
        <button
          type="button"
          className="flex flex-1 items-center justify-center gap-2 rounded-md border border-gray-200 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          onClick={onReset}
        >
          <RotateCcw className="h-4 w-4" />
          New brief
        </button>
      </div>
    </div>
  );
}
