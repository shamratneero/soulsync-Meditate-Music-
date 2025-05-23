// src/components/Player/Player.jsx

import React, { useRef, useState, useEffect } from "react";

const Player = ({ song }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    const duration = audioRef.current.duration || 0;
    const currentTime = audioRef.current.currentTime || 0;
    setProgress((currentTime / duration) * 100);
  };

  return (
    <div className="w-full max-w-md mx-auto mt-6 px-4 py-5 rounded-2xl bg-gray-900 text-white shadow-2xl">
      <div className="flex items-center space-x-4">
        <div className="w-16 h-16 rounded-xl bg-gray-700 flex items-center justify-center text-xl font-bold">
          🎧
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-lg">
            {song?.title || "Unknown Title"}
          </h3>
          <p className="text-sm text-gray-400">
            {song?.mood || "Unknown Mood"}
          </p>
        </div>
      </div>

      <audio
        ref={audioRef}
        src={
          song?.audio_file?.startsWith("http")
            ? song.audio_file
            : `http://127.0.0.1:8000${song?.audio_file}`
        }
        onTimeUpdate={handleTimeUpdate}
      />

      <div className="mt-4">
        <div className="w-full h-2 bg-gray-700 rounded-full">
          <div
            className="h-2 bg-green-400 rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="mt-4 flex justify-center">
        <button
          onClick={togglePlay}
          className="bg-green-600 hover:bg-green-500 px-4 py-2 rounded-full transition"
        >
          {isPlaying ? "⏸ Pause" : "▶️ Play"}
        </button>
      </div>
    </div>
  );
};

export default Player;
