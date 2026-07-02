import { Loader2, Play } from 'lucide-react';

interface BriefFormProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

// Controlled component with no internal state — text/status live in App (lifting
// state up), since App is what needs to react to submit and drive the request.
export default function BriefForm({ value, onChange, onSubmit, isLoading }: BriefFormProps) {
  const submitDisabled = !value.trim() || isLoading;

  return (
    <div className="space-y-3">
      <textarea
        id="brief-text"
        name="brief-text"
        className="w-full resize-none rounded-md border border-gray-200 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 disabled:bg-gray-50 disabled:text-gray-400"
        placeholder="Paste a client brief here..."
        rows={6}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={isLoading}
      />
      <button
        type="button"
        className="flex w-full items-center justify-center gap-2 rounded-md bg-gray-900 py-2 text-sm font-medium text-white transition-colors disabled:bg-gray-200 disabled:text-gray-400"
        onClick={onSubmit}
        disabled={submitDisabled}
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Decoding...
          </>
        ) : (
          <>
            <Play className="h-4 w-4" />
            Run
          </>
        )}
      </button>
    </div>
  );
}
