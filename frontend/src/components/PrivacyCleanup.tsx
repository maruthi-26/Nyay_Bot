"use client";

import { useEffect } from "react";

export default function PrivacyCleanup() {
  useEffect(() => {
    window.localStorage.removeItem("nyaybot-session");
  }, []);

  return null;
}
