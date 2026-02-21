import { useState, useRef, useEffect } from 'react';
import { sendQuery } from './api';
import { ChatMessage } from './components/ChatMessage';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: string[];
  isLoading?: boolean;
  useTypingEffect?: boolean;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || isSubmitting) return;

    setInput('');
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: q,
      sources: [],
    };
    setMessages((prev) => [...prev, userMsg]);

    const assistantId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      {
        id: assistantId,
        role: 'assistant',
        content: '',
        sources: [],
        isLoading: true,
      },
    ]);
    setIsSubmitting(true);

    try {
      const res = await sendQuery(q);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: res.answer,
                sources: res.sources,
                isLoading: false,
                useTypingEffect: true,
              }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: `Error: ${err instanceof Error ? err.message : 'Request failed'}`,
                sources: [],
                isLoading: false,
                useTypingEffect: false,
              }
            : m
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex h-screen bg-stone-100">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-stone-900 text-white flex flex-col shadow-lg">
        <div className="p-5 border-b border-stone-700">
          <h1 className="font-bold text-base tracking-tight">LegalMind</h1>
          <p className="text-xs text-stone-400 mt-1">Knowledge Base</p>
        </div>
        <div className="p-3">
          <button
            onClick={() => setMessages([])}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white px-4 py-2.5 text-sm font-medium transition-colors shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0 bg-white/50">
        <header className="flex-shrink-0 border-b border-stone-200/80 bg-white/90 backdrop-blur px-6 py-4">
          <h2 className="text-lg font-semibold text-stone-800">Chat</h2>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-2xl mx-auto space-y-8">
            {messages.length === 0 && (
              <div className="text-center py-20">
                <div className="w-16 h-16 rounded-2xl bg-amber-100 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-stone-700">Ask about your documents</p>
                <p className="text-sm text-stone-500 mt-1">Legal documents are indexed and searchable</p>
              </div>
            )}
            {messages.map((m) => (
              <ChatMessage
                key={m.id}
                role={m.role}
                content={m.content}
                sources={m.sources}
                isLoading={m.isLoading}
                useTypingEffect={m.useTypingEffect}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="flex-shrink-0 border-t border-stone-200/80 bg-white px-6 py-5"
        >
          <div className="max-w-2xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about contracts, liability, or legal terms..."
              disabled={isSubmitting}
              className="w-full rounded-xl border border-stone-300 px-4 py-3.5 text-stone-900 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-400 disabled:opacity-60 disabled:cursor-not-allowed shadow-sm"
            />
            <p className="text-xs text-stone-400 mt-2">
              AI responses are generated from your indexed documents.
            </p>
          </div>
        </form>
      </main>
    </div>
  );
}
