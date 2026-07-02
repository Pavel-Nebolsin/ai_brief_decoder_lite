import { AlertTriangle, RotateCcw } from 'lucide-react';
import type { SafeError } from '../lib/types';

interface ErrorViewProps {
  error: SafeError;
  onRetry: () => void;
}

export default function ErrorView({ error, onRetry }: ErrorViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />
        <div className="min-w-0">
          <div className="font-mono text-xs text-red-700">{error.code}</div>
          <div className="mt-0.5 text-sm text-red-700">{error.message}</div>
        </div>
      </div>
      <button
        type="button"
        className="flex w-full items-center justify-center gap-2 rounded-md border border-gray-200 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        onClick={onRetry}
      >
        <RotateCcw className="h-4 w-4" />
        Try again
      </button>
    </div>
  );
}
