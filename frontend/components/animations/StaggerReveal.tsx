"use client";

import { useEffect, useRef, useState, ReactNode, Children, cloneElement, isValidElement } from "react";

interface StaggerRevealProps {
  children: ReactNode;
  stagger?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  distance?: number;
  duration?: number;
  delay?: number;
  easing?: string;
  threshold?: number;
  once?: boolean;
  className?: string;
}

const dirMap: Record<string, { x: number; y: number }> = {
  up: { x: 0, y: 1 },
  down: { x: 0, y: -1 },
  left: { x: 1, y: 0 },
  right: { x: -1, y: 0 },
  none: { x: 0, y: 0 },
};

export default function StaggerReveal({
  children,
  stagger = 0.08,
  direction = "up",
  distance = 40,
  duration = 0.6,
  delay = 0,
  easing = "cubic-bezier(0.16, 1, 0.3, 1)",
  threshold = 0.1,
  once = true,
  className = "",
}: StaggerRevealProps) {
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once && containerRef.current) {
            observer.unobserve(containerRef.current);
          }
        } else if (!once) {
          setIsVisible(false);
        }
      },
      { threshold }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [threshold, once]);

  const dir = dirMap[direction] || dirMap.up;
  const tx = dir.x * distance;
  const ty = dir.y * distance;

  const items = Children.toArray(children);

  return (
    <div ref={containerRef} className={className}>
      {items.map((child, i) => (
        <div
          key={i}
          style={{
            opacity: isVisible ? 1 : 0,
            transform: isVisible
              ? "translate(0, 0) scale(1)"
              : `translate(${tx}px, ${ty}px) scale(0.95)`,
            transition: `opacity ${duration}s ${easing} ${delay + i * stagger}s, transform ${duration}s ${easing} ${delay + i * stagger}s`,
            willChange: "opacity, transform",
          }}
        >
          {child}
        </div>
      ))}
    </div>
  );
}
