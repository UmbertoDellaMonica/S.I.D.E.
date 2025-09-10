import { useState, useRef, useEffect } from "react";

interface DraggableButtonProps {
  onClick: () => void;
  containerRef: React.RefObject<HTMLDivElement>;
  children: React.ReactNode;
}

export function DraggableButton({
  onClick,
  containerRef,
  children,
}: DraggableButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 10 });
  const [dragging, setDragging] = useState(false);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  // Posiziona inizialmente in alto a destra
  useEffect(() => {
    if (containerRef.current && buttonRef.current) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const buttonRect = buttonRef.current.getBoundingClientRect();
      setPosition({
        x: containerRect.width - buttonRect.width - 10, // 10px margin
        y: 10,
      });
    }
  }, [containerRef]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (buttonRef.current) {
      setDragging(true);
      const rect = buttonRef.current.getBoundingClientRect();
      setOffset({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (dragging && containerRef.current && buttonRef.current) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const buttonRect = buttonRef.current.getBoundingClientRect();

      let newX = e.clientX - containerRect.left - offset.x;
      let newY = e.clientY - containerRect.top - offset.y;

      // vincolo all’interno del container
      newX = Math.max(
        0,
        Math.min(newX, containerRect.width - buttonRect.width)
      );
      newY = Math.max(
        0,
        Math.min(newY, containerRect.height - buttonRect.height)
      );

      setPosition({ x: newX, y: newY });
    }
  };

  const handleMouseUp = () => setDragging(false);

  useEffect(() => {
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [dragging, offset]);

  return (
    <button
      ref={buttonRef}
      onMouseDown={handleMouseDown}
      onClick={onClick}
      style={{
        position: "absolute",
        left: position.x,
        top: position.y,
        cursor: dragging ? "grabbing" : "grab",
      }}
      className="px-3 py-1 text-sm rounded bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-semibold hover:scale-105 transition-transform"
    >
      {children}
    </button>
  );
}
