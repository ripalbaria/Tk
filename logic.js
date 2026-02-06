const fs = require('fs');

try {
    const html = fs.readFileSync('debug_page.html', 'utf8');
    // Screenshot 156716 ke mutabiq array dhoondo
    const arrayMatch = html.match(/var\s+_0x477048\s*=\s*\[(.*?)\]/);
    
    if (arrayMatch) {
        let rawData = arrayMatch[1];
        // Quotes aur space hata kar array ke pieces nikalo
        let pieces = rawData.replace(/['"\s]/g, '').split(',');
        
        // Browser logic: pieces ko join karo aur cleanup apply karo
        let fullString = pieces.join('');
        
        // Humne dekha ki extra '0' pattern hai: 0%20 -> %20
        let cleaned = fullString.replace(/0%/g, '%');
        
        // Final decoding
        let decoded = decodeURIComponent(cleaned);
        
        // Search for Amazon IVS Link pattern from Toolkit
        const awsPattern = /https?:\/\/[^\s"'<>]*?playback\.live-video\.net[^\s"'<>]*?m3u8[^\s"'<>]*/;
        const match = decoded.match(awsPattern);
        
        if (match) {
            console.log(match[0]);
        } else {
            // Agar seedha nahi mila, to pure decoded text me dhoondo
            console.log("NOT_FOUND_BUT_DECODED");
            console.log(decoded.substring(0, 500)); 
        }
    }
} catch (e) {
    console.log("ERROR: " + e.message);
}

