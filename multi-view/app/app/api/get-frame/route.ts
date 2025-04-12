import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // 1. Parse the request body to get the RTSP URL
    const body = await request.json();
    const rtspUrl = body.url;

    // 2. Validate if the URL was provided
    if (!rtspUrl || typeof rtspUrl !== 'string') {
      return NextResponse.json(
        { error: 'Missing or invalid \'url\' in request body' },
        { status: 400 } // Bad Request
      );
    }

    console.log(`API: Received request for frame from: ${rtspUrl}`);

    // 3. Simulate processing and always return the fixed data
    const responseData = {
      frameDataUrl: '/images/placeholder-image.jpg', // Fixed image path
      width: 1920,
      height: 1080,
    };

    // 4. Return the successful JSON response
    return NextResponse.json(responseData);

  } catch (error) {
    // Handle potential JSON parsing errors or other unexpected issues
    console.error('[API GET-FRAME] Error:', error);
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
