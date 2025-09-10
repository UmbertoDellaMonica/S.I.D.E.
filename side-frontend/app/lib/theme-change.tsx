"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
  useCallback,
} from "react";

interface ThemeContextType {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: "light",
  toggleTheme: () => {},
});

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  // Derive initial theme from <html> class (set by inline script) to avoid FOUC.
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof document === "undefined") return "light"; // SSR fallback
    return document.documentElement.classList.contains("dark")
      ? "dark"
      : "light";
  });

  const applyTheme = useCallback((newTheme: "light" | "dark") => {
    const root = document.documentElement;
    if (!root.classList.contains(newTheme)) {
      root.classList.remove("light", "dark");
      root.classList.add(newTheme);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // ignore write errors (private mode, etc.)
    }
    applyTheme(theme);
  }, [theme, applyTheme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);

export function ModeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="px-4 py-2 bg-zinc-200 dark:bg-zinc-700 text-black dark:text-white rounded shadow hover:bg-zinc-300 dark:hover:bg-zinc-600 transition-colors"
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      {theme === "dark" ? "🌞" : "🌙"}
    </button>
  );
}
