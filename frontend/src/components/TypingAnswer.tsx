import { useEffect, useRef, useState } from 'react';

interface TypingAnswerProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
}

export function TypingAnswer({ text, speed = 12, onComplete }: TypingAnswerProps) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    if (!text) {
      setDisplayed('');
      setDone(true);
      onCompleteRef.current?.();
      return;
    }
    setDisplayed('');
    setDone(false);
    let i = 0;
    const timer = setInterval(() => {
      if (i >= text.length) {
        clearInterval(timer);
        setDone(true);
        onCompleteRef.current?.();
        return;
      }
      setDisplayed(text.slice(0, i + 1));
      i++;
    }, 1000 / speed);
    return () => clearInterval(timer);
  }, [text, speed]); // Don't include onComplete - prevents re-run on parent re-renders

  return (
    <div className="text-stone-700 leading-relaxed whitespace-pre-wrap">
      {displayed}
      {!done && <span className="animate-pulse">|</span>}
    </div>
  );
}
