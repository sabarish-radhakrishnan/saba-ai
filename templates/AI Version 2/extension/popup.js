const questionEl = document.getElementById("question");
const outputEl = document.getElementById("output");
const askBtn = document.getElementById("askBtn");
const clearBtn = document.getElementById("clearBtn");
const includePageTextEl = document.getElementById("includePageText");

function setOutput(text) {
  outputEl.textContent = text;
}

askBtn.addEventListener("click", async () => {
  const message = (questionEl.value || "").trim();
  const includePageText = includePageTextEl.checked;

  if (!message) {
    setOutput("Type a question first.");
    return;
  }

  setOutput("Thinking...");

  chrome.runtime.sendMessage(
    { type: "ASK_AI", message, includePageText },
    (resp) => {
      const err = chrome.runtime.lastError;
      if (err) {
        setOutput("Extension error: " + err.message);
        return;
      }

      if (!resp?.ok) {
        setOutput("Error: " + (resp?.error || "Unknown error"));
        return;
      }

      setOutput(resp.answer || "(No answer returned)");
    }
  );
});

clearBtn.addEventListener("click", () => {
  questionEl.value = "";
  setOutput("Ready.");
});
