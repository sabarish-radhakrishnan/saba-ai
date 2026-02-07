// content.js
// Collects context from the current page.

function getSelectedText() {
  const selection = window.getSelection();
  return selection ? selection.toString().trim() : "";
}

function getPageText(maxChars = 8000) {
  const text = (document.body?.innerText || "").trim();
  if (!text) return "";
  return text.length > maxChars ? text.slice(0, maxChars) + "\n...[truncated]" : text;
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg?.type === "GET_CONTEXT") {
    const selectedText = getSelectedText();
    const pageText = msg.includePageText ? getPageText() : "";

    sendResponse({
      ok: true,
      url: location.href,
      title: document.title || "",
      selectedText,
      pageText
    });
  }
  return true;
});
