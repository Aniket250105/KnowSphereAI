'use client';

import { useState, useRef, useEffect } from 'react';
import { chatService } from '@/services/chat';
import { Send, Bot, User, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/providers/AuthProvider';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  metadata?: any;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const data = await chatService.chat(userMsg);
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: data.answer || data.response || 'No response',
          citations: data.citations || [],
          metadata: {
            grounding_score: data.grounding_score,
            hallucination_risk: data.hallucination_risk
          }
        }
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: 'Sorry, I encountered an error while processing your request. Please try again later.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex-1 overflow-y-auto space-y-4 p-4 scroll-smooth">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-8 text-muted-foreground">
            <div className="bg-muted p-4 rounded-full mb-4">
              <Bot className="w-12 h-12 text-primary" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">How can I help you today?</h2>
            <p className="max-w-md mx-auto">
              Ask questions about your documents, generate insights, or let the AI agents assist you with complex tasks.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={cn(
                "flex max-w-4xl mx-auto w-full",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              <div className={cn(
                "flex gap-4 p-4 rounded-2xl max-w-[85%]",
                msg.role === 'user' 
                  ? "bg-primary text-primary-foreground ml-12" 
                  : "bg-muted text-foreground mr-12"
              )}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-1 text-primary">
                    <Bot size={18} />
                  </div>
                )}
                
                <div className="overflow-hidden">
                  <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                  
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-border/50 text-xs text-muted-foreground">
                      <p className="font-semibold mb-2">Sources:</p>
                      <ul className="space-y-1 list-disc list-inside">
                        {msg.citations.map((cit, i) => (
                          <li key={i}>{typeof cit === 'string' ? cit : cit.document_id || cit.source || 'Unknown Source'}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {msg.metadata?.grounding_score !== undefined && (
                    <div className="mt-3 flex items-center gap-4 text-xs font-medium">
                      <span className={cn(
                        "px-2 py-1 rounded-md",
                        msg.metadata.grounding_score > 0.8 ? "bg-green-500/10 text-green-500" : "bg-yellow-500/10 text-yellow-500"
                      )}>
                        Grounding: {(msg.metadata.grounding_score * 100).toFixed(0)}%
                      </span>
                      {msg.metadata.hallucination_risk && (
                        <span className="px-2 py-1 rounded-md bg-red-500/10 text-red-500 flex items-center gap-1">
                          <AlertCircle size={12} />
                          Risk: {msg.metadata.hallucination_risk}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-primary-foreground/20 flex items-center justify-center shrink-0 mt-1 text-primary-foreground">
                    <User size={18} />
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex max-w-4xl mx-auto w-full justify-start">
            <div className="flex gap-4 p-4 rounded-2xl bg-muted text-foreground mr-12">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-1 text-primary">
                <Bot size={18} />
              </div>
              <div className="flex items-center space-x-2 h-8">
                <div className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-background">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-end shadow-sm border rounded-xl overflow-hidden bg-background focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask KnowSphere AI..."
            className="w-full max-h-48 min-h-[56px] resize-none bg-transparent py-4 pl-4 pr-12 text-sm outline-none placeholder:text-muted-foreground disabled:opacity-50"
            rows={1}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 bottom-2 p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:hover:bg-primary transition-colors"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </form>
        <div className="text-center mt-2 text-xs text-muted-foreground">
          KnowSphere AI can make mistakes. Consider verifying important information.
        </div>
      </div>
    </div>
  );
}
