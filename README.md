<div align="center">

# 📸 Photo & Video Organizer 2.0
### *Next-Gen Local-First Media Sorter & Duplicate Cleaner*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?logo=qt&logoColor=white)](https://pyside.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen)]()
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline%20%7C%20Zero%20Cloud-red?logo=shield&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

<br/>

![Photo & Video Organizer 2.0 Banner](assets/banner_v2.jpg)

**[🇷🇺 Русский](#-организатор-фото-и-видео-20) • [🇬🇧 English](#-photo--video-organizer-20-english)**

</div>

---

<br/>

## 🇷🇺 Организатор фото и видео 2.0

**Photo & Video Organizer 2.0** — это быстрое, полностью автономное десктопное приложение для наведения идеального порядка в семейных и рабочих архивах фотографий и видео.

В отличие от Google Photos, Apple Photos, Mylio или платных аналогов, программа работает **на 100% локально на вашем компьютере**:
* 🔒 **0 байт отправляется в сеть** — ваши личные фото, документы и домашние видео никогда не покинут ваш ПК.
* 💸 **Никаких подписок** — бесплатно, без рекламы и без скрытых платежей.
* ⚡ **Мгновенная сортировка** — обработка терабайтных внешних дисков и карт памяти на максимальной скорости накопителя.

---

### 🗺️ Интерактивная карта интерфейса

Интерфейс спроектирован по принципу *Zero-Friction*: вся мощь сортировки упакована в одно стильное окно размером `585 × 720 px`, где всё понятно без инструкций.

<div align="center">

![Карта кнопок и интерфейса](assets/ui_annotated.svg)

</div>

### 🕹️ Описание блоков и элементов управления

| № | Элемент | Название | Назначение |
|---|---|---|---|
| **1** | **Вырез (Notch)** | `PHOTO-VIDEO-ORGANIZER` | Фирменный статус-бэйдж в стиле Dynamic Island. |
| **2** | **Монитор состояния** | **Экран дисплея** | Монолитный инфо-экран: выводит ход сканирования, имя обрабатываемого файла, статус дубликатов и прогресс-бар в реальном времени. |
| **3** | **Селектор режимов** | `FULL` *(Полная проверка)* | Сортирует фото и видео по папкам `Год/Месяц` на основе EXIF, отсеивает дубликаты в `Duplicates`, а скриншоты — в `Other`. |
| | | `DUPLICATE` *(Поиск дубликатов)* | Сканирует архив и находит одинаковые файлы по криптографическому хэшу SHA-256 без изменения структуры папок. |
| | | `OTHER` *(Прочие файлы)* | Извлекает скриншоты (<100 КБ или по ключевым словам) и документы из фотопотока. |
| **4** | **Сетка папок (2×2)** | `Temp` | **Откуда брать:** папка-источник (сброшенные фото с телефона, флешки фотоаппарата, папка «Загрузки»). |
| | | `Media` | **Куда складывать:** целевая библиотека (автоматически создаются папки `YYYY/MM`). |
| | | `Duplicate` | **Папка дубликатов:** изолированное хранилище найденных копий (файлы не удаляются вслепую). |
| | | `Other` | **Папка прочего:** скриншоты, чеки, нераспознанные форматы. |
| **5** | **Кнопка START** | `START / STOP` | Запуск алгоритма в отдельном потоке `QThread` (интерфейс не зависает). При клике плавно превращается в красную кнопку `STOP`. |
| **6** | **Боковая панель** | `?` *(Справка & Undo)* | Интерактивная справка и кнопка **«Отменить последнюю сортировку»** (возвращает все файлы обратно, если вы ошиблись). |
| | | `🇷🇺 / 🇬🇧 / 🇨🇳` *(Языки)* | Мгновенное переключение языка интерфейса с динамической сменой государственного флага. |
| | | `GitHub` | Прямой переход к исходному коду и обновлениям проекта. |
| | | `Donate` | Кнопка поддержки независимой разработки. |

---

### ✨ Ключевые возможности версии 2.0

* **Точная датировка по EXIF**: Извлекает метаданные `DateTimeOriginal` даже у старых сканов и снимков с профессиональных камер.
* **Поддержка Apple & RAW**: Уверенно читает JPEG, PNG, HEIC, GIF, а также «сырые» форматы фотографов (CR2, CR3, NEF, ARW, DNG, RAF, RW2).
* **Сортировка видео**: Упорядочивает MP4, MOV, MKV, AVI, WEBM, TS по дате создания.
* **Умный фильтр скриншотов**: Автоматически распознает снимки экрана по 15+ языковым паттернам (`screenshot`, `скрин`, `снимок экрана` и т.д.) или объему < 100 КБ.
* **Побайтовое хэширование SHA-256**: Гарантирует, что дубликатом признаются только 100% идентичные файлы, исключая ошибки и потерю фото.
* **Автосохранение путей**: Запоминает ваши папки и язык между запусками.

---

### 🚀 Быстрый запуск

#### Вариант А: Запуск на Windows (в 1 клик)
1. Скачайте репозиторий или релизный ZIP-архив.
2. Запустите `Install.bat` (установит зависимости за 5 секунд).
3. Запустите **`PhotoOrganizer.bat`** (приложение откроется без лишних черных окон консоли).

#### Вариант Б: Сборка в один автономный `.exe` файл
Просто запустите файл **`Build_EXE.bat`** — через минуту в папке `dist/` появится готовый автономный `PhotoVideoOrganizer.exe`.

#### Вариант В: Запуск на macOS / Linux
```bash
git clone https://github.com/keks84725/Photo-Video-Organizer.git
cd Photo-Video-Organizer
pip install -r requirements.txt
python3 main.py
```

---

<br/>

## 🇬🇧 Photo & Video Organizer 2.0 (English)

**Photo & Video Organizer 2.0** is an ultra-fast, local-first, privacy-focused desktop application designed to bring order to messy photo and video archives.

Unlike cloud solutions like Google Photos, Apple iCloud, or expensive subscriptions (Mylio, Excire), this tool operates **100% offline**:
* 🔒 **Zero Telemetry / Zero Cloud** — not a single byte leaves your computer. Your family moments, private records, and documents remain strictly yours.
* 💸 **No Subscriptions** — completely free and open-source under the MIT license.
* ⚡ **High Throughput** — process multi-terabyte external hard drives and camera SD cards at full disk speed.

---

### 🗺️ Visual Interface Guide

<div align="center">

![Buttons & UI Callout Guide](assets/ui_annotated_en.svg)

</div>

### 🕹️ Control Panel & Buttons

| No. | Control | Name | Function |
|---|---|---|---|
| **1** | **Top Notch** | `PHOTO-VIDEO-ORGANIZER` | Dynamic island style title badge. |
| **2** | **Display Screen** | **Status Monitor** | Integrated log and status display: outputs real-time scanning metrics, active filenames, and progress bar. |
| **3** | **Mode Selector** | `FULL` *(Full Check)* | Performs complete date-based organization into `YYYY/MM` folders, separates duplicates into `Duplicates`, and extracts screenshots into `Other`. |
| | | `DUPLICATE` *(Duplicate Check)* | Deep cryptographic SHA-256 hash scanner that isolates identical clones without modifying the main structure. |
| | | `OTHER` *(Other Check)* | Quickly isolates screenshots (<100KB or filename keywords) and unsupported formats. |
| **4** | **Folder Grid (2×2)** | `Temp` | **Source:** folder containing unsorted files (phone backups, camera cards, downloads). |
| | | `Media` | **Destination:** target library organized chronologically into `YYYY/MM` subfolders. |
| | | `Duplicate` | **Duplicates folder:** safe holding area for detected copies (never deletes files blindly). |
| | | `Other` | **Other folder:** holding area for screenshots and non-media formats. |
| **5** | **Action Button** | `START / STOP` | Single-click execution running on a background worker thread (`QThread`). Switches to red `STOP` button during operation. |
| **6** | **Utility Sidebar** | `?` *(Help & Undo)* | Interactive documentation modal and one-click **«Undo Last Sort»** button to safely restore all files. |
| | | `🇬🇧 / 🇷🇺 / 🇨🇳` *(Languages)* | 3-way language switch with dynamic national flag updates. |
| | | `GitHub` | Direct link to repository and open-source releases. |
| | | `Donate` | Support independent open-source development. |

---

### 📦 Supported Formats

* **Photos**: JPEG, JPG, PNG, HEIC, TIFF, BMP, GIF, WEBP.
* **RAW Formats**: Canon (CR2, CR3), Nikon (NEF, NRW), Sony (ARW, SRF, SR2), Adobe (DNG), Fujifilm (RAF), Panasonic (RW2), Olympus (ORF).
* **Videos**: MP4, MOV, MKV, AVI, WMV, M4V, MPG, WEBM, TS, MTS, M2TS.

---

### 💻 Installation & Build

#### Windows One-Click Setup
1. Clone or download the repository.
2. Double-click `Install.bat` to install dependencies.
3. Double-click **`PhotoOrganizer.bat`** to start the app.
4. *(Optional)* Run **`Build_EXE.bat`** to compile a single portable `PhotoVideoOrganizer.exe` into the `dist/` directory.

#### macOS & Linux Setup
```bash
git clone https://github.com/keks84725/Photo-Video-Organizer.git
cd Photo-Video-Organizer
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

---

<div align="center">

Made with ❤️ for photographers, archivists, and privacy advocates worldwide.

</div>
