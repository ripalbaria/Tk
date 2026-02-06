const fs = require('fs');

try {
    const html = fs.readFileSync('debug_page.html', 'utf8');
    // Extract the main obfuscated array seen in 156716.jpg
    const arrayMatch = html.match(/var\s+(_0x[a-f0-9]+)\s*=\s*\[(.*?)\]/);
    
    if (arrayMatch) {
        let rawData = arrayMatch[2];
        // Join pieces and handle the '0%' pattern from Termux screenshots
        let joined = rawData.replace(/['"\s]/g, '').split(',').join('');
        let cleaned = joined.replace(/0%/g, '%');
        let decoded = decodeURIComponent(cleaned);
        
        // Final search for Amazon IVS playback URL (Toolkit style)
        const awsPattern = /https?:\/\/[^\s"'<>]*?playback\.live-video\.net[^\s"'<>]*?m3u8[^\s"'<>]*/;
        const match = decoded.match(awsPattern);
        
        if (match) {
            console.log(match[0]);
        } else {
            // Fallback: search the entire decoded blob for any m3u8
            const anyM3u8 = decoded.match(/https?:\/\/[^\s"'<>]*?\.m3u8[^\s"'<>]*/);
            if (anyM3u8) console.log(anyM3u8[0]);
        }
    }
} catch (e) {
    console.error("Decoder Error: " + e.message);
}
