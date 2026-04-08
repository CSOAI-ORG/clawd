import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { LivingCharacter } from "./components/LivingCharacter";
import { ChatPanel } from "./components/ChatPanel";
import { CharacterPicker, type VisualStyle } from "./components/CharacterPicker";
import { DiceBearCharacter } from "./components/DiceBearCharacter";
import { Live2DCharacter } from "./components/Live2DCharacter";
import { useConnectionStatus } from "./hooks/useConnectionStatus";
import { useCharacterBridge } from "./hooks/useCharacterBridge";
import type { RingStatus } from "./lib/types";

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

// Built-in characters (synced from MEOK database)
const CHARACTERS = [
  { id: "jarvis", name: "Jarvis", archetype: "Scholar" },
  { id: "sophie", name: "Sophie", archetype: "Healer" },
  { id: "legion", name: "Legion", archetype: "Guardian" },
  { id: "oracle", name: "Oracle", archetype: "Mystic" },
  { id: "adam", name: "Adam", archetype: "Pioneer" },
  { id: "sage", name: "Sage Wisdom", archetype: "Scholar" },
  { id: "dragon", name: "Dragon Forge", archetype: "Pioneer" },
  { id: "guardian", name: "Guardian Shield", archetype: "Guardian" },
  { id: "riri", name: "Riri Builder", archetype: "Trickster" },
  { id: "curiosity", name: "Curiosity Spark", archetype: "Mystic" },
  { id: "harvest", name: "Harvest Reaper", archetype: "Guardian" },
  { id: "orion", name: "Orion Scout", archetype: "Pioneer" },
];

type View = "character" | "chat" | "picker";

export default function App() {
  const [view, setView] = useState<View>("character");
  const [activeGame, setActiveGame] = useState<string | null>(null);
  const [voiceActive, setVoiceActive] = useState(false);
  const [visualStyle, setVisualStyle] = useState<VisualStyle>(
    () => (localStorage.getItem("meok-visual-style") as VisualStyle) || "css-face"
  );
  const [activeCharId, setActiveCharId] = useState(
    () => localStorage.getItem("meok-active-char") || "jarvis"
  );
  const connectionStatus = useConnectionStatus();
  const { state: characterState, sendUserInput } = useCharacterBridge();

  // Save preferences
  useEffect(() => { localStorage.setItem("meok-visual-style", visualStyle); }, [visualStyle]);
  useEffect(() => { localStorage.setItem("meok-active-char", activeCharId); }, [activeCharId]);

  // Game detection
  useEffect(() => {
    const unlisten = listen<string>("game-detected", (event) => {
      setActiveGame(event.payload === "none" ? null : event.payload);
    });
    return () => { unlisten.then((fn) => fn()); };
  }, []);

  // Voice activation (Ctrl+Shift+V)
  useEffect(() => {
    const unlisten = listen("voice-activate", () => {
      setView("chat");
      setVoiceActive(true);
      invoke("resize_for_panel");
    });
    return () => { unlisten.then((fn) => fn()); };
  }, []);

  // Character selection from tray
  useEffect(() => {
    const unlisten = listen<string>("character-selected", (event) => {
      setActiveCharId(event.payload);
    });
    return () => { unlisten.then((fn) => fn()); };
  }, []);

  const gameAccent = activeGame ? (GAME_COLORS[activeGame] ?? DEFAULT_GAME_COLOR) : undefined;
  const activeChar = CHARACTERS.find(c => c.id === activeCharId) || CHARACTERS[0];

  const handleCharacterClick = async () => {
    try {
      await invoke("resize_for_panel");
      setView("chat");
    } catch (e) {
      console.error("resize failed:", e);
      setView("chat"); // Still switch even if resize fails
    }
  };

  const handleCharacterRightClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await invoke("resize_for_panel");
      setView("picker");
    } catch (e2) {
      console.error("resize failed:", e2);
      setView("picker");
    }
  };

  const handleClose = async () => {
    setView("character");
    setVoiceActive(false);
    await invoke("resize_for_fab");
  };

  const handleSelectChar = (id: string) => {
    setActiveCharId(id);
  };

  return (
    <div className="w-full h-full flex items-start justify-start">
      {/* Game mode indicator */}
      {activeGame && view === "character" && (
        <div
          className="absolute top-0 left-0 right-0 flex items-center justify-center"
          style={{
            height: "18px", background: gameAccent, opacity: 0.9,
            borderRadius: "6px 6px 0 0", fontSize: "9px", fontWeight: 700,
            color: "#fff", letterSpacing: "0.5px", textTransform: "uppercase",
            pointerEvents: "none", zIndex: 10,
          }}
        >
          🎮 {activeGame}
        </div>
      )}

      {view === "chat" ? (
        <ChatPanel
          onClose={handleClose}
          activeGame={activeGame}
          gameAccent={gameAccent}
          voiceActive={voiceActive}
        />
      ) : view === "picker" ? (
        <CharacterPicker
          characters={CHARACTERS}
          activeCharacterId={activeCharId}
          onSelect={handleSelectChar}
          onStyleChange={setVisualStyle}
          currentStyle={visualStyle}
          onClose={handleClose}
        />
      ) : (
        /* Character view — render based on visual style */
        <div onContextMenu={handleCharacterRightClick}>
          {visualStyle === "live2d" ? (
            <Live2DCharacter
              state={characterState}
              modelId={activeChar.archetype.toLowerCase() === "healer" ? "shizuku" : "hiyori"}
              size={120}
              onClick={handleCharacterClick}
            />
          ) : visualStyle === "dicebear" ? (
            <DiceBearCharacter
              name={activeChar.name}
              archetype={activeChar.archetype}
              state={characterState}
              size={80}
              onClick={handleCharacterClick}
            />
          ) : (
            <LivingCharacter
              state={characterState}
              size={80}
              onClick={handleCharacterClick}
            />
          )}
        </div>
      )}
    </div>
  );
}
