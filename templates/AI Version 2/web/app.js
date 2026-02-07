const apiUrlEl = document.getElementById("apiUrl");
const msgEl = document.getElementById("message");
const ctxEl = document.getElementById("context");
const outEl = document.getElementById("out");
const askBtn = document.getElementById("askBtn");
const clearBtn = document.getElementById("clearBtn");
const pingBtn = document.getElementById("pingBtn");

function setOut(t) { outEl.textContent = t; }

async function postChat(apiUrl, message, context) {
  const res = await fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context })
  });

  const data = await res.json().catch(async () => ({ error: await res.text() }));
  if (!res.ok || data?.success === false) {
    throw new Error(data?.error || data?.error || `HTTP ${res.status}`);
  }
  return data.response;
}

pingBtn.addEventListener("click", async () => {
  try {
    setOut("Pinging...");
    const base = apiUrlEl.value.replace(/\/api\/chat\s*$/i, "");
    const res = await fetch(base + "/api/status");
    const data = await res.json();
    setOut("✅ Backend OK:\n" + JSON.stringify(data, null, 2));
  } catch (e) {
    setOut("❌ Ping failed:\n" + (e?.message || String(e)));
  }
});

askBtn.addEventListener("click", async () => {
  const apiUrl = apiUrlEl.value.trim();
  const message = msgEl.value.trim();
  const context = ctxEl.value.trim();

  if (!message) return setOut("Type a message first.");

  try {
    setOut("Thinking...");
    const answer = await postChat(apiUrl, message, context);
    setOut(answer || "(No answer returned)");
  } catch (e) {
    setOut("❌ Error:\n" + (e?.message || String(e)));
  }
});

clearBtn.addEventListener("click", () => {
  msgEl.value = "";
  ctxEl.value = "";
  setOut("Ready.");
});
