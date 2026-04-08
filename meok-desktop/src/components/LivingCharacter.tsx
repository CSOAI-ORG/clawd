/**
 * LivingCharacter — The MEOK OS AI companion that floats on your desktop
 *
 * A living, breathing character that:
 * - Shows Jarvis (analytical) or Sophie (warm) based on SOV3 persona
 * - Reacts to emotions in real-time
 * - Lip-syncs when speaking
 * - Shows thought bubbles
 * - Pulses when listening
 * - Spins when thinking
 * - Displays tool use status
 *
 * Connected to SOV3 via WebSocket character bridge.
 */

import { useState, useEffect } from "react";
import type { CharacterState } from "../hooks/useCharacterBridge";

interface Props {
  state: CharacterState;
  size?: number;
  onClick?: () => void;
}

// Emotion → color mapping
const EMOTION_COLORS: Record<string, string> = {
  neutral: "#60B8F0",    // MEOK sky blue
  excited: "#FFD700",    // Gold
  tired: "#8B7EC8",      // Soft purple
  stressed: "#FF6B6B",   // Warm red
  curious: "#50C878",    // Emerald
  caring: "#FF69B4",     // Pink
  focused: "#4A90D9",    // Deep blue
  playful: "#FFA500",    // Orange
};

// Persona → face style
const PERSONA_STYLES = {
  jarvis: {
    eyeColor: "#4A90D9",
    faceRadius: "42%",
    borderWidth: 3,
    mouthCurve: 0.1,  // Slight, professional
  },
  sophie: {
    eyeColor: "#9B59B6",
    faceRadius: "48%",
    borderWidth: 2,
    mouthCurve: 0.3,  // Warmer, more expressive
  },
};

export function LivingCharacter({ state, size = 80, onClick }: Props) {
  const [breathPhase, setBreathPhase] = useState(0);
  const [blinkTimer, setBlinkTimer] = useState(0);
  const [isBlinking, setIsBlinking] = useState(false);
  const [thoughtVisible, setThoughtVisible] = useState(false);
  const [irisOffset, setIrisOffset] = useState({ x: 0, y: 0 });

  const style = PERSONA_STYLES[state.persona] || PERSONA_STYLES.jarvis;
  const emotionColor = EMOTION_COLORS[state.emotion] || EMOTION_COLORS.neutral;
  const scale = size / 80;

  // Breathing animation
  useEffect(() => {
    const speed = state.thinking ? 800 : state.speaking ? 1200 : 2000;
    const interval = setInterval(() => {
      setBreathPhase(p => (p + 1) % 360);
    }, speed / 60);
    return () => clearInterval(interval);
  }, [state.thinking, state.speaking]);

  // Blink randomly
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() < 0.1) {
        setIsBlinking(true);
        setTimeout(() => setIsBlinking(false), 150);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  // Show thought bubble when speaking
  useEffect(() => {
    if (state.speaking && state.lastText) {
      setThoughtVisible(true);
      const timer = setTimeout(() => setThoughtVisible(false), 8000);
      return () => clearTimeout(timer);
    }
  }, [state.speaking, state.lastText]);

  // Iris follows state
  useEffect(() => {
    if (state.listening) {
      // Look slightly up when listening
      setIrisOffset({ x: 0, y: -2 });
    } else if (state.thinking) {
      // Look to the side when thinking
      setIrisOffset({ x: 3, y: -1 });
    } else if (state.speaking) {
      // Look at user when speaking
      setIrisOffset({ x: 0, y: 0 });
    } else {
      // Idle — slight random movement
      setIrisOffset({
        x: Math.sin(breathPhase * 0.02) * 2,
        y: Math.cos(breathPhase * 0.03) * 1,
      });
    }
  }, [state.listening, state.thinking, state.speaking, breathPhase]);

  const breathScale = 1 + Math.sin(breathPhase * Math.PI / 180) * 0.03;
  const eyeOpenness = isBlinking ? 0.1 : (state.tired ? 0.7 : 1.0);

  // Mouth shape
  const mouthWidth = state.speaking
    ? 12 + Math.sin(breathPhase * 0.3) * 6  // Animated when speaking
    : 10;
  const mouthHeight = state.speaking
    ? 4 + Math.sin(breathPhase * 0.3) * 3
    : state.persona === "sophie" ? 3 : 1;

  return (
    <div
      onClick={onClick}
      style={{
        position: "relative",
        width: size,
        height: size,
        cursor: "pointer",
        transform: `scale(${breathScale})`,
        transition: "transform 0.3s ease",
      }}
    >
      {/* Connection indicator ring */}
      <div
        style={{
          position: "absolute",
          inset: -4,
          borderRadius: "50%",
          border: `2px solid ${state.connected ? emotionColor : "#666"}`,
          opacity: state.connected ? (state.listening ? 0.8 : 0.4) : 0.2,
          animation: state.listening ? "pulse 1.5s ease-in-out infinite" : undefined,
        }}
      />

      {/* Face */}
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: style.faceRadius,
          background: state.persona === "sophie"
            ? "radial-gradient(ellipse at 30% 30%, #2a1f3d, #13121f)"
            : "radial-gradient(ellipse at 30% 30%, #1a2332, #0d0c18)",
          border: `${style.borderWidth}px solid ${emotionColor}40`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
          position: "relative",
        }}
      >
        {/* Eyes container */}
        <div style={{ display: "flex", gap: size * 0.2, marginTop: -size * 0.05 }}>
          {/* Left eye */}
          <div style={{
            width: size * 0.18,
            height: size * 0.18 * eyeOpenness,
            borderRadius: "50%",
            background: "#1a1a2e",
            border: `1px solid ${emotionColor}30`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "height 0.15s ease",
          }}>
            <div style={{
              width: size * 0.08,
              height: size * 0.08,
              borderRadius: "50%",
              background: style.eyeColor,
              transform: `translate(${irisOffset.x}px, ${irisOffset.y}px)`,
              transition: "transform 0.3s ease",
              boxShadow: `0 0 ${size * 0.05}px ${style.eyeColor}60`,
            }} />
          </div>

          {/* Right eye */}
          <div style={{
            width: size * 0.18,
            height: size * 0.18 * eyeOpenness,
            borderRadius: "50%",
            background: "#1a1a2e",
            border: `1px solid ${emotionColor}30`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "height 0.15s ease",
          }}>
            <div style={{
              width: size * 0.08,
              height: size * 0.08,
              borderRadius: "50%",
              background: style.eyeColor,
              transform: `translate(${irisOffset.x}px, ${irisOffset.y}px)`,
              transition: "transform 0.3s ease",
              boxShadow: `0 0 ${size * 0.05}px ${style.eyeColor}60`,
            }} />
          </div>
        </div>

        {/* Mouth */}
        <div style={{
          width: mouthWidth * scale,
          height: mouthHeight * scale,
          borderRadius: state.speaking ? "50%" : `0 0 ${mouthWidth}px ${mouthWidth}px`,
          background: state.speaking ? "#2a1f3d" : "transparent",
          borderBottom: state.speaking ? "none" : `2px solid ${emotionColor}40`,
          marginTop: size * 0.08,
          transition: "all 0.1s ease",
        }} />

        {/* Consciousness glow */}
        <div style={{
          position: "absolute",
          bottom: 2,
          left: "50%",
          transform: "translateX(-50%)",
          width: size * 0.3,
          height: 2,
          borderRadius: 1,
          background: `linear-gradient(90deg, transparent, ${emotionColor}, transparent)`,
          opacity: state.consciousnessLevel,
        }} />
      </div>

      {/* Persona label */}
      <div style={{
        position: "absolute",
        bottom: -14,
        left: "50%",
        transform: "translateX(-50%)",
        fontSize: 9,
        color: emotionColor,
        opacity: 0.6,
        fontFamily: "monospace",
        whiteSpace: "nowrap",
      }}>
        {state.persona.toUpperCase()}
        {state.currentTool ? ` ⚡ ${state.currentTool}` : ""}
      </div>

      {/* Speech bubble */}
      {thoughtVisible && state.lastText && (
        <div style={{
          position: "absolute",
          bottom: size + 8,
          left: size / 2,
          transform: "translateX(-50%)",
          background: "#1a1a2e",
          border: `1px solid ${emotionColor}30`,
          borderRadius: 12,
          padding: "8px 12px",
          maxWidth: 280,
          fontSize: 12,
          color: "#e0e0e0",
          lineHeight: 1.4,
          boxShadow: `0 4px 20px rgba(0,0,0,0.5), 0 0 10px ${emotionColor}10`,
          zIndex: 1000,
        }}>
          {state.lastText.slice(0, 200)}
          {state.lastText.length > 200 ? "..." : ""}
          {/* Arrow */}
          <div style={{
            position: "absolute",
            bottom: -6,
            left: "50%",
            transform: "translateX(-50%) rotate(45deg)",
            width: 12,
            height: 12,
            background: "#1a1a2e",
            borderRight: `1px solid ${emotionColor}30`,
            borderBottom: `1px solid ${emotionColor}30`,
          }} />
        </div>
      )}

      {/* Listening indicator */}
      {state.listening && (
        <div style={{
          position: "absolute",
          top: -8,
          right: -8,
          width: 16,
          height: 16,
          borderRadius: "50%",
          background: "#FF4444",
          animation: "pulse 1s ease-in-out infinite",
          boxShadow: "0 0 8px #FF4444",
        }} />
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}
