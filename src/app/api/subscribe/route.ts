import { Resend } from 'resend';
import { NextRequest, NextResponse } from 'next/server';

// Resend 클라이언트를 lazy 초기화 (빌드 시 API 키가 없어도 에러 방지)
let resendClient: Resend | null = null;
function getResend(): Resend {
  if (!resendClient) {
    resendClient = new Resend(process.env.RESEND_API_KEY);
  }
  return resendClient;
}

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json();

    if (!email || !email.includes('@')) {
      return NextResponse.json(
        { error: '올바른 이메일 주소를 입력해주세요.' },
        { status: 400 }
      );
    }

    const audienceId = process.env.RESEND_AUDIENCE_ID;
    if (!audienceId) {
      console.error('RESEND_AUDIENCE_ID is not set');
      return NextResponse.json(
        { error: '서버 설정 오류입니다. 관리자에게 문의하세요.' },
        { status: 500 }
      );
    }

    const resend = getResend();

    // Resend Audience에 구독자 추가
    const { data, error } = await resend.contacts.create({
      email,
      unsubscribed: false,
      audienceId,
    });

    if (error) {
      // 이미 등록된 이메일인 경우
      if (error.message?.includes('already exists')) {
        return NextResponse.json(
          { message: '이미 구독 중인 이메일입니다. 😊' },
          { status: 200 }
        );
      }
      console.error('Resend error:', error);
      return NextResponse.json(
        { error: '구독 처리 중 오류가 발생했습니다.' },
        { status: 500 }
      );
    }

    // 환영 이메일 발송
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'Daily Better <onboarding@resend.dev>';
    
    await resend.emails.send({
      from: fromEmail,
      to: email,
      subject: '🎉 Daily Better 뉴스레터 구독 완료!',
      html: `
        <div style="max-width: 600px; margin: 0 auto; font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background: #0a0a0a; color: #e0e0e0; padding: 40px 30px; border-radius: 12px;">
          <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #60a5fa; font-size: 28px; margin: 0;">Daily Better</h1>
            <p style="color: #888; font-size: 14px; margin-top: 8px;">어제보다 나은 하루</p>
          </div>
          
          <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 8px; padding: 30px; margin-bottom: 20px;">
            <h2 style="color: #fff; font-size: 20px; margin-top: 0;">구독을 환영합니다! 🚀</h2>
            <p style="color: #ccc; line-height: 1.8;">
              앞으로 매일 아침, <strong style="color: #60a5fa;">전문가 수준의 재테크·자기계발 인사이트</strong>를 
              이메일로 받아보실 수 있습니다.
            </p>
            <ul style="color: #ccc; line-height: 2;">
              <li>📈 실전 투자 전략 & 시장 분석</li>
              <li>💡 돈 관리 시스템 & 절약 노하우</li>
              <li>🧠 마인드셋 & 생산성 향상 팁</li>
              <li>📊 최신 경제 트렌드 해설</li>
            </ul>
          </div>
          
          <div style="text-align: center; margin-top: 30px;">
            <a href="https://wealth-growth-kohl.vercel.app" 
               style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
              블로그 방문하기 →
            </a>
          </div>
          
          <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #333;">
            <p style="color: #666; font-size: 12px;">
              © ${new Date().getFullYear()} Daily Better. All rights reserved.<br>
              구독을 원치 않으시면 이메일 하단의 수신거부 링크를 클릭하세요.
            </p>
          </div>
        </div>
      `,
    });

    return NextResponse.json(
      { message: '구독이 완료되었습니다! 환영 이메일을 확인해주세요. 📬' },
      { status: 200 }
    );
  } catch (err) {
    console.error('Subscribe error:', err);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' },
      { status: 500 }
    );
  }
}
