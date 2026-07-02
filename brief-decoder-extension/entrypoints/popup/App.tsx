import { useState } from 'react';
import BriefForm from './components/BriefForm';
import ResultView from './components/ResultView';
import ErrorView from './components/ErrorView';
import { decodeBrief } from './lib/api';
import type { DecodeBriefResponse } from './lib/types';

type Status = 'idle' | 'loading' | 'success' | 'error';

export default function App() {
  const [text, setText] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [response, setResponse] = useState<DecodeBriefResponse | null>(null);

  async function handleRun() {
    setStatus('loading');
    const res = await decodeBrief(text); // never throws, see lib/api.ts
    setResponse(res);
    setStatus(res.status === 'succeeded' ? 'success' : 'error');
  }

  function handleRetry() {
    setStatus('idle');
    setResponse(null);
    // text intentionally kept — user shouldn't retype the brief after a failure
  }

  function handleNewBrief() {
    setStatus('idle');
    setResponse(null);
    setText('');
  }

  function handleCopy() {
    if (response?.result) {
      navigator.clipboard.writeText(JSON.stringify(response.result, null, 2));
    }
  }

  return (
    <div className="w-[380px] overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-gray-100 px-4 py-3">
        <div className="flex h-6 w-6 items-center justify-center rounded bg-gray-900">
          <span className="text-xs font-semibold text-white">B</span>
        </div>
        <span className="text-sm font-medium text-gray-900">AI Brief Decoder</span>
      </div>

      <div className="p-4">
        {(status === 'idle' || status === 'loading') && (
          <BriefForm
            value={text}
            onChange={setText}
            onSubmit={handleRun}
            isLoading={status === 'loading'}
          />
        )}
        {status === 'success' && response?.result && (
          <ResultView result={response.result} onCopy={handleCopy} onReset={handleNewBrief} />
        )}
        {status === 'error' && response?.error && (
          <ErrorView error={response.error} onRetry={handleRetry} />
        )}
      </div>
    </div>
  );
}
