﻿# Интерактивная сортировка фотографий с EXIF
param(
    [int]$BatchSize = 50
)

# Функция для выбора папки через диалог
function Get-FolderPath {
    param(
        [string]$Description,
        [string]$DefaultPath = ""
    )
    
    Add-Type -AssemblyName System.Windows.Forms
    
    # Создаем и настраиваем диалог выбора папки
    $folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderDialog.Description = $Description
    $folderDialog.SelectedPath = $DefaultPath
    $folderDialog.ShowNewFolderButton = $true
    
    # Показываем диалог и возвращаем результат
    if ($folderDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        return $folderDialog.SelectedPath
    } else {
        Write-Host "Диалог отменен. Используется путь по умолчанию." -ForegroundColor Yellow
        return $DefaultPath
    }
}

# Функция для определения скриншотов по имени файла и размеру
function Test-IsScreenshot {
    param([string]$FilePath)
    
    $fileItem = Get-Item $FilePath
    $fileName = $fileItem.Name
    $nameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($fileName).ToLower()
    
    # БЫСТРАЯ ПРОВЕРКА: файлы меньше 100KB с высокой вероятностью скриншоты
    if ($fileItem.Length -lt 100KB) {
        Write-Host "    Маленький файл (<100KB), вероятно скриншот" -ForegroundColor Magenta
        return $true
    }
    
    # Ключевые слова для идентификации скриншотов
    $screenshotKeywords = @(
        'screenshot',
        'скриншот',
        'screen shot',
        'скрин',
        'снимок экрана',
        'screencap',
        'screen_cap',
        'screengrab',
        'screen_grab',
        'snapshot',
        'screencapture',
        'printscreen',
        'prntscrn'
    )
    
    # Проверяем наличие ключевых слов в имени файла
    foreach ($keyword in $screenshotKeywords) {
        if ($nameWithoutExt -match $keyword) {
            return $true
        }
    }
    
    return $false
}

# Функция для проверки поддерживаемых форматов файлов
function Test-SupportedFileFormat {
    param([string]$FilePath)
    
    $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
    
    # Поддерживаемые форматы фото
    $photoExtensions = @(
        '.jpg', '.jpeg', '.jpe', '.jfif',
        '.png', '.bmp', '.tiff', '.tif',
        '.gif', '.webp', '.heic', '.heif',
        '.raw', '.arw', '.cr2', '.cr3', '.nef', '.nrw',
        '.dng', '.orf', '.raf', '.rw2', '.pef', '.srf',
        '.sr2', '.mrw', '.dcr', '.x3f', '.erf', '.mdc',
        '.psd', '.ai', '.eps'
    )
    
    # Поддерживаемые форматы видео
    $videoExtensions = @(
        '.mp4', '.m4v', '.mov', '.avi', '.wmv',
        '.mpg', '.mpeg', '.m2ts', '.mts', '.mkv',
        '.flv', '.f4v', '.webm', '.vob', '.ogv',
        '.3gp', '.3g2', '.mxf', '.ts'
    )
    
    # Все поддерживаемые форматы
    $supportedExtensions = $photoExtensions + $videoExtensions
    
    return $supportedExtensions -contains $extension
}

# Запрашиваем пути у пользователя
Write-Host "=== Настройка путей для сортировки фотографий ===" -ForegroundColor Cyan
Write-Host ""

# Путь к исходной папке
$defaultSource = if (Test-Path "D:\Pictures\Photos\temp") { "D:\Pictures\Photos\temp" } else { [Environment]::GetFolderPath('MyPictures') }
Write-Host "Выберите ИСХОДНУЮ папку с фотографиями (temp):" -ForegroundColor Yellow
Write-Host "Обычно это: D:\Pictures\Photos\temp или аналогичный путь" -ForegroundColor Gray
$SourcePath = Get-FolderPath -Description "Выберите исходную папку с фотографиями для сортировки" -DefaultPath $defaultSource

if ([string]::IsNullOrEmpty($SourcePath)) {
    Write-Host "Ошибка: Не выбрана исходная папка!" -ForegroundColor Red
    return
}

# Путь к целевой папке
$defaultDestination = if (Test-Path "D:\Pictures\Photos") { "D:\Pictures\Photos" } else { [Environment]::GetFolderPath('MyPictures') }
Write-Host "`nВыберите ЦЕЛЕВУЮ папку для отсортированных фотографий:" -ForegroundColor Yellow
Write-Host "Обычно это: D:\Pictures\Photos или аналогичный путь" -ForegroundColor Gray
$DestinationRoot = Get-FolderPath -Description "Выберите целевую папку для отсортированных фотографий" -DefaultPath $defaultDestination

if ([string]::IsNullOrEmpty($DestinationRoot)) {
    Write-Host "Ошибка: Не выбрана целевая папка!" -ForegroundColor Red
    return
}

# Автоматически создаем подпапки для проблемных файлов и скриншотов
$UnsortedPath = Join-Path $DestinationRoot "Unsorted"
$DoublePath = Join-Path $UnsortedPath "Double"
$ScreenshotPath = Join-Path $DestinationRoot "Screenshots"
$OtherFilesPath = Join-Path $UnsortedPath "OtherFiles"

Write-Host ""
Write-Host "Выбранные пути:" -ForegroundColor Green
Write-Host "  Источник: $SourcePath" -ForegroundColor White
Write-Host "  Целевая папка: $DestinationRoot" -ForegroundColor White
Write-Host "  Папка скриншотов: $ScreenshotPath" -ForegroundColor Magenta
Write-Host "  Папка проблемных файлов: $UnsortedPath" -ForegroundColor White
Write-Host "  Папка других файлов: $OtherFilesPath" -ForegroundColor Yellow
Write-Host "  Папка дубликатов: $DoublePath" -ForegroundColor White

# Подтверждение перед началом
Write-Host ""
Write-Host "ВНИМАНИЕ: Все файлы из исходной папки будут перемещены в целевую структуру!" -ForegroundColor Red
Write-Host "Поддерживаются только фото и видео файлы. Остальные файлы будут перемещены в папку OtherFiles." -ForegroundColor Yellow
$confirmation = Read-Host "Нажмите Enter для начала сортировки или 'N' для отмены"

if ($confirmation -eq 'N' -or $confirmation -eq 'n') {
    Write-Host "Сортировка отменена пользователем." -ForegroundColor Yellow
    return
}

# Создаем необходимые папки
Write-Host "`nСоздание структуры папок..." -ForegroundColor Cyan
$null = New-Item -ItemType Directory -Path $DestinationRoot -Force
$null = New-Item -ItemType Directory -Path $UnsortedPath -Force
$null = New-Item -ItemType Directory -Path $DoublePath -Force
$null = New-Item -ItemType Directory -Path $ScreenshotPath -Force
$null = New-Item -ItemType Directory -Path $OtherFilesPath -Force

Write-Host "Папки созданы успешно!" -ForegroundColor Green

# Предзагружаем сборку для EXIF (ускоряет последующие вызовы)
Add-Type -AssemblyName System.Drawing

# Кэш для уже обработанных дат из имен файлов
$dateCache = @{}

# Функция получения даты из имени файла (быстрая)
function Get-DateFromFileName {
    param([string]$FileName)
    
    if ($dateCache.ContainsKey($FileName)) {
        return $dateCache[$FileName]
    }
    
    try {
        $nameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
        
        # Быстрая проверка через substring
        if ($nameWithoutExt.Length -ge 8) {
            $yearPart = $nameWithoutExt.Substring(0, 4)
            $monthPart = $nameWithoutExt.Substring(4, 2) 
            $dayPart = $nameWithoutExt.Substring(6, 2)
            
            if ($yearPart -match "^\d{4}$" -and $monthPart -match "^\d{2}$" -and $dayPart -match "^\d{2}$") {
                $year = [int]$yearPart
                $month = [int]$monthPart
                $day = [int]$dayPart
                
                if ($year -ge 2000 -and $year -le ([DateTime]::Now.Year + 1) -and 
                    $month -ge 1 -and $month -le 12 -and 
                    $day -ge 1 -and $day -le 31) {
                    
                    $result = [DateTime]::new($year, $month, $day)
                    $dateCache[$FileName] = $result
                    return $result
                }
            }
        }
        
        # Дополнительные паттерны для файлов с другим форматом
        $patterns = @(
            'IMG_(\d{4})(\d{2})(\d{2})',
            'VID_(\d{4})(\d{2})(\d{2})', 
            '(\d{4})-(\d{2})-(\d{2})',
            '(\d{4})\.(\d{2})\.(\d{2})'
        )
        
        foreach ($pattern in $patterns) {
            if ($nameWithoutExt -match $pattern) {
                $year = [int]$Matches[1]
                $month = [int]$Matches[2]
                $day = [int]$Matches[3]
                
                if ($year -ge 2000 -and $year -le ([DateTime]::Now.Year + 1)) {
                    $result = [DateTime]::new($year, $month, $day)
                    $dateCache[$FileName] = $result
                    return $result
                }
            }
        }
    }
    catch {
        # Игнорируем ошибки
    }
    
    $dateCache[$FileName] = $null
    return $null
}

# Оптимизированная функция чтения EXIF
function Get-ExifDate {
    param([string]$FilePath)
    
    # Быстрая проверка типа файла
    $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
    $imageExtensions = @('.jpg', '.jpeg', '.tiff', '.tif', '.png', '.bmp', '.arw', '.cr2', '.nef')
    
    if ($imageExtensions -notcontains $extension) {
        return $null
    }
    
    try {
        # Используем FileStream для более надежного чтения
        $stream = [System.IO.File]::OpenRead($FilePath)
        $image = [System.Drawing.Image]::FromStream($stream, $false, $false)
        
        try {
            $propertyItems = $image.PropertyItems
            
            # Все основные EXIF теги для даты
            $dateTimeTags = @(
                0x9003, # DateTimeOriginal (дата съемки)
                0x9004, # DateTimeDigitized 
                0x0132, # DateTime (изменение)
                0x9000  # ExifVersion
            )
            
            foreach ($property in $propertyItems) {
                if ($dateTimeTags -contains $property.Id -and $property.Value -and $property.Value.Length -gt 0) {
                    try {
                        $dateString = [System.Text.Encoding]::ASCII.GetString($property.Value).Trim()
                        $dateString = $dateString -replace '[^\x20-\x7E]', '' # Только ASCII
                        
                        if (-not [string]::IsNullOrWhiteSpace($dateString)) {
                            # Основные форматы дат EXIF
                            $formats = @(
                                "yyyy:MM:dd HH:mm:ss",
                                "yyyy:MM:dd HH:mm",
                                "yyyy-MM-dd HH:mm:ss", 
                                "yyyy/MM/dd HH:mm:ss",
                                "yyyyMMdd HH:mm:ss"
                            )
                            
                            foreach ($format in $formats) {
                                try {
                                    $parsedDate = [DateTime]::ParseExact($dateString, $format, [System.Globalization.CultureInfo]::InvariantCulture)
                                    if ($parsedDate.Year -ge 1990 -and $parsedDate.Year -le [DateTime]::Now.Year + 1) {
                                        return $parsedDate
                                    }
                                }
                                catch {
                                    # Пробуем следующий формат
                                }
                            }
                            
                            # Пробуем ручной парсинг для сложных случаев
                            if ($dateString -match '(\d{4}).?(\d{2}).?(\d{2}).?(\d{2}).?(\d{2}).?(\d{2})') {
                                $year = [int]$Matches[1]
                                $month = [int]$Matches[2]
                                $day = [int]$Matches[3]
                                $hour = [int]$Matches[4]
                                $minute = [int]$Matches[5] 
                                $second = [int]$Matches[6]
                                
                                if ($year -ge 1990 -and $year -le [DateTime]::Now.Year + 1) {
                                    return [DateTime]::new($year, $month, $day, $hour, $minute, $second)
                                }
                            }
                        }
                    }
                    catch {
                        # Продолжаем с другим тегом
                        continue
                    }
                }
            }
        }
        finally {
            $image.Dispose()
            $stream.Close()
        }
    }
    catch {
        # Игнорируем ошибки EXIF
    }
    
    return $null
}

# Функция получения даты файла (полная точность)
function Get-FileDate {
    param([string]$FilePath)
    
    $fileItem = Get-Item $FilePath
    $fileName = $fileItem.Name
    
    Write-Host "  Файл: $fileName" -ForegroundColor Gray
    
    # 1. Пытаемся получить дату из EXIF (самая точная)
    $exifDate = Get-ExifDate -FilePath $FilePath
    if ($exifDate) {
        Write-Host "    EXIF дата: $($exifDate.ToString('dd.MM.yyyy HH:mm:ss'))" -ForegroundColor Green
        return $exifDate
    }
    
    # 2. Пытаемся извлечь дату из имени файла
    $fileNameDate = Get-DateFromFileName -FileName $fileName
    if ($fileNameDate) {
        Write-Host "    Дата из имени: $($fileNameDate.ToString('dd.MM.yyyy'))" -ForegroundColor Yellow
        return $fileNameDate
    }
    
    # 3. Используем системные даты
    $creationTime = $fileItem.CreationTime
    $lastWriteTime = $fileItem.LastWriteTime
    
    # Берем самую раннюю дату
    $selectedDate = ($creationTime, $lastWriteTime | Sort-Object | Select-Object -First 1)
    Write-Host "    Системная дата: $($selectedDate.ToString('dd.MM.yyyy HH:mm:ss'))" -ForegroundColor Cyan
    
    return $selectedDate
}

# Функция для проверки дубликатов
function Test-FileDuplicate {
    param([string]$SourceFile, [string]$TargetFolder)
    
    $sourceItem = Get-Item $SourceFile
    $sourceName = $sourceItem.Name
    
    if (-not (Test-Path $TargetFolder)) { return $false }
    
    $existingFile = Join-Path $TargetFolder $sourceName
    if (Test-Path $existingFile) {
        $existingItem = Get-Item $existingFile
        return $existingItem.Length -eq $sourceItem.Length
    }
    
    return $false
}

# Функция для создания структуры папок
function Get-DestinationPath {
    param([DateTime]$Date)
    
    $yearFolder = $Date.Year.ToString("0000")
    $monthNames = @("Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь")
    $monthFolder = "$($Date.Month.ToString('00')) - $($monthNames[$Date.Month - 1])"
    
    $fullPath = Join-Path $DestinationRoot $yearFolder
    $fullPath = Join-Path $fullPath $monthFolder
    
    $null = New-Item -ItemType Directory -Path $fullPath -Force
    return $fullPath
}

# Функция безопасного перемещения файла
function Move-FileSafely {
    param([string]$SourcePath, [string]$DestinationPath)
    
    try {
        # Быстрая проверка блокировки
        try {
            $stream = [System.IO.File]::Open($SourcePath, 'Open', 'Read', 'None')
            $stream.Close()
        }
        catch {
            Start-Sleep -Milliseconds 50
        }
        
        Move-Item -Path $SourcePath -Destination $DestinationPath -Force
        return $true
    }
    catch {
        return $false
    }
}

# ОСНОВНОЙ ПРОЦЕСС С ПРОГРЕССОМ
Write-Host "`n=== Начало сортировки фотографий ===" -ForegroundColor Cyan

# Получаем все файлы
$allFiles = @(Get-ChildItem -Path $SourcePath -File -Recurse)
$totalFiles = $allFiles.Count

Write-Host "Найдено файлов для обработки: $totalFiles" -ForegroundColor Cyan

if ($totalFiles -eq 0) {
    Write-Host "Нет файлов для обработки!" -ForegroundColor Yellow
    return
}

$processedCount = 0
$errorCount = 0
$duplicateCount = 0
$screenshotCount = 0
$otherFilesCount = 0
$startTime = Get-Date

# Статистика по методам определения даты
$exifCount = 0
$nameCount = 0
$systemCount = 0

# Обрабатываем файлы с прогрессом
for ($i = 0; $i -lt $totalFiles; $i++) {
    $file = $allFiles[$i]
    
    # Показываем прогресс
    if ($i % $BatchSize -eq 0 -or $i -eq $totalFiles - 1) {
        $percent = [math]::Round(($i / $totalFiles) * 100, 1)
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt 0) {
            $filesPerSecond = [math]::Round($i / $elapsed.TotalSeconds, 1)
            $remaining = [math]::Round(($totalFiles - $i) / $filesPerSecond / 60, 1)
        } else {
            $filesPerSecond = 0
            $remaining = 0
        }
        
        Write-Progress -Activity "Обработка файлов" -Status "$i/$totalFiles ($percent%) | Скриншоты: $screenshotCount | Другие: $otherFilesCount | EXIF: $exifCount | Имена: $nameCount | Система: $systemCount" -PercentComplete $percent
    }
    
    try {
        # Проверяем поддерживаемый формат файла
        if (-not (Test-SupportedFileFormat -FilePath $file.FullName)) {
            Write-Host "  Неподдерживаемый формат: $($file.Name)" -ForegroundColor Yellow
            $destinationFile = Join-Path $OtherFilesPath $file.Name
            $counter = 1
            while (Test-Path $destinationFile) {
                $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                $extension = [System.IO.Path]::GetExtension($file.Name)
                $destinationFile = Join-Path $OtherFilesPath "$baseName-$counter$extension"
                $counter++
            }
            
            if (Move-FileSafely -SourcePath $file.FullName -Destination $destinationFile) {
                $otherFilesCount++
            } else {
                $errorCount++
            }
            continue
        }
        
        # Проверяем, является ли файл скриншотом
        if (Test-IsScreenshot -FilePath $file.FullName) {
            Write-Host "  Скриншот обнаружен: $($file.Name)" -ForegroundColor Magenta
            
            # Проверка дубликатов для скриншотов
            if (Test-FileDuplicate -SourceFile $file.FullName -TargetFolder $ScreenshotPath) {
                $duplicateDestination = Join-Path $DoublePath $file.Name
                $counter = 1
                while (Test-Path $duplicateDestination) {
                    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                    $extension = [System.IO.Path]::GetExtension($file.Name)
                    $duplicateDestination = Join-Path $DoublePath "$baseName-$counter$extension"
                    $counter++
                }
                
                if (Move-FileSafely -SourcePath $file.FullName -Destination $duplicateDestination) {
                    $duplicateCount++
                    $screenshotCount++
                } else {
                    $errorCount++
                }
            }
            else {
                $destinationFile = Join-Path $ScreenshotPath $file.Name
                $counter = 1
                while (Test-Path $destinationFile) {
                    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                    $extension = [System.IO.Path]::GetExtension($file.Name)
                    $destinationFile = Join-Path $ScreenshotPath "$baseName-$counter$extension"
                    $counter++
                }
                
                if (Move-FileSafely -SourcePath $file.FullName -Destination $destinationFile) {
                    $processedCount++
                    $screenshotCount++
                } else {
                    $errorCount++
                }
            }
            continue
        }
        
        # Обычная обработка для поддерживаемых файлов (не скриншотов)
        $fileDate = Get-FileDate -FilePath $file.FullName
        $destinationFolder = Get-DestinationPath -Date $fileDate
        
        # Обновляем статистику методов
        $exifDate = Get-ExifDate -FilePath $file.FullName
        if ($exifDate) { $exifCount++ }
        elseif (Get-DateFromFileName -FileName $file.Name) { $nameCount++ }
        else { $systemCount++ }
        
        # Проверка дубликатов и перемещение
        if (Test-FileDuplicate -SourceFile $file.FullName -TargetFolder $destinationFolder) {
            $duplicateDestination = Join-Path $DoublePath $file.Name
            $counter = 1
            while (Test-Path $duplicateDestination) {
                $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                $extension = [System.IO.Path]::GetExtension($file.Name)
                $duplicateDestination = Join-Path $DoublePath "$baseName-$counter$extension"
                $counter++
            }
            
            if (Move-FileSafely -SourcePath $file.FullName -Destination $duplicateDestination) {
                $duplicateCount++
            } else {
                $errorCount++
            }
        }
        else {
            $destinationFile = Join-Path $destinationFolder $file.Name
            $counter = 1
            while (Test-Path $destinationFile) {
                $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                $extension = [System.IO.Path]::GetExtension($file.Name)
                $destinationFile = Join-Path $destinationFolder "$baseName-$counter$extension"
                $counter++
            }
            
            if (Move-FileSafely -SourcePath $file.FullName -Destination $destinationFile) {
                $processedCount++
            } else {
                $errorCount++
            }
        }
    }
    catch {
        $errorCount++
    }
}

Write-Progress -Activity "Обработка файлов" -Completed

# Очистка пустых папок
Write-Host "Очистка пустых папок..." -ForegroundColor Cyan
Get-ChildItem -Path $SourcePath -Directory -Recurse | 
    Where-Object { (Get-ChildItem $_.FullName -Recurse -Force | Measure-Object).Count -eq 0 } | 
    Remove-Item -Recurse -Force

$totalTime = (Get-Date) - $startTime
Write-Host "`n=== Обработка завершена! ===" -ForegroundColor Cyan
Write-Host "Время выполнения: $([math]::Round($totalTime.TotalMinutes, 1)) минут" -ForegroundColor White
Write-Host ""
Write-Host "Статистика обработки:" -ForegroundColor Green
Write-Host "  Скриншоты: $screenshotCount файлов" -ForegroundColor Magenta
Write-Host "  Другие файлы: $otherFilesCount файлов" -ForegroundColor Yellow
Write-Host "  EXIF: $exifCount файлов" -ForegroundColor Green  
Write-Host "  Имена файлов: $nameCount файлов" -ForegroundColor Yellow
Write-Host "  Системные даты: $systemCount файлов" -ForegroundColor Cyan
Write-Host ""
Write-Host "Результаты сортировки:" -ForegroundColor Green
Write-Host "  Успешно обработано: $processedCount" -ForegroundColor Green
Write-Host "  Скриншоты перемещены: $screenshotCount" -ForegroundColor Magenta
Write-Host "  Другие файлы перемещены: $otherFilesCount" -ForegroundColor Yellow
Write-Host "  Дубликатов: $duplicateCount" -ForegroundColor Yellow
Write-Host "  Ошибок: $errorCount" -ForegroundColor Red
Write-Host "  Средняя скорость: $([math]::Round($totalFiles / $totalTime.TotalSeconds, 1)) файл/сек" -ForegroundColor Gray
Write-Host ""
Write-Host "Распределение файлов:" -ForegroundColor Green
Write-Host "  Папка скриншотов: $ScreenshotPath" -ForegroundColor Magenta
Write-Host "  Папка других файлов: $OtherFilesPath" -ForegroundColor Yellow
Write-Host "  Папка с проблемными файлами: $UnsortedPath" -ForegroundColor Magenta
Write-Host "  Папка с дубликатами: $DoublePath" -ForegroundColor Magenta

# Завершающее сообщение
if ($errorCount -eq 0 -and $duplicateCount -eq 0) {
    Write-Host "`nВсе файлы успешно отсортированы! ✓" -ForegroundColor Green
} else {
    Write-Host "`nСортировка завершена с замечаниями. Проверьте папки с проблемными файлами." -ForegroundColor Yellow
}

Read-Host "`nНажмите Enter для выхода"