// background.js (Manifest V3 service worker)

console.log("🔥 background.js LOADED");

// ---- helpers ----
async function getActiveTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  return tabs?.[0];
}

async function getPageContext(tabId, includePageText) {
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(
      tabId,
      { type: "GET_CONTEXT", includePageText },
      (resp) => {
        const err = chrome.runtime.lastError;
        if (err) return reject(new Error(err.message));
        if (!resp) return reject(new Error("No response from content script"));
        resolve(resp);
      }
    );
  });
}

async function callBackend(message, context) {
  console.log("🌐 calling backend...");

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000); // 20s timeout

  try {
    const res = await fetch("http://127.0.0.1:5000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, context }),
      signal: controller.signal
    });

    let data;
    try {
      data = await res.json();
    } catch {
      const text = await res.text();
      throw new Error("Backend returned non-JSON: " + text);
    }

    if (!res.ok || data?.success === false) {
      throw new Error(data?.error || `Backend error (HTTP ${res.status})`);
    }

    return data.response;
  } finally {
    clearTimeout(timeout);
  }
}

// ---- main message handler ----
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg?.type !== "ASK_AI") return;

  (async () => {
    try {
      console.log("📩 ASK_AI received:", msg);

      const tab = await getActiveTab();
      if (!tab?.id) throw new Error("No active tab found");

      console.log("🧾 active tab:", tab.id, tab.url);

      const includePageText = Boolean(msg.includePageText);

      // Try to get page context, but don’t fail if it breaks
      let ctx;
      try {
        ctx = await getPageContext(tab.id, includePageText);
        console.log("📄 got context:", {
          title: ctx?.title,
          hasSelected: !!ctx?.selectedText,
          pageTextLen: (ctx?.pageText || "").length
        });
      } catch (e) {
        console.warn("⚠️ Could not get page context:", e.message);
        ctx = {
          title: tab.title || "",
          url: tab.url || "",
          selectedText: "",
          pageText: ""
        };
      }

      // Build context string
      const parts = [];
      if (ctx.title) parts.push(`Title: ${ctx.title}`);
      if (ctx.url) parts.push(`URL: ${ctx.url}`);
      if (ctx.selectedText) {
        parts.push("\nSelected Text:\n" + ctx.selectedText);
      } else if (ctx.pageText) {
        parts.push("\nPage Text (truncated):\n" + ctx.pageText);
      }

      const contextString = parts.join("\n");

      const answer = await callBackend(msg.message, contextString);

      sendResponse({ ok: true, answer });
    } catch (e) {
      console.error("❌ background error:", e);
      sendResponse({ ok: false, error: e.message || String(e) });
    }
  })();

  return true; // keep channel open for async response
});
