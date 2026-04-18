'use client';

import { useEffect, useState } from 'react';
import { Users, TrendingUp } from 'lucide-react';

export default function VisitorCounter() {
  const [counts, setCounts] = useState<{ total: number; today: number } | null>(null);

  useEffect(() => {
    // API 호출 (페이지 뷰 카운트 및 조회)
    const fetchVisitorCount = async () => {
      try {
        const res = await fetch('/api/visitor', { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          if (data.total !== undefined) {
            setCounts(data);
          }
        }
      } catch (error) {
        console.error('Failed to fetch visitor count');
        // 에러 시 빈 값 유지되더라도 무시
      }
    };
    
    // 웹사이트 초기 렌더링을 방해하지 않기 위해 1초 지연 호출
    const timer = setTimeout(() => {
      fetchVisitorCount();
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="visitor-widget-container">
      <div className="visitor-widget" title="방문자 통계 (Vercel KV)">
        <div className="visitor-widget-inner">
          {counts ? (
            <>
              <div className="visitor-stat">
                <TrendingUp size={16} className="visitor-stat-icon today" />
                <span>오늘 <strong className="visitor-value">{counts.today.toLocaleString()}</strong></span>
              </div>
              <div className="visitor-divider"></div>
              <div className="visitor-stat">
                <Users size={16} className="visitor-stat-icon total" />
                <span>누적 <strong className="visitor-value">{counts.total.toLocaleString()}</strong></span>
              </div>
            </>
          ) : (
            <div className="visitor-skeleton">
              <div className="visitor-skeleton-block"></div>
              <div className="visitor-skeleton-block"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
