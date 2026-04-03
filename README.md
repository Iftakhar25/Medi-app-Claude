# 🩺 FamilyMed AI
### AI-powered family medical records manager — built with Streamlit & Gemini 2.5 Flash

---

## ✨ Features

- 📷 **Camera capture** — take photos of prescriptions/reports directly in-app
- 🔍 **Blur detection** — automatically rejects blurry, unreadable photos
- 🤖 **Gemini 2.5 Flash AI** — identifies diseases, reads medicines, classifies documents
- 🗂️ **Smart disease vaults** — records auto-sorted into colour-coded boxes per person per condition
- 👤 **Profile pictures** — set a selfie above each person's health vaults for easy identification
- 📱 **Mobile-friendly** — designed to work beautifully on phones

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API Key
- Visit [Google AI Studio](https://aistudio.google.com)
- Create a free API key
- Either paste it in the app sidebar, or set it as an environment variable:

```bash
export GEMINI_API_KEY="your_key_here"
```

### 3. Run the app
```bash
streamlit run app.py
```

---

## 📱 How to Use

### Store Data
1. Open the app and tap **Store Data**
2. *(Optional)* Toggle the camera to take a profile selfie
3. Enter your **name** and optionally the **disease/condition**
4. Point the camera at your prescription or report
5. Tap **Add photo to collection** (repeat for multiple pages)
6. Tap **Analyze & Save** — Gemini reads everything and files it automatically

### Explore Data
1. Tap **Explore Data** from the home screen
2. See all disease vaults for every family member
3. Use the search bar to filter by name or condition
4. Click any vault to expand it and view documents, medicines, and AI analysis

---

## 📁 Data Storage

All data is stored **locally** in a `medical_data/` folder:
```
medical_data/
├── records.json      ← structured health metadata
├── profiles/         ← profile pictures (.jpg)
└── reports/          ← medical document photos (.jpg)
```

No data is ever sent to the cloud (except the images sent to Gemini for analysis).

---

## 🔧 Customisation

| Setting | How to change |
|---|---|
| Blur threshold | Adjust `threshold=180` in `check_blur()` (lower = stricter) |
| Image quality | Adjust `quality=88` in `compress_image()` |
| Gemini model | Change `'gemini-2.5-flash'` in `analyze_with_gemini()` |
| Colour palette | Edit the `PALETTE` list at the top of `app.py` |

---

## 💡 Tips

- Good lighting makes a huge difference for AI accuracy
- For lab reports, make sure all key numbers/values are in frame
- If a disease isn't detected correctly, type it manually in the optional field
- Multiple family members can share the same app — each gets their own vaults

---

*Built with ❤️ using Streamlit + Google Gemini 2.5 Flash*
