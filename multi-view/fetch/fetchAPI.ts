export const uploadRtspUrls = async (rtspUrls: string[]) => {
    const response = await fetch('/api/uploadRtspUrls', {
        method: 'POST',
        body: JSON.stringify({ rtspUrls }),
    });
    return response.json();
};


