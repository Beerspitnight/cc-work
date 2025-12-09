# Claude-Powered Honda Scraper

This scraper uses Claude AI to extract vehicle data from dealership websites, making it more robust and adaptable than traditional DOM-based scraping.

## Features

- **AI-Powered Extraction**: Uses Claude to understand and extract data from HTML
- **More Reliable**: No brittle CSS selectors that break when sites change
- **Intelligent Parsing**: Claude understands context (e.g., sale price vs MSRP)
- **Adaptive**: Works across different dealership website layouts

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key

### 3. Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Option B: Create .env file**
```bash
cp .env.example .env
# Edit .env and add your API key
```

**Option C: Direct in Code (Not Recommended)**
Edit `scraper-claude.js` line 9:
```javascript
apiKey: 'your-actual-api-key-here'
```

## Usage

### Test on Single Page

Test the Claude extraction on a single page first:

```bash
node test-claude-single.js
```

This will show you Claude's raw response and the extracted JSON data.

### Run Full Scraper

Once testing looks good, run the full scraper:

```bash
node scraper-claude.js
```

This will:
1. Scrape all 6 Honda dealerships
2. Extract vehicle data using Claude AI
3. Filter for 2019-2023 Accords (Sport, EX-L, Sport-L trims)
4. Save matching vehicles to `honda-accords-claude.csv`

## How It Works

### Traditional Approach (Old Scrapers)
```javascript
// Brittle - breaks when HTML changes
const mileage = document.querySelector('.mileage-class-name').textContent;
const price = document.querySelector('[data-price]').textContent;
```

### Claude Approach (New Scraper)
```javascript
// Robust - Claude understands the HTML
const data = await extractWithClaude(html);
// Returns: { year: 2022, mileage: 35000, price: 24500, ... }
```

### Advantages

1. **No DOM Hunting**: Don't need to find the right CSS selectors
2. **Context Aware**: Claude knows sale price ≠ MSRP
3. **Adaptive**: Works even when dealership site layouts change
4. **Simpler Code**: No complex DOM traversal logic

### Disadvantages

1. **API Costs**: ~$0.50-$2.00 per 100 pages (using Haiku model)
2. **Slower**: API calls take ~1-2 seconds each
3. **Rate Limits**: Subject to Anthropic API rate limits
4. **Requires Key**: Need valid Anthropic API key

## Cost Estimate

Using Claude 3.5 Haiku (cheapest model):
- Input: ~$0.25 per million tokens
- Output: ~$1.25 per million tokens

For 100 vehicle pages:
- ~500KB HTML each = 250k tokens total
- Cost: **~$0.50 - $1.00** for 100 pages

## Troubleshooting

### "Authentication error" or "Invalid API key"
- Make sure `ANTHROPIC_API_KEY` is set correctly
- Check that your API key is active in the Anthropic console

### "Could not find JSON in Claude response"
- Claude's response format might have changed
- Check the raw response in `test-claude-single.js`
- Adjust the `extractJsonFromClaude` function if needed

### "Rate limit exceeded"
- Add longer delays between requests (increase `waitForTimeout`)
- Upgrade your Anthropic API tier

### No vehicles found
- Check that criteria in `CRITERIA` object matches your needs
- Run `test-claude-single.js` to see what data Claude is extracting
- Verify the sitemap URLs are correct for the dealership

## Criteria

Current search criteria:
- **Years**: 2019-2023
- **Trims**: Sport, EX-L, Sport-L, EXL
- **Max Mileage**: 60,000 miles
- **Max Price**: $25,000

To modify, edit the `CRITERIA` object in `scraper-claude.js`:

```javascript
const CRITERIA = {
    make: 'honda',
    model: 'accord',
    trims: ['sport', 'ex-l', 'sport-l', 'exl'],
    minYear: 2019,
    maxYear: 2023,
    maxMileage: 60000,
    maxPrice: 25000
};
```

## Comparison with Traditional Scrapers

| Feature | Traditional (`scraper-final.js`) | Claude (`scraper-claude.js`) |
|---------|----------------------------------|------------------------------|
| Speed | Fast (~500ms/page) | Slower (~2s/page) |
| Cost | Free | ~$0.01 per page |
| Reliability | Breaks when HTML changes | Adapts to HTML changes |
| Accuracy | Depends on selectors | High (AI understanding) |
| Setup | None | Requires API key |

## Files

- `scraper-claude.js` - Main Claude-powered scraper
- `test-claude-single.js` - Test script for single page
- `.env.example` - Example environment variable file
- `CLAUDE-SCRAPER-README.md` - This file

## Next Steps

1. Test with `test-claude-single.js` to verify Claude extraction works
2. Run `scraper-claude.js` on a small batch (maybe just 1 dealership)
3. Review the output CSV to ensure data quality
4. Scale up to all dealerships once confident

## Support

For issues with:
- **Scraper logic**: Check this README and test scripts
- **Claude API**: Visit https://docs.anthropic.com/
- **Playwright**: Visit https://playwright.dev/docs/intro
