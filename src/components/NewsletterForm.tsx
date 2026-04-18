'use client';

import { useState, FormEvent } from 'react';

export default function NewsletterForm() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      setStatus('error');
      setMessage('올바른 이메일 주소를 입력해주세요.');
      return;
    }

    setStatus('loading');
    setMessage('');

    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setMessage(data.message);
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.error || '구독 처리 중 오류가 발생했습니다.');
      }
    } catch {
      setStatus('error');
      setMessage('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
  };

  return (
    <div className="newsletter-section">
      <h4>Newsletter</h4>
      <p>프리미엄 재테크 인사이트를 이메일로 받아보세요.</p>
      <form className="newsletter-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="example@email.com"
          required
          aria-label="Newsletter Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={status === 'loading'}
        />
        <button type="submit" disabled={status === 'loading'}>
          {status === 'loading' ? '처리 중...' : '구독하기'}
        </button>
      </form>
      {message && (
        <p 
          className={`newsletter-message ${status === 'success' ? 'success' : 'error'}`}
          style={{
            marginTop: '0.75rem',
            fontSize: '0.85rem',
            color: status === 'success' ? '#34d399' : '#f87171',
            transition: 'all 0.3s ease',
          }}
        >
          {message}
        </p>
      )}
    </div>
  );
}
