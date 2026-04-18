import { kv } from '@vercel/kv';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    // 오늘 날짜 구하기 (YYYY-MM-DD 형식)
    const today = new Date().toISOString().split('T')[0];
    
    // 누적 접속자 수 증가
    const total = await kv.incr('pageviews:total');
    // 오늘 접속자 수 증가
    const daily = await kv.incr(`pageviews:today:${today}`);
    
    // 오늘의 카운터 키는 이틀 뒤면 필요 없으므로 만료 시간 설정 (48시간)
    await kv.expire(`pageviews:today:${today}`, 48 * 60 * 60);

    return NextResponse.json({ total, today: daily });
  } catch (error) {
    console.error('Visitor Counter API Error:', error);
    // 에러 발생 시 UI 에러 방지를 위해 기본값 반환
    return NextResponse.json(
      { total: 0, today: 0, error: 'Database connection failed' }, 
      { status: 200 } // 500으로 던지면 프론트 fetch가 깨지므로 200에 0을 보냅니다
    );
  }
}
