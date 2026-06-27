"use client";
export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <p className="text-4xl mb-4">🧂</p>
      <h2 className="text-xl font-bold mb-2">Something went wrong</h2>
      <p className="text-salt-500 mb-6">The AI pipeline may be warming up. Try again.</p>
      <button onClick={reset} className="px-6 py-3 bg-umami-400 text-white rounded-xl font-semibold">
        Try Again
      </button>
    </div>
  );
}
