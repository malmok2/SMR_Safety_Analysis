/* 크로미움 실행 파일을 찾는다.
 *   1) 환경변수 CHROME_PATH
 *   2) PLAYWRIGHT_BROWSERS_PATH(또는 /opt/pw-browsers) 밑에 설치된 chromium
 *   3) 그래도 없으면 설치된 Chrome 채널
 */
const fs = require('fs');
const path = require('path');

function findChromium(){
  if (process.env.CHROME_PATH) return { executablePath: process.env.CHROME_PATH };
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  try {
    const dirs = fs.readdirSync(root).filter(d => /^chromium-/.test(d)).sort().reverse();
    for (const d of dirs) {
      for (const rel of ['chrome-linux/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium',
                         'chrome-win/chrome.exe']) {
        const p = path.join(root, d, rel);
        if (fs.existsSync(p)) return { executablePath: p };
      }
    }
  } catch (e) { /* 설치 경로 없음 — 채널로 넘어간다 */ }
  return { channel: 'chrome' };
}
module.exports = { findChromium };
