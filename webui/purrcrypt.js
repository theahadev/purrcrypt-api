/**
 * PurrCrypt Web UI - API Client
 *
 * This module communicates with the PurrCrypt API for encryption/decryption.
 */

class PurrCryptAPI {
  constructor(apiUrl = "https://api.ahathe.dev/purrcrypt") {
    // Remove trailing slash to prevent double slashes in URLs
    this.apiUrl = apiUrl.replace(/\/+$/, "");
  }

  setApiUrl(url) {
    // Remove trailing slash to prevent double slashes in URLs
    this.apiUrl = url.replace(/\/+$/, "");
  }

  async encrypt(text, password = null) {
    const response = await fetch(`${this.apiUrl}/encrypt`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        password: password || "",
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Encryption failed");
    }

    const data = await response.json();
    return data.meow;
  }

  async decrypt(meow, password = null) {
    const response = await fetch(`${this.apiUrl}/decrypt`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        meow: meow,
        password: password || "",
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Decryption failed");
    }

    const data = await response.json();
    return data.text;
  }

  async checkHealth() {
    try {
      const response = await fetch(`${this.apiUrl}/health`);
      const data = await response.json();
      return data.status === "OK";
    } catch (error) {
      return false;
    }
  }

  async getInfo() {
    const response = await fetch(`${this.apiUrl}/`);
    if (!response.ok) {
      throw new Error("Failed to fetch API info");
    }
    return await response.json();
  }
}

// Export for use in other scripts
if (typeof module !== "undefined" && module.exports) {
  module.exports = { PurrCryptAPI };
}
