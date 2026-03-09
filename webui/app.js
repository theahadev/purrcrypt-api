/**
 * PurrCrypt Web UI - Main Application
 * Uses the PurrCrypt API for encryption/decryption
 */

// Initialize API client — URL comes from config.js
let api = new PurrCryptAPI(PURRCRYPT_CONFIG.apiUrl);

// Current mode: 'decrypt' or 'encrypt'
let currentMode = "encrypt";

// UI Elements
const elements = {
  // Tabs
  tabButtons: document.querySelectorAll(".tab-button"),

  // Main form elements
  mainHeading: document.getElementById("main-heading"),
  mainInput: document.getElementById("main-input"),
  mainPassword: document.getElementById("main-password"),
  mainBtn: document.getElementById("main-btn"),
  mainOutput: document.getElementById("main-output"),
  outputGroup: document.getElementById("output-group"),
  stats: document.getElementById("stats"),
  copyOutput: document.getElementById("copy-output"),

  // Labels
  inputLabel: document.getElementById("input-label"),
  passwordLabel: document.getElementById("password-label"),
  buttonLabel: document.getElementById("button-label"),
  outputLabel: document.getElementById("output-label"),

  // Toast
  toast: document.getElementById("toast"),
};

/**
 * Matrix-style text scramble effect
 */
function scrambleText(element, newText, duration = 200) {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()";
  let iterations = 0;
  const maxIterations = Math.floor(duration / 15);

  const interval = setInterval(() => {
    element.textContent = newText
      .split("")
      .map((char, index) => {
        if (char === " " || char === "\n") return char;
        if (index < iterations) return newText[index];
        return chars[Math.floor(Math.random() * chars.length)];
      })
      .join("");

    iterations += 1;

    if (iterations > newText.length) {
      clearInterval(interval);
      element.textContent = newText;
    }
  }, 15);
}

/**
 * Update form labels based on mode
 */
function updateFormLabels(mode) {
  if (mode === "decrypt") {
    scrambleText(elements.mainHeading, "Decrypt Your Message", 200);
    scrambleText(elements.inputLabel, "Encrypted Input", 175);
    scrambleText(
      elements.passwordLabel,
      "Password (If used during encryption)",
      175,
    );
    scrambleText(elements.buttonLabel, "Decrypt Message", 175);
    scrambleText(elements.outputLabel, "Decrypted Output", 175);

    elements.mainInput.placeholder = "Paste your encrypted message here...";
    elements.mainPassword.placeholder = "Leave empty if no password was used";
    elements.stats.style.display = "none";
  } else {
    scrambleText(elements.mainHeading, "Encrypt Your Message", 200);
    scrambleText(elements.inputLabel, "Input", 175);
    scrambleText(elements.passwordLabel, "Password (Optional)", 175);
    scrambleText(elements.buttonLabel, "Encrypt Message", 175);
    scrambleText(elements.outputLabel, "Encrypted Output", 175);

    elements.mainInput.placeholder = "Enter your message here...";
    elements.mainPassword.placeholder = "Leave empty for no password";
  }
}

/**
 * Show toast notification
 */
function showToast(message, type = "success") {
  elements.toast.textContent = message;
  elements.toast.className = `toast ${type}`;
  elements.toast.classList.add("show");

  setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 3000);
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Copied to clipboard", "success");
  } catch (err) {
    // Fallback for older browsers
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();

    try {
      document.execCommand("copy");
      showToast("Copied to clipboard", "success");
    } catch (e) {
      showToast("Failed to copy", "error");
    }

    document.body.removeChild(textarea);
  }
}

/**
 * Format bytes to human readable string
 */
function formatBytes(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

/**
 * Tab switching with matrix effect
 */
elements.tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const tabName = button.dataset.tab;

    // Don't do anything if already on this tab
    if (currentMode === tabName) return;

    // Update active tab button
    elements.tabButtons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");

    // Update mode
    currentMode = tabName;

    // Clear form
    elements.mainInput.value = "";
    elements.mainPassword.value = "";
    elements.mainOutput.value = "";
    elements.outputGroup.style.display = "none";

    // Update labels with matrix effect
    updateFormLabels(tabName);
  });
});

/**
 * Main button handler (encrypt or decrypt based on mode)
 */
elements.mainBtn.addEventListener("click", async () => {
  const message = elements.mainInput.value.trim();
  const password = elements.mainPassword.value;

  // Validation
  if (!message) {
    showToast(`Please enter a message to ${currentMode}`, "error");
    return;
  }

  // Show loading state
  elements.mainBtn.classList.add("loading");
  elements.mainBtn.disabled = true;

  try {
    if (currentMode === "encrypt") {
      // Perform encryption via API
      const encrypted = await api.encrypt(message, password || null);

      // Calculate stats
      const originalSize = new TextEncoder().encode(message).length;
      const encryptedSize = new TextEncoder().encode(encrypted).length;
      const wordCount = encrypted.split(/\s+/).length;
      const ratio = (encryptedSize / originalSize).toFixed(2);

      // Display results
      elements.mainOutput.value = encrypted;
      elements.outputGroup.style.display = "block";

      // Show stats
      const statsHTML = `
                <strong>${wordCount}</strong> words generated |
                Original: <strong>${formatBytes(originalSize)}</strong> →
                Encrypted: <strong>${formatBytes(encryptedSize)}</strong>
                (${ratio}x expansion)
            `;
      elements.stats.innerHTML = statsHTML;
      elements.stats.style.display = "block";

      // Show success message
      showToast("Message encrypted successfully", "success");
    } else {
      // Perform decryption via API
      const decrypted = await api.decrypt(message, password || null);

      // Display results
      elements.mainOutput.value = decrypted;
      elements.outputGroup.style.display = "block";
      elements.stats.style.display = "none";

      // Show success message
      showToast("Message decrypted successfully", "success");
    }

    // Scroll to output
    elements.outputGroup.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  } catch (error) {
    console.error(`${currentMode} error:`, error);
    showToast(error.message, "error");
  } finally {
    // Remove loading state
    elements.mainBtn.classList.remove("loading");
    elements.mainBtn.disabled = false;
  }
});

/**
 * Copy button handler
 */
elements.copyOutput.addEventListener("click", () => {
  const text = elements.mainOutput.value;
  if (text) {
    copyToClipboard(text);
  }
});

/**
 * Keyboard shortcuts
 */
document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + Enter to encrypt/decrypt
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    elements.mainBtn.click();
    e.preventDefault();
  }
});

/**
 * Auto-resize textarea
 */
function autoResize(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = textarea.scrollHeight + "px";
}

elements.mainInput.addEventListener("input", function () {
  autoResize(this);
});

/**
 * Clear output when input changes
 */
elements.mainInput.addEventListener("input", () => {
  if (elements.outputGroup.style.display !== "none") {
    elements.mainOutput.value = "";
    elements.outputGroup.style.display = "none";
  }
});

/**
 * Update API status indicator
 */
function updateApiStatus(connected, version = null) {
  const statusElement = document.getElementById("api-status");
  const statusText = statusElement.querySelector(".status-text");
  const versionElement = document.getElementById("api-version");

  if (connected) {
    statusElement.className = "api-status connected";
    statusText.textContent = "API Connected";
    if (version) {
      versionElement.textContent = `v${version}`;
    } else {
      versionElement.textContent = "Unknown";
    }
  } else {
    statusElement.className = "api-status disconnected";
    statusText.textContent = "API Disconnected";
    versionElement.textContent = "Unknown";
  }
}

/**
 * Check API connection on load
 */
window.addEventListener("load", async () => {
  console.log(`
╔═══════════════════════════════════════╗
║  PurrCrypt Web UI Loaded             ║
║  Connecting to API...                 ║
╚═══════════════════════════════════════╝
    `);

  // Check if API is available
  const isHealthy = await api.checkHealth();

  if (isHealthy) {
    console.log("✅ API connection successful!");

    // Fetch API info to get version
    try {
      const info = await api.getInfo();
      const version = info.version || "unknown";
      updateApiStatus(true, version);
    } catch (error) {
      console.warn("Could not fetch API version:", error);
      updateApiStatus(true);
    }
  } else {
    console.warn("API not available at " + api.apiUrl);
    updateApiStatus(false);
    showToast("API not available. Please start the API server first.", "error");
  }
});

/**
 * Error boundary for unhandled errors
 */
window.addEventListener("error", (event) => {
  console.error("Unhandled error:", event.error);
  showToast("An unexpected error occurred", "error");
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason);
  showToast("An unexpected error occurred", "error");
});
