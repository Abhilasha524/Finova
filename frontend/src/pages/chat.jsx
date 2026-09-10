import { useState } from "react";

import { sendChatMessage } from "../api/chat";

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!message.trim() || loading) {
      return;
    }

    const userMessage = message.trim();

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const data = await sendChatMessage(userMessage);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: data.answer,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: `Error: ${error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const suggestedQuestions = [
    "How much did I spend?",
    "How much did I earn?",
    "What is my net savings?",
    "What is my financial persona?",
  ];

  function handleSuggestion(question) {
    if (loading) {
      return;
    }

    setMessage(question);
  }

  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1000,
        margin: "0 auto",
      }}
    >
      {/* PAGE HEADER */}
      <div
        style={{
          marginBottom: "2rem",
          textAlign: "center",
        }}
      >
        <h1
          style={{
            margin: 0,
            marginBottom: "0.5rem",
            fontSize: "2.2rem",
            lineHeight: 1.2,
          }}
        >
          AI Financial Assistant
        </h1>

        <p
          style={{
            margin: 0,
            opacity: 0.75,
          }}
        >
          Ask questions about your income, expenses, savings, goals,
          transactions, and spending behaviour.
        </p>
      </div>

      {/* CHAT CARD */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        {/* CHAT HEADER — GREEN KEPT EXACTLY AS REQUESTED */}
        <div
          style={{
            padding: "1rem 1.25rem",
            borderBottom: "1px solid #fffcfc",
            backgroundColor: "#324635",
          }}
        >
          <strong>💬 Financial Assistant</strong>

          <div
            style={{
              fontSize: "0.85rem",
              opacity: 0.7,
              marginTop: "0.25rem",
            }}
          >
            Ask questions based on your transaction data.
          </div>
        </div>

        {/* MESSAGES */}
        <div
          style={{
            padding: "1.5rem",
            minHeight: 380,
            maxHeight: 500,
            overflowY: "auto",
          }}
        >
          {/* EMPTY CHAT */}
          {messages.length === 0 && (
            <div
              style={{
                textAlign: "center",
                padding: "3rem 1rem",
              }}
            >
              <div
                style={{
                  fontSize: "3rem",
                  marginBottom: "1rem",
                }}
              >
                🤖
              </div>

              <h2
                style={{
                  marginBottom: "0.5rem",
                }}
              >
                How can I help?
              </h2>

              <p
                style={{
                  margin: "0 auto 1.5rem",
                  maxWidth: 550,
                  lineHeight: 1.6,
                  opacity: 0.7,
                }}
              >
                Ask me about your spending, income, savings, transactions,
                financial persona, or goals.
              </p>

              {/* SUGGESTED QUESTIONS */}
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  justifyContent: "center",
                  gap: "0.6rem",
                }}
              >
                {suggestedQuestions.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => handleSuggestion(question)}
                    disabled={loading}
                    style={{
                      padding: "0.6rem 0.9rem",
                      borderRadius: 999,
                      border: "1px solid #9b8965",
                      backgroundColor: "#292c27",
                      color: "#ded8c8",
                      cursor: loading ? "not-allowed" : "pointer",
                      transition: "all 0.2s ease",
                    }}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* CHAT MESSAGES */}
          {messages.map((item, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent:
                  item.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "1rem",
              }}
            >
              <div
                style={{
                  maxWidth: "75%",
                  padding: "0.9rem 1rem",

                  borderRadius:
                    item.role === "user"
                      ? "14px 14px 4px 14px"
                      : "14px 14px 14px 4px",

                  /* USER = PLUM, AI = DEEP SAGE */
                  backgroundColor:
                    item.role === "user"
                      ? "#51445f"
                      : "#263b32",

                  border:
                    item.role === "user"
                      ? "1px solid #695879"
                      : "1px solid #4c6658",

                  color:
                    item.role === "user"
                      ? "#f1eafa"
                      : "#dce8df",

                  boxShadow:
                    item.role === "user"
                      ? "0 3px 10px rgba(81, 68, 95, 0.22)"
                      : "0 3px 10px rgba(0, 0, 0, 0.18)",
                }}
              >
                <div
                  style={{
                    fontSize: "0.8rem",
                    fontWeight: "600",
                    marginBottom: "0.3rem",

                    color:
                      item.role === "user"
                        ? "#d8c9e5"
                        : "#a9c5b1",
                  }}
                >
                  {item.role === "user" ? "You" : "AI Assistant"}
                </div>

                <div
                  style={{
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {item.text}
                </div>
              </div>
            </div>
          ))}

          {/* THINKING MESSAGE */}
          {loading && (
            <div
              style={{
                display: "flex",
                justifyContent: "flex-start",
              }}
            >
              <div
                style={{
                  padding: "0.9rem 1rem",
                  borderRadius: "14px 14px 14px 4px",

                  backgroundColor: "#3b4030",
                  border: "1px solid #666b4e",

                  color: "#d8d8b8",
                  opacity: 0.9,

                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.15)",
                }}
              >
                AI Assistant is thinking...
              </div>
            </div>
          )}
        </div>

        {/* INPUT */}
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            gap: "0.75rem",
            padding: "1rem",
            borderTop: "1px solid #ddd",
          }}
        >
          <input
            type="text"
            placeholder="Ask a financial question..."
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            disabled={loading}
            style={{
              flex: 1,
              padding: "0.75rem 1rem",
              borderRadius: 8,
              border: "1px solid #8b8b8b",
              backgroundColor: "#242522",
              color: "#eeeeee",
              boxSizing: "border-box",
            }}
          />

          {/* SEND BUTTON — SEPARATE TERRACOTTA COLOR */}
          <button
            type="submit"
            disabled={loading || !message.trim()}
            style={{
              padding: "0.75rem 1.3rem",
              borderRadius: 8,
              border: "none",

              backgroundColor:
                loading || !message.trim()
                  ? "#59483f"
                  : "#9b6a52",

              color: "#fff7f2",

              cursor:
                loading || !message.trim()
                  ? "not-allowed"
                  : "pointer",

              fontWeight: "600",

              boxShadow:
                loading || !message.trim()
                  ? "none"
                  : "0 3px 8px rgba(155, 106, 82, 0.25)",

              transition: "all 0.2s ease",
            }}
          >
            {loading ? "..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;