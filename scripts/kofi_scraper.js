/**
 * Ko-fi Chapter Scraper
 * 
 * Chạy script này trong browser console (F12 -> Console) khi đang ở trang Ko-fi chapter.
 * Script sẽ extract nội dung chapter và tự động chuyển sang chapter tiếp theo.
 * 
 * Cách sử dụng:
 * 1. Mở trang Ko-fi chapter trong Chrome
 * 2. Mở Developer Tools (F12)
 * 3. Paste toàn bộ code này vào Console
 * 4. Gọi: await scrapeChapter() để lấy 1 chapter
 * 5. Hoặc: await scrapeMultipleChapters(5) để lấy 5 chapters liên tiếp
 */

// Cấu hình
const CONFIG = {
    // Delay giữa các chapter (ms) để tránh bị rate limit
    delayBetweenChapters: 2000,
    // Selector cho link ">> Next Chapter"
    nextChapterSelectors: [
        'a[href*="ko-fi.com/post"]',
        'a:contains("Next Chapter")',
        'a:contains(">> Next")'
    ]
};

/**
 * Extract nội dung từ trang hiện tại
 * Ko-fi sử dụng Shadow DOM nên cần truy cập vào .article-host shadowRoot
 */
function extractChapterContent() {
    // Lấy title từ heading (nằm ngoài Shadow DOM)
    const titleElement = document.querySelector('h1') || document.querySelector('h2');
    const postTitle = titleElement ? titleElement.innerText.trim() : document.title;

    // Tìm Shadow DOM container của Ko-fi
    const articleHost = document.querySelector('.article-host');
    let rawText = '';
    let nextChapterLink = null;

    if (articleHost && articleHost.shadowRoot) {
        // Nội dung nằm trong Shadow DOM
        const shadowRoot = articleHost.shadowRoot;
        const frView = shadowRoot.querySelector('.fr-view');

        if (frView) {
            // Sử dụng innerText để giữ nguyên line breaks
            rawText = frView.innerText;
        } else {
            rawText = shadowRoot.textContent || '';
        }

        // Tìm link next chapter trong Shadow DOM
        const shadowLinks = Array.from(shadowRoot.querySelectorAll('a'));
        for (const link of shadowLinks) {
            const text = link.innerText.toLowerCase();
            if (text.includes('next chapter') || text.includes('>> next')) {
                nextChapterLink = link.href;
                break;
            }
        }
    } else {
        // Fallback: tìm trong DOM bình thường
        const postContainer = document.querySelector('.kfds-c-post-content')
            || document.querySelector('[data-testid="post-content"]')
            || document.querySelector('.post-body')
            || document.body;

        rawText = postContainer.innerText;
    }

    // Nếu chưa tìm thấy next chapter link, tìm trong DOM chính
    if (!nextChapterLink) {
        nextChapterLink = findNextChapterLink();
    }

    // Làm sạch text
    const cleanedText = cleanText(rawText);

    return {
        title: postTitle,
        url: window.location.href,
        content: cleanedText,
        nextChapterUrl: nextChapterLink,
        extractedAt: new Date().toISOString()
    };
}


/**
 * Làm sạch text, loại bỏ navigation và noise
 */
function cleanText(text) {
    // Tách theo dòng
    let lines = text.split('\n');

    // Loại bỏ các dòng không cần thiết
    const skipPatterns = [
        /^>> Next Chapter/i,
        /^<< Previous Chapter/i,
        /^Support me/i,
        /^Buy me a coffee/i,
        /^Ko-fi/i,
        /^See all$/i,
        /^Terms$/i,
        /^Privacy$/i,
        /^\d+ comments?$/i,
        /^Share$/i,
        /^Like$/i,
        /^Your page$/i
    ];

    lines = lines.filter(line => {
        const trimmed = line.trim();
        if (trimmed.length === 0) return false;
        if (trimmed.length < 3) return false;

        for (const pattern of skipPatterns) {
            if (pattern.test(trimmed)) return false;
        }

        return true;
    });

    // Ghép lại
    return lines.join('\n\n');
}

/**
 * Tìm link đến chapter tiếp theo
 */
function findNextChapterLink() {
    // Tìm theo text
    const links = Array.from(document.querySelectorAll('a'));

    for (const link of links) {
        const text = link.innerText.toLowerCase();
        if (text.includes('next chapter') || text.includes('>> next')) {
            return link.href;
        }
    }

    // Tìm theo href pattern
    const postLinks = links.filter(l => l.href.includes('ko-fi.com/post'));
    if (postLinks.length > 0) {
        // Lấy link cuối cùng (thường là next chapter)
        return postLinks[postLinks.length - 1].href;
    }

    return null;
}

/**
 * Parse chapter number và volume từ title
 */
function parseChapterInfo(title) {
    // Pattern: [Vol. X] Chapter Y: Title hoặc Chapter Y-Z
    const volMatch = title.match(/Vol\.?\s*(\d+)/i);
    const chapterMatch = title.match(/Chapter\s*(\d+)(?:\s*[-–]\s*(\d+))?/i);

    return {
        volume: volMatch ? parseInt(volMatch[1]) : 1,
        chapterStart: chapterMatch ? parseInt(chapterMatch[1]) : null,
        chapterEnd: chapterMatch && chapterMatch[2] ? parseInt(chapterMatch[2]) : null
    };
}

/**
 * Tách nội dung thành từng chapter riêng biệt
 */
function splitIntoChapters(content, title) {
    const info = parseChapterInfo(title);
    const chapters = [];

    // Pattern để tìm tiêu đề chapter trong nội dung
    // Ví dụ: [Vol. 9] Chapter 137: The Strange Loot Has Increased!
    const chapterPattern = /\[Vol\.\s*\d+\]\s*Chapter\s*(\d+):\s*([^\n]+)/gi;

    const matches = [...content.matchAll(chapterPattern)];

    if (matches.length > 0) {
        for (let i = 0; i < matches.length; i++) {
            const match = matches[i];
            const chapterNum = parseInt(match[1]);
            const chapterTitle = match[2].trim();

            // Lấy nội dung từ match này đến match tiếp theo (hoặc cuối file)
            const startIndex = match.index + match[0].length;
            const endIndex = i < matches.length - 1 ? matches[i + 1].index : content.length;
            const chapterContent = content.substring(startIndex, endIndex).trim();

            chapters.push({
                id: chapterNum,
                volume: info.volume,
                title: chapterTitle,
                content: chapterContent
            });
        }
    } else {
        // Không tìm thấy pattern, trả về toàn bộ content như 1 chapter
        chapters.push({
            id: info.chapterStart || 1,
            volume: info.volume,
            title: title,
            content: content
        });
    }

    return chapters;
}

/**
 * Scrape 1 chapter từ trang hiện tại
 */
async function scrapeChapter() {
    console.log('📖 Đang extract chapter từ:', window.location.href);

    const data = extractChapterContent();
    const chapters = splitIntoChapters(data.content, data.title);

    console.log(`✅ Đã extract ${chapters.length} chapter(s)`);
    chapters.forEach(ch => {
        console.log(`   - Chapter ${ch.id}: ${ch.title} (${ch.content.length} ký tự)`);
    });

    if (data.nextChapterUrl) {
        console.log('➡️ Next chapter:', data.nextChapterUrl);
    }

    return {
        ...data,
        chapters: chapters
    };
}

/**
 * Scrape nhiều chapters liên tiếp
 */
async function scrapeMultipleChapters(count = 5) {
    const allChapters = [];
    let currentUrl = window.location.href;

    console.log(`🚀 Bắt đầu scrape ${count} bài viết...`);

    for (let i = 0; i < count; i++) {
        console.log(`\n📖 [${i + 1}/${count}] Đang xử lý...`);

        const data = await scrapeChapter();
        allChapters.push(...data.chapters);

        if (data.nextChapterUrl && i < count - 1) {
            console.log(`⏳ Chờ ${CONFIG.delayBetweenChapters}ms rồi chuyển sang chapter tiếp...`);
            await new Promise(r => setTimeout(r, CONFIG.delayBetweenChapters));

            // Chuyển sang chapter tiếp
            window.location.href = data.nextChapterUrl;

            // Lưu progress vào localStorage
            localStorage.setItem('kofi_scraper_progress', JSON.stringify({
                currentIndex: i + 1,
                totalCount: count,
                chapters: allChapters
            }));

            // Dừng script vì trang sẽ reload
            return {
                message: 'Đang chuyển trang, chạy lại script ở trang mới để tiếp tục',
                chapters: allChapters,
                nextUrl: data.nextChapterUrl
            };
        } else if (!data.nextChapterUrl) {
            console.log('⚠️ Không tìm thấy link chapter tiếp theo. Dừng lại.');
            break;
        }
    }

    console.log(`\n✅ Hoàn thành! Đã scrape ${allChapters.length} chapters.`);
    return {
        chapters: allChapters,
        totalChapters: allChapters.length
    };
}

/**
 * Export chapters thành XML format phù hợp với parse_chapters.py
 */
function exportToXML(chapters) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<chapters>\n';

    for (const chapter of chapters) {
        xml += `  <chapter number="${chapter.id}" volume="${chapter.volume}">\n`;
        xml += `    <title>${escapeXML(chapter.title)}</title>\n`;
        xml += `    <text>${escapeXML(chapter.content)}</text>\n`;
        xml += `  </chapter>\n`;
    }

    xml += '</chapters>';
    return xml;
}

function escapeXML(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

/**
 * Download file
 */
function downloadFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    console.log(`📥 Đã download: ${filename}`);
}

/**
 * Scrape và export ngay
 */
async function scrapeAndExport() {
    const result = await scrapeChapter();
    const xml = exportToXML(result.chapters);

    // Tạo filename từ chapter range
    const chapterIds = result.chapters.map(c => c.id);
    const minCh = Math.min(...chapterIds);
    const maxCh = Math.max(...chapterIds);
    const filename = minCh === maxCh
        ? `ch${minCh}.vn.txt`
        : `ch${minCh}_${maxCh}.vn.txt`;

    downloadFile(xml, filename);
    return result;
}

// Hiển thị hướng dẫn
console.log(`
╔════════════════════════════════════════════════════════════╗
║           Ko-fi Chapter Scraper - Sẵn sàng!                ║
╠════════════════════════════════════════════════════════════╣
║ Các lệnh có thể sử dụng:                                    ║
║                                                              ║
║ 1. scrapeChapter()                                          ║
║    → Lấy nội dung từ trang hiện tại                         ║
║                                                              ║
║ 2. scrapeAndExport()                                        ║
║    → Scrape và download file XML ngay                       ║
║                                                              ║
║ 3. scrapeMultipleChapters(5)                                ║
║    → Scrape 5 bài viết liên tiếp (tự động navigate)         ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
`);
