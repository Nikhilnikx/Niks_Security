"use client";

import { useEffect, useRef, useState, useMemo } from "react";

interface SplitTextProps {
  text: string;
  className?: string;
  delay?: number;
  speed?: number;
  splitBy?: "characters" | "words" | "lines";
  staggerChildren?: number;
  threshold?: number;
  once?: boolean;
  onLetterAnimationComplete?: () => void;
  style?: React.CSSProperties;
}

interface CharProps {
  char: string;
  index: number;
  isVisible: boolean;
  delay: number;
  speed: number;
}

const Char = ({ char, index, isVisible, delay, speed }: CharProps) => {
  return (
    <span
      className="inline-block"
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? "translateY(0) rotateX(0)" : "translateY(40px) rotateX(-90deg)",
        transition: `opacity ${speed}s ease-out ${delay}s, transform ${speed}s ease-out ${delay}s`,
        transformOrigin: "bottom center",
      }}
    >
      {char === " " ? "\u00A0" : char}
    </span>
  );
};

const SplitText = ({
  text,
  className = "",
  delay = 0,
  speed = 0.4,
  splitBy = "characters",
  staggerChildren = 0.03,
  threshold = 0.1,
  once = true,
  onLetterAnimationComplete,
  style,
}: SplitTextProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once && elementRef.current) {
            observer.unobserve(elementRef.current);
          }
        } else if (!once) {
          setIsVisible(false);
        }
      },
      { threshold }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, [threshold, once]);

  useEffect(() => {
    if (isVisible && onLetterAnimationComplete) {
      const totalChars = text.length;
      const totalTime = delay + totalChars * staggerChildren + speed;
      const timer = setTimeout(onLetterAnimationComplete, totalTime * 1000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, text, delay, staggerChildren, speed, onLetterAnimationComplete]);

  const items = useMemo(() => {
    if (splitBy === "words") {
      return text.split(" ").map((word, i) => ({
        text: word,
        index: i,
        isSpace: false,
      }));
    }
    return text.split("").map((char, i) => ({
      text: char,
      index: i,
      isSpace: char === " ",
    }));
  }, [text, splitBy]);

  if (splitBy === "words") {
    return (
      <div ref={elementRef} className={className} style={style}>
        {items.map((item, i) => (
          <span key={i} className="inline-block">
            <span
              className="inline-block"
              style={{
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? "translateY(0)" : "translateY(30px)",
                transition: `opacity ${speed}s ease-out ${delay + i * staggerChildren}s, transform ${speed}s ease-out ${delay + i * staggerChildren}s`,
              }}
            >
              {item.text}
            </span>
            {i < items.length - 1 && <span>&nbsp;</span>}
          </span>
        ))}
      </div>
    );
  }

  return (
    <div ref={elementRef} className={className} style={style}>
      {items.map((item, i) => (
        <Char
          key={i}
          char={item.text}
          index={i}
          isVisible={isVisible}
          delay={delay + i * staggerChildren}
          speed={speed}
        />
      ))}
    </div>
  );
};

export default SplitText;
