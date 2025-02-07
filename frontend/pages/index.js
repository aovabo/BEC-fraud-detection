import { useState } from "react";

export default function Home() {
  const [emailText, setEmailText] = useState("");
  const [response, setResponse] = useState(null);

  const analyzeEmail = async () => {
    const res = await fetch("http://127.0.0.1:5000/process_payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email_text: emailText,
        payment_details: { vendor: "vendor123", amount: 5000 }
      })
    });

    const data = await res.json();
    setResponse(data);
  };

  return (
    <div>
      <h1>SafeWire AI</h1>
      <textarea placeholder="Paste email here..." onChange={(e) => setEmailText(e.target.value)} />
      <button onClick={analyzeEmail}>Analyze</button>
      <pre>{response ? JSON.stringify(response, null, 2) : "Awaiting response..."}</pre>
    </div>
  );
}
