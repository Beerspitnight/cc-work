const { chromium } = require('playwright');

// Improved Carvana reconnaissance
async function reconCarvanaV2() {
    console.log('🔍 Carvana.com Reconnaissance v2\n');
    console.log('════════════════════════════════════════════════════════\n');

    const browser = await chromium.launch({
        headless: false,  // Show browser for manual inspection
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });

    const page = await context.newPage();

    // Capture network requests - looking for API endpoints
    const apiCalls = [];
    const xhrCalls = [];

    page.on('request', request => {
        const url = request.url();
        const resourceType = request.resourceType();

        if (resourceType === 'xhr' || resourceType === 'fetch') {
            xhrCalls.push({
                url: url,
                method: request.method(),
                resourceType: resourceType,
                postData: request.postData()
            });
        }

        if (url.includes('api') || url.includes('graphql') || url.includes('search') || url.includes('inventory')) {
            apiCalls.push({
                url: url,
                method: request.method(),
                headers: request.headers()
            });
        }
    });

    try {
        // Try different Carvana URLs
        const searchUrls = [
            'https://www.carvana.com/cars/honda-accord',
            'https://www.carvana.com/cars?make=Honda&model=Accord',
            'https://www.carvana.com/search?q=honda+accord'
        ];

        for (const testUrl of searchUrls) {
            console.log(`\n🌐 Testing: ${testUrl}`);

            try {
                await page.goto(testUrl, {
                    waitUntil: 'domcontentloaded',
                    timeout: 45000
                });

                console.log('✓ Page loaded');
                await page.waitForTimeout(8000); // Wait for dynamic content

                // Get page title to verify we're on a valid page
                const title = await page.title();
                console.log(`   Title: ${title}`);

                // Check if we found vehicles
                const vehicleCount = await page.evaluate(() => {
                    // Try multiple selectors
                    const selectors = [
                        '[data-qa="base-vehicle-card"]',
                        '[class*="vehicle-card"]',
                        '[class*="VehicleCard"]',
                        '[data-test*="vehicle"]',
                        'a[href*="/vehicle/"]'
                    ];

                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            return { selector, count: elements.length };
                        }
                    }

                    return { selector: 'none', count: 0 };
                });

                console.log(`   Vehicle cards found: ${vehicleCount.count} (using selector: ${vehicleCount.selector})`);

                if (vehicleCount.count > 0) {
                    console.log('   ✅ This URL works!');

                    // Extract sample vehicle data
                    const sampleVehicles = await page.evaluate((selector) => {
                        const cards = Array.from(document.querySelectorAll(selector)).slice(0, 3);
                        return cards.map(card => ({
                            html: card.outerHTML.substring(0, 500),
                            text: card.textContent.substring(0, 300),
                            classes: card.className
                        }));
                    }, vehicleCount.selector);

                    console.log('\n   📦 Sample vehicle cards:');
                    sampleVehicles.forEach((v, i) => {
                        console.log(`\n   [${i+1}] Classes: ${v.classes}`);
                        console.log(`       Text: ${v.text.replace(/\s+/g, ' ').trim()}`);
                    });

                    break; // Found working URL
                }

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }

        console.log('\n════════════════════════════════════════════════════════');
        console.log('🌐 XHR/FETCH CALLS:');
        console.log('════════════════════════════════════════════════════════\n');

        if (xhrCalls.length > 0) {
            xhrCalls.forEach((call, i) => {
                console.log(`[${i+1}] ${call.method} ${call.resourceType}`);
                console.log(`    ${call.url}`);
                if (call.postData) {
                    console.log(`    POST Data: ${call.postData.substring(0, 200)}`);
                }
                console.log('');
            });
        } else {
            console.log('⚠️  No XHR/Fetch calls detected\n');
        }

        console.log('════════════════════════════════════════════════════════');
        console.log('🔑 API CALLS:');
        console.log('════════════════════════════════════════════════════════\n');

        if (apiCalls.length > 0) {
            apiCalls.forEach((call, i) => {
                console.log(`[${i+1}] ${call.method}`);
                console.log(`    ${call.url}\n`);
            });
        } else {
            console.log('⚠️  No obvious API calls detected\n');
        }

        console.log('\n✅ Reconnaissance complete!');
        console.log('💡 Browser will stay open for 3 minutes for manual inspection');
        console.log('💡 Check the Network tab in DevTools for more details!\n');

        // Keep browser open for manual inspection
        await new Promise(resolve => setTimeout(resolve, 180000)); // 3 minutes

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await browser.close();
    }
}

reconCarvanaV2().catch(console.error);
