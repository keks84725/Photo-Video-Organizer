<div align="center">

# 📸 Photo & Video Organizer 2.0
### *Next-Gen Local-First Photo Sorter & Duplicate Cleaner*

[![Release](https://img.shields.io/badge/Release-v2.0-blue.svg)](https://github.com/keks84725/Photo-Video-Organizer/releases/tag/v2.0)
[![Download EXE](https://img.shields.io/badge/Download-PhotoVideoOrganizer.exe%20(55%20MB)-success?logo=windows&logoColor=white)](https://github.com/keks84725/Photo-Video-Organizer/releases/download/v2.0/PhotoVideoOrganizer.exe)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline%20%7C%20Zero%20Cloud-red?logo=shield&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

<br/>

![Photo & Video Organizer 2.0 Banner](assets/banner_v2.jpg)

<br/>

### [![Скачать PhotoVideoOrganizer.exe](https://img.shields.io/badge/📥%20Скачать%20PhotoVideoOrganizer.exe%20(v2.0%20Windows)-55%20MB-0284C7?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/keks84725/Photo-Video-Organizer/releases/download/v2.0/PhotoVideoOrganizer.exe)

*Портативный автономный .exe • 55 МБ • Запуск в 1 клик без установки*

**[💾 Прямая ссылка на PhotoVideoOrganizer.exe](https://github.com/keks84725/Photo-Video-Organizer/releases/download/v2.0/PhotoVideoOrganizer.exe)** • **[📦 Страница релиза v2.0](https://github.com/keks84725/Photo-Video-Organizer/releases/tag/v2.0)**

**[🇷🇺 Описание на русском](#-photo--video-organizer-20) • [🇬🇧 English Guide](#-photo--video-organizer-20-english)**

</div>

---

## 🇷🇺 Photo & Video Organizer 2.0

**Photo & Video Organizer 2.0** — это быстрое, полностью автономное десктопное приложение для наведения идеального порядка в фотоархивах, очистки дубликатов и сортировки снимков по датам.

В отличие от облачных сервисов и платных аналогов, программа работает **на 100% локально на вашем компьютере**:
* 🔒 **0 байт отправляется в сеть** — ваши личные фото и документы никогда не покинут ваш ПК.
* 💸 **Никаких подписок** — бесплатно, без рекламы и без скрытых платежей.
* ⚡ **Портативный `.exe`** — программа не требует установки, регистрации и сторонних компонентов.

---

### 🗺️ Интерактивная карта интерфейса

Интерфейс спроектирован по принципу *Zero-Friction*: вся функциональность упакована в одно окно размером `585 × 720 px`, где всё понятно с первого взгляда.

<div align="center">

![Карта кнопок и интерфейса](assets/ui_interface_guide.jpg)

</div>

### 🕹️ Описание блоков и элементов управления

| № | Элемент | Название | Назначение |
|---|---|---|---|
| **1** | **Вырез (Notch)** | `PHOTO-VIDEO-ORGANIZER` | Фирменный статус-бэйдж в стиле Dynamic Island. |
| **2** | **Монитор состояния** | **Экран дисплея** | Выводит ход сканирования, имя обрабатываемого файла, статус дубликатов и прогресс-бар в реальном времени. |
| **3** | **Селектор режимов** | `FULL` *(Полная проверка)* | Сортирует фотографии по папкам `Год/Месяц` на основе EXIF, отсеивает дубликаты в `Duplicates`, а скриншоты — в `Other`. |
| | | `DUPLICATE` *(Поиск дубликатов)* | Сканирует архив и находит одинаковые файлы по криптографическому хэшу SHA-256 без изменения структуры папок. |
| | | `OTHER` *(Прочие файлы)* | Извлекает скриншоты (<100 КБ или по ключевым словам) и документы из фотопотока. |
| **4** | **Сетка папок (2×2)** | `Temp` | **Откуда брать:** папка-источник (сброшенные фото с телефона, флешки фотоаппарата, папка «Загрузки»). |
| | | `Media` | **Куда складывать:** целевая библиотека (автоматически создаются папки `YYYY/MM`). |
| | | `Duplicate` | **Папка дубликатов:** изолированное хранилище найденных копий (файлы не удаляются вслепую). |
| | | `Other` | **Папка прочего:** скриншоты, чеки, нераспознанные форматы. |
| **5** | **Кнопка START** | `START / STOP` | Запуск алгоритма в отдельном потоке (окно не зависает). При клике плавно превращается в красную кнопку `STOP`. |
| **6** | **Боковая панель** | `?` *(Справка & Undo)* | Интерактивная справка и кнопка **«Отменить последнюю сортировку»** (возвращает все файлы обратно, если вы ошиблись). |
| | | `🇷🇺 / 🇬🇧 / 🇨🇳` *(Языки)* | Мгновенное переключение языка интерфейса с динамической сменой государственного флага. |
| | | `GitHub` | Прямой переход к странице проекта и обновлениям. |
| | | `Donate` | Кнопка поддержки независимой разработки. |

---

### ✨ Возможности версии 2.0

* **Точная датировка по EXIF**: Извлекает метаданные `DateTimeOriginal` даже у старых снимков с профессиональных камер.
* **Поддержка Apple & RAW**: Уверенно читает JPEG, PNG, HEIC, а также форматы фотографов (CR2, CR3, NEF, ARW, DNG, RAF, RW2).
* **Умный фильтр скриншотов**: Автоматически распознает снимки экрана по 15+ языковым паттернам (`screenshot`, `скрин`, `снимок экрана` и т.д.) или объему < 100 КБ.
* **Побайтовое хэширование SHA-256**: Гарантирует, что дубликатом признаются только 100% идентичные файлы, исключая потерю фото.
* **Автосохранение путей**: Запоминает выбранные папки и язык между запусками.
* *(Обработка и умная сортировка видеофайлов запланирована к релизу в версии 2.1)*.

---

### 💻 Запуск программы

Программа поставляется в виде одного готового автономного файла **`PhotoVideoOrganizer.exe`** (без установщиков, библиотек и командных строк):

1. Запустите скачанный файл **`PhotoVideoOrganizer.exe`** двойным кликом на Windows 10/11.
2. Выберите папки источника и назначения в сетке и нажмите кнопку **START** — приложение сразу начнет организацию файлов!

---

<br/>

## 🇬🇧 Photo & Video Organizer 2.0 (English)

**Photo & Video Organizer 2.0** is an ultra-fast, local-first, privacy-focused desktop application designed to bring order to messy photo archives and clean up duplicates.

Unlike cloud solutions or paid subscriptions, this tool operates **100% offline**:
* 🔒 **Zero Telemetry / Zero Cloud** — not a single byte leaves your computer. Your family moments and private photos remain strictly yours.
* 💸 **No Subscriptions** — completely free and open-source under the MIT license.
* ⚡ **Portable `.exe`** — no setup wizards, no installers, no dependencies required.

---

### 🗺️ Visual Interface Guide

<div align="center">

![Photo & Video Organizer 2.0 Interface & Controls Guide](assets/ui_interface_guide.jpg)

</div>

### 🕹️ Control Panel & Buttons

| No. | Control | Name | Function |
|---|---|---|---|
| **1** | **Top Notch** | `PHOTO-VIDEO-ORGANIZER` | Dynamic island style title badge. |
| **2** | **Display Screen** | **Status Monitor** | Outputs real-time scanning metrics, active filenames, and progress bar. |
| **3** | **Mode Selector** | `FULL` *(Full Check)* | Organizes photos chronologically into `YYYY/MM` folders, separates duplicates into `Duplicates`, and extracts screenshots into `Other`. |
| | | `DUPLICATE` *(Duplicate Check)* | Cryptographic SHA-256 hash scanner that isolates identical clones without modifying the main structure. |
| | | `OTHER` *(Other Check)* | Quickly isolates screenshots (<100KB or filename keywords) and non-photo formats. |
| **4** | **Folder Grid (2×2)** | `Temp` | **Source:** folder containing unsorted files (phone backups, camera cards, downloads). |
| | | `Media` | **Destination:** target library organized into `YYYY/MM` subfolders. |
| | | `Duplicate` | **Duplicates folder:** safe holding area for detected copies (never deletes files blindly). |
| | | `Other` | **Other folder:** holding area for screenshots and other formats. |
| **5** | **Action Button** | `START / STOP` | Single-click execution running on a background worker thread. Switches to red `STOP` button during operation. |
| **6** | **Utility Sidebar** | `?` *(Help & Undo)* | Interactive documentation modal and one-click **«Undo Last Sort»** button to safely restore all files. |
| | | `🇬🇧 / 🇷🇺 / 🇨🇳` *(Languages)* | 3-way language switch with dynamic national flag updates. |
| | | `GitHub` | Direct link to repository and open-source releases. |
| | | `Donate` | Support independent open-source development. |

---

### 📦 Supported Photo Formats

* **Photos**: JPEG, JPG, PNG, HEIC, TIFF, BMP, GIF, WEBP.
* **RAW Formats**: Canon (CR2, CR3), Nikon (NEF, NRW), Sony (ARW, SRF, SR2), Adobe (DNG), Fujifilm (RAF), Panasonic (RW2), Olympus (ORF).
* *(Advanced video sorting is scheduled for the upcoming v2.1 release)*.

---

### 💻 How to Run

Zero installations or setup wizards required. The application is distributed as a single standalone portable **`PhotoVideoOrganizer.exe`**:

1. Double-click the downloaded **`PhotoVideoOrganizer.exe`** on Windows 10/11.
2. Select your source and target folders in the grid, then click **START** to begin organizing!

---

<div align="center">

Made with ❤️ for photographers, archivists, and privacy advocates worldwide.

</div>
