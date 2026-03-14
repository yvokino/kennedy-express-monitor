# Kennedy Express Lane Monitor

Automatically scrapes [expresschi.com](https://expresschi.com/) every 15 minutes using GitHub Actions to track the Kennedy Expressway (I-90/94) reversible express lane status — direction, speed, travel time, and congestion.

After 1–2 weeks, run the analysis script to see open/close patterns.

## Files

- `scrape.py` — Fetches expresschi.com and appends a row to the CSV
- `analyze.py` — Generates a pattern summary report from the collected data
- `.github/workflows/scrape.yml` — GitHub Actions config (runs every 15 min)
- `data/kennedy_express_log.csv` — Auto-generated data log

## Setup Instructions

### Step 1: Create a GitHub Account

Go to [github.com/signup](https://github.com/signup) and create a free account.

### Step 2: Create a New Repository

1. Click the **+** button (top right) → **New repository**
2. Name it `kennedy-express-monitor`
3. Set it to **Public** (free unlimited Actions minutes)
4. Check **"Add a README file"** (we'll replace it)
5. Click **Create repository**

### Step 3: Upload the Project Files

**Option A — Browser upload (easiest):**

1. In your new repo, click **"Add file"** → **"Upload files"**
2. Drag and drop ALL files from this project (keeping folder structure)
3. Click **"Commit changes"**
4. Repeat for the `.github/workflows/` folder if needed

**Option B — Terminal (faster):**

```bash
# Clone your new empty repo
git clone https://github.com/YOUR_USERNAME/kennedy-express-monitor.git
cd kennedy-express-monitor

# Copy all project files into this folder, then:
git add .
git commit -m "Initial setup: Kennedy express lane monitor"
git push
```

### Step 4: Enable GitHub Actions

1. Go to your repo on GitHub
2. Click the **"Actions"** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**
4. You should see the workflow "Scrape Kennedy Express Lane Status"

### Step 5: Test It Manually

1. In the **Actions** tab, click on the workflow name
2. Click **"Run workflow"** → **"Run workflow"** (green button)
3. Wait ~30 seconds, then check the `data/` folder — you should see `kennedy_express_log.csv` with one row

### Step 6: Let It Run

That's it! The scraper will now run every 15 minutes automatically. Come back in 1–2 weeks.

### Step 7: Analyze the Data

After collecting data, you can either:

**A) Download and analyze locally:**
```bash
git pull  # get latest data
python analyze.py
```

**B) Bring the CSV back to Claude:**
Download `data/kennedy_express_log.csv` from your repo and upload it here — I'll analyze the patterns for you.

## Notes

- Times are logged in **UTC**. Chicago is UTC-5 (CDT) or UTC-6 (CST).
- GitHub Actions cron can drift by a few minutes — this is normal and fine for pattern analysis.
- The scraper logs a `SCRAPE_FAILED` row if the site is unreachable, so you can track reliability.
- Data source: [IDOT](https://idot.illinois.gov/) via [expresschi.com](https://expresschi.com/)
