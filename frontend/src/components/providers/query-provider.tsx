"use client";

// Temporarily simplified during hydration debugging
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  // Temporarily return children directly without QueryProvider wrapper
  return <>{children}</>;
}
