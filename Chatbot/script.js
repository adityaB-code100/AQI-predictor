async function chat() {
  let msg = document.getElementById("msg").value;
  let chatBox = document.getElementById("chatBox");

  if (!msg.trim()) return;

  chatBox.innerHTML += `<div><b>You:</b> ${msg}</div>`;

  const res = await fetch("https://aditya5818e.app.n8n.cloud/webhook/b2887a82-528f-4532-9944-7977711e0d3f/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message: msg })
  });

  const data = await res.json().catch(() => res.text());

  chatBox.innerHTML += `<div><b>Bot:</b> ${typeof data === "string" ? data : JSON.stringify(data)}</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;

  document.getElementById("msg").value = "";
}
