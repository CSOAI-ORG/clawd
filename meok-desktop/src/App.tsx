import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { LivingCharacter } from "./components/LivingCharacter";
import { ChatPanel } from "./components/ChatPanel";
import { useConnectionStatus } from "./hooks/useConnectionStatus";
import { useCharacterBridge } from "./hooks/useCharacterBridge";
import type { RingStatus } from "./lib/types";

// Game → accent color mapping
const GAME_COLORS: Record<string, string> = {
  "Fortnite":          "#F7D618",
  "Valorant":          "#FF4655",
  "League of Legends": "#C89B3C",
  "Counter-Strike 2":  "#F0A500",
  "Rocket League":      "#1DB4F3",
  "Overwatch 2":        "#F99E1A",
  "Dota 2":             "#C23B2A",
  "Minecraft":          "#5D8A1C",
  "Hearthstone":        "#B8803B",
  "Diablo IV":          "#992D2D",
};

const DEFAULT_GAME_COLOR = "#60B8F0";

export default function App() {
  const [panelOpen, setPanelOpen] = useState(false);
  const [activeGame, setActiveGame] = useState<string | null>(null);
  const [voiceActive, setVoiceActive] = useState(false);
  const connectionStatus = useConnectionStatus();
  const { state: characterState, sendUserInput } = useCharacterBridge();

  // Listen for game detection events from Tauri background thread
  useEffect(() => {
    const unlisten = listen<string>("game-detected", (event) => {
      const game = event.payload === "none" ? null : event.payload;
      setActiveGame(game);
    });
    return () => { unlisten.then((fn) => fn()); };
  }, []);

  // Listen for voice activation (Ctrl+Shift+V)
  useEffect(() => {
    const unlisten = listen("voice-activate", () => {
      setPanelOpen(true);
      setVoiceActive(true);
      invoke("resize_for_panel");
    });
    return () => { unlisten.then((fn) => fn()); };
  }, []);

  const gameAccent = activeGame
    ? (GAME_COLORS[activeGame] ?? DEFAULT_GAME_COLOR)
    : undefined;

  const handleCharacterClick = async () => {
    if (panelOpen) {
      setPanelOpen(false);
      await invoke("resize_for_fab");
    } else {
      setPanelOpen(true);
      await invoke("resize_for_panel");
    }
  };

  const handleClose = async () => {
    setPanelOpen(false);
    await invoke("resize_for_fab");
  };

  return (
    <div className="w-full h-full flex items-start justify-start">
      {/* Game mode indicator */}
      {activeGame && !panelOpen && (
        <div
          className="absolute top-0 left-0 right-0 flex items-center justify-center"
          style={{
            height: "18px",
            background: gameAccent,
            opacity: 0.9,
            borderRadius: "6px 6px 0 0",
            fontSize: "9px",
            fontWeight: 700,
            color: "#fff",
            letterSpacing: "0.5px",
            textTransform: "uppercase",
            pointerEvents: "none",
            zIndex: 10,
          }}
        >
          🎮 {activeGame}
        </div>
      )}

      {panelOpen ? (
        <ChatPanel
          onClose={handleClose}
          activeGame={activeGame}
          gameAccent={gameAccent}
          voiceActive={voiceActive}
        />
      ) : (
        <LivingCharacter
          state={characterState}
          size={80}
          onClick={handleCharacterClick}
        />
      )}
    </div>
  );
}
