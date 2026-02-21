import { useState } from 'react';
import { TypingAnswer } from './TypingAnswer';
import { SourceCitations } from './SourceCitations';
import { ThinkingLoader } from './ThinkingLoader';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content?: string;
  sources?: string[];
  isLoading?: boolean;
  useTypingEffect?: boolean;
  onTypingComplete?: () => void;
}

export function ChatMessage({
  role,
  content = '',
  sources = [],
  isLoading,
  useTypingEffect,
  onTypingComplete,
}: ChatMessageProps) {
  if (role === 'user') {
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-[80%] rounded-2xl bg-stone-800 text-white px-4 py-3 shadow-sm">
          <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{content}</p>
        </div>
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-stone-600 flex items-center justify-center mt-1">
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
          </svg>
        </div>
      </div>
    );
  }

  const [typingDone, setTypingDone] = useState(false);

  // Once typing is done, show static content forever (no re-animation on new messages)
  const showStatic = typingDone || !useTypingEffect;

  return (
    <div className="flex justify-start gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center mt-1">
        <svg className="w-4 h-4 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z" />
        </svg>
      </div>
      <div className="flex-1 min-w-0 rounded-2xl bg-white border border-stone-200/80 px-5 py-4 shadow-sm hover:shadow-md transition-shadow">
        {isLoading && <ThinkingLoader />}
        {!isLoading && content && showStatic && (
          <>
            <div className="text-stone-700 leading-relaxed whitespace-pre-wrap text-[15px]">
              {content}
            </div>
            <SourceCitations sources={sources} />
          </>
        )}
        {!isLoading && content && !showStatic && (
          <TypingAnswer
            text={content}
            speed={45}
            onComplete={() => {
              setTypingDone(true);
              onTypingComplete?.();
            }}
          />
        )}
      </div>
    </div>
  );
}
