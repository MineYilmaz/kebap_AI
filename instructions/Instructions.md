# Proje Talimatlari

Bu dosya projenin calisma kurallarini tanimlar. Projeye katkida bulunan herkes
(insan veya AI) bu kurallara uyar.

## 1. Arac zinciri

- Python paket ve proje yonetimi yalnizca `uv` ile yapilir. `pip install` veya
  `python -m venv` kullanilmaz.
- Python surumu `.python-version` dosyasinda tanimlidir: **3.11**.
- Bagimliliklar `pyproject.toml` icinde tanimlanir; `uv.lock` degisikliklerle
  birlikte guncel tutulur ve commit edilir.
- Testler pytest ile yazilir ve `uv run pytest` ile calistirilir. Canli servis
  gerektiren integration testleri varsayilan calistirmadan haric tutulur.

## 2. Dinamik yapilandirma ve hardcoding yasagi

- Ortama gore degisebilecek ayarlar, yollar, URL'ler ve gizli degerler uygulama
  koduna gomulmez.
- Yapilandirma `.env` dosyasindan `python-dotenv` araciligiyla okunur.
  Ayarlar `kebap_ai/config.py` icindeki `Settings` ile tanimlanir ve uygulama
  tarafindan `get_settings()` uzerinden alinir.
- Yeni bir ayar eklerken:
  1. `.env.example` dosyasina aciklamali, gizli olmayan bir ornek ekleyin.
  2. Gercek degeri yalnizca yerel `.env` dosyasina koyun.
  3. `Settings` sinifina typed bir alan ve gerekiyorsa guvenli varsayilan ekleyin.
  4. Ayari uygulamada `get_settings()` uzerinden kullanin.
  5. Ayarin davranisini test edin.
- Dosya yollarini sabit mutlak yollarla degil, ilgili modulun konumunu temel alan
  `pathlib.Path` ifadeleriyle olusturun.
- Sabitler yalnizca ortamdan degismemesi gereken, gercekten sabit degerler icin
  kullanilir.

## 3. Ortam degiskenleri

- `.env` ve `.env.local` gercek degerleri tutar ve `.gitignore` tarafindan
  dislanir; asla Git'e commit edilmez. DeepEval Confident AI girisi API key'i
  varsayilan olarak `.env.local` dosyasina kaydedebilir.
- `.env.example` gizli bilgi icermez, commit edilir ve gerekli ayarlari aciklar.
- Ilk kurulumda PowerShell ile `.env` dosyasini olusturun:

  ```powershell
  Copy-Item .env.example .env
  ```

- Projede kullanilan ayarlar `.env.example` ile `Settings` arasinda tutarli
  tutulur. Buna uygulama, sunucu, chatbot ve gerekiyorsa model/judge ayarlari
  dahildir.
- Token, API anahtari ve sifreleri loglara, test ciktisina veya ornek
  yapilandirma dosyalarina yazmayin.

## 4. Hata ayiklama ve loglama

- `.env` icindeki `DEBUG=true` debug kipini etkinlestirir. Uygulama debug
  ayarini `Settings` uzerinden alir; debug kipi uretim ortaminda kapali tutulur.
- Log seviyesi `LOG_LEVEL` yapilandirmasindan belirlenir. `DEBUG=true` iken
  debug loglamasi etkinlestirilir; log kurulumu merkezi bir
  `config.setup_logging()` fonksiyonunda yapilir.
- VS Code hata ayiklama ayarlari `.vscode/launch.json` icinde tutulur ve `.env`
  dosyasini yukler. Ayarlar su senaryolari kapsamalidir:
  - **Uygulamayi Debug Et** — Flask uygulamasini baslatir.
  - **Acik Dosyayi Debug Et** — editorde acik olan Python dosyasini calistirir.
  - **Testleri Debug Et** — pytest'i debugger altinda calistirir.
- Hata ayiklama icin `print()` kullanmayin; `logging` kullanin.
- Loglarda gizli degerleri veya hassas istek basliklarini yazdirmayin.

## 5. Test

- Her yeni modul ve davranis icin `tests/` altina pytest testi ekleyin.
- Testlerde ortam degiskenlerini `monkeypatch` ile ayarlayin; gercek `.env`
  dosyasina veya canli servise bagimlilik kurmayin.
- Birim testlerinde HTTP istekleri `httpx.MockTransport` gibi mock'larla
  taklit edilir. Canli servis testleri `integration` marker'i ile ayrilir ve
  varsayilan test calistirmasina dahil edilmez.
- Test komutlari:

  ```powershell
  uv run pytest
  uv run pytest -m unit
  uv run pytest -m integration -s
  ```

- Pytest ayarlari `pyproject.toml` dosyasinin
  `[tool.pytest.ini_options]` bolumunde tutulur.
- LLM kalite degerlendirme testleri DeepEval kullanir. Eval testlerini
  `uv run deepeval test run tests/evals -m integration` ile calistirin;
  geleneksel pytest testleri `uv run pytest` ile calistirilmaya devam eder.
  Chatbot answer-relevancy degerlendirmesi `ANTHROPIC_API_KEY`,
  `CLAUDE_MODEL`, `CHATBOT_TEST_MESSAGE` ve `CHATBOT_EVAL_THRESHOLD`
  ayarlarini kullanir.

## 6. DeepEval ve Confident AI

- DeepEval gelistirme bagimliligidir ve `pyproject.toml` / `uv.lock` icinde
  tutulur. Kurmak veya guncellemek icin proje kokunde:

  ```powershell
  uv sync --group dev
  uv run deepeval --help
  ```

- DeepEval testleri yerel calisabilir. Test calistirmalarini Confident AI
  hesabinda gormek icin Confident AI hesabinizdan bir API key alin ve CLI
  girisini yapin. Key'i proje kokundeki `.env.local` dosyasinda
  `CONFIDENT_AI_API_KEY=` satirinin esittir isaretinden sonra saklayin. Bu dosya
  Git tarafindan dislanir:

  ```powershell
  notepad .env.local
  ```

  Key'i PowerShell oturumuna yukleyip DeepEval CLI'ye aktararak giris yapin.
  Komut key degerini ekrana yazdirmaz; tamamlaninca oturum degiskenini silin:

  ```powershell
  $env:CONFIDENT_AI_API_KEY = ((Get-Content .env.local | Where-Object { $_ -match '^CONFIDENT_AI_API_KEY=' } | Select-Object -First 1) -replace '^CONFIDENT_AI_API_KEY=', '').Trim()
  if (-not $env:CONFIDENT_AI_API_KEY) { throw "Add the key to .env.local first." }
  try { uv run deepeval login --api-key $env:CONFIDENT_AI_API_KEY } finally { Remove-Item Env:CONFIDENT_AI_API_KEY -ErrorAction SilentlyContinue }
  ```

- Confident AI API key'i `ANTHROPIC_API_KEY` degildir. Confident AI key'i test
  kosularini platforma baglar; `ANTHROPIC_API_KEY` Claude istekleri ve
  Anthropic tabanli judge cagrilari icin kullanilir. Key'leri kaynak koduna,
  `.env.example` dosyasina veya commit'e koymayin.
- Eval calistirmak icin:

  ```powershell
  uv run deepeval test run tests/evals -m integration
  ```

  Henüz `tests/evals` klasorunde eval testi yoksa once bir DeepEval test dosyasi
  ekleyin.
- Basarili CLI girisinden sonra key'i terminalde veya sohbetlerde paylasmayin.
  Confident AI key'i yenilenirse `.env.local` dosyasini da guncelleyin.

## 7. Git

- `.env`, `.env.local`, `.venv`, `__pycache__`, `.pytest_cache`, kapsama
  raporlari ve diger uretilen dosyalar commit edilmez.
- `.env.example`, kaynak kod, testler ve `uv.lock` Git'e dahil edilir.
- Commit'ler kucuk ve anlamli tutulur; mesaj degisikligi ozetler.
- Commit oncesinde ilgili testleri calistirin ve gercek gizli bilgi
  eklenmedigini kontrol edin.

## 8. Bagimlilik ekleme

- Calisma zamani bagimliligi eklemek icin `uv add <paket>` kullanin.
- Gelistirme bagimliligi (test, lint vb.) eklemek icin `uv add --dev <paket>`
  kullanin.
- Paketleri elle `pyproject.toml` veya `uv.lock` dosyasina yazmak yerine `uv`
  komutlariyla yonetin.
- Bagimlilik degisikliginden sonra `uv.lock` dosyasini commit edin; ayni
  kilitlenmis bagimliliklarin her ortamda kurulmasini saglar.
