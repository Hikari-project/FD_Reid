import { NextRequest, NextResponse } from 'next/server';

interface SetRoiRequest {
  sourceUrl: string;
  roi: [number, number, number, number]; // [x1, y1, x2, y2]
}

export async function POST(req: NextRequest) {
  try {
    const data = await req.json() as SetRoiRequest;
    const { sourceUrl, roi } = data;
    
    if (!sourceUrl || !roi || roi.length !== 4) {
      return NextResponse.json(
        { error: '无效的请求参数' }, 
        { status: 400 }
      );
    }
    
    // 格式化ROI坐标，确保是整数
    const formattedRoi = roi.map(coord => Math.round(coord));
    
    // 向Python后端API发送请求
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/set_roi`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        source_url: sourceUrl,
        roi: formattedRoi
      }),
    });
    
    if (!response.ok) {
      const error = await response.text();
      console.error('Error setting ROI:', error);
      return NextResponse.json(
        { error: '设置ROI失败' }, 
        { status: response.status }
      );
    }
    
    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error processing ROI request:', error);
    return NextResponse.json(
      { error: '处理请求时发生错误' }, 
      { status: 500 }
    );
  }
} 