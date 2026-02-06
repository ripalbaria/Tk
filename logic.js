const fs = require('fs');
try {
    const html = fs.readFileSync('debug_page.html', 'utf8');
    const arrayMatch = html.match(/var\s+(_0x[a-f0-9]+)\s*=\s*\[(.*?)\]/);
    if (arrayMatch) {
        let rawData = arrayMatch[2].replace(/['"\s]/g, '').split(',');
        // Player logic: Har piece ko individually check karna
        let decodedStrings = rawData.map(p => {
            try { return decodeURIComponent(p.replace(/0%/g, '%')); }
            catch (e) { return ""; }
        });
        let finalOutput = decodedStrings.join('');
        // Search for the AWS link pattern
        let awsLink = finalOutput.match(/https?:\/\/[^\s"'<>]*?playback\.live-video\.net[^\s"'<>]*?m3u8[^\s"'<>]*/);
        if (awsLink) console.log(awsLink[0]);
        else console.log("LINK_NOT_FOUND_IN_DECODED_DATA");
    }
} catch (e) { console.log("ERROR: " + e.message); }
