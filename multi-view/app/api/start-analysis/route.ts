import { NextResponse } from 'next/server';

// Simulate processing delay (optional)
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export async function POST(request: Request) {
  try {
    // 1. Parse the incoming request body
    const body = await request.json();
    const { rtsp_address, polygon_points, crossing_lines } = body;

    // 2. Basic validation (add more specific validation if needed)
    if (!rtsp_address || !Array.isArray(polygon_points) || !Array.isArray(crossing_lines)) {
      return NextResponse.json(
        { error: 'Missing or invalid parameters in request body. Required: rtsp_address, polygon_points, crossing_lines' },
        { status: 400 } // Bad Request
      );
    }

    console.log(`API: Received start analysis request for: ${rtsp_address}`);
    console.log('API: Polygon Points:', polygon_points);
    console.log('API: Crossing Lines:', crossing_lines);

    // 3. Simulate backend processing time (optional)
    await delay(1500); // Simulate 1.5 seconds processing

    // 4. Construct the successful response with the fixed MJPEG URL
    const responseData = {
      mjpegStreamUrl: 'http://47.97.71.139:8003/video_feed', // Your fixed stream URL
    };

    // 5. Return the successful JSON response
    return NextResponse.json(responseData);

  } catch (error) {
    // Handle potential JSON parsing errors or other unexpected issues
    console.error('[API START-ANALYSIS] Error:', error);
    let errorMessage = 'Internal Server Error';
     if (error instanceof SyntaxError) { // More specific error for JSON parsing
        errorMessage = 'Invalid JSON in request body';
        return NextResponse.json({ error: errorMessage }, { status: 400 }); // Bad Request
    }
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    );
  }
}

// Optional: Add a GET handler if needed, otherwise it will return 405 Method Not Allowed
// export async function GET(request: Request) {
//   return NextResponse.json({ message: 'Method Not Allowed' }, { status: 405 });
// }
