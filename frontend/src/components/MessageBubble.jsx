export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message ${message.role} ${message.isError ? 'error' : ''}`}>
      {!isUser && <div className="avatar">AI</div>}
      <div className="bubble">
        <div className="content">{message.content}</div>
        {!isUser && message.sources?.length > 0 && (
          <div className="sources">
            <p className="sources-label">Sources</p>
            {message.sources.map((src, i) => (
              <div key={i} className="source-item">
                <span className="source-name">{src.source}</span>
                <span className="source-score">{Math.round(src.score * 100)}% match</span>
              </div>
            ))}
          </div>
        )}
      </div>
      {isUser && <div className="avatar user-avatar">You</div>}
    </div>
  )
}
