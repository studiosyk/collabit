param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [string]$Title,
    [string]$Date,
    [string]$Step,
    [string]$DestinationRoot,
    [switch]$MoveSource
)

$ErrorActionPreference = "Stop"

function Get-SafeFileName {
    param([Parameter(Mandatory = $true)][string]$Name)

    $invalidChars = [System.IO.Path]::GetInvalidFileNameChars()
    $result = $Name
    foreach ($char in $invalidChars) {
        $result = $result.Replace([string]$char, "")
    }
    $result = $result -replace "\s+", " "
    return $result.Trim()
}

function Get-PostSlug {
    param([Parameter(Mandatory = $true)][string]$Name)

    $slug = $Name.ToLowerInvariant()
    $slug = $slug -replace "^.+?step", "step"
    $slug = $slug -replace "step\s*([0-9]+)[^0-9]+([0-9]+)", ""
    $slug = $slug -replace "\s+", ""
    $slug = $slug -replace "[\?!\(\)\[\]:/\\|]", ""
    $slug = Get-SafeFileName $slug
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return "title"
    }
    return $slug
}

function Get-SourceTitle {
    param([Parameter(Mandatory = $true)][string]$SourceFile)

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFile)
    $title = $baseName -replace "^.+?Step", "Step"
    $title = $title.Trim()
    return $title
}

function Get-StepId {
    param([string]$Text)

    if ($Text -match "(?i)step\s*([0-9]+)[^0-9]+([0-9]+)") {
        return "step$($Matches[1])-$($Matches[2])".ToLowerInvariant()
    }
    return "stepx-x"
}

function Set-Utf8File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
$source = Resolve-Path $SourcePath
$sourceItem = Get-Item -LiteralPath $source
$stockRoot = Resolve-Path (Join-Path $repoRoot "core/writing/1_stock")
$sourceFullName = [System.IO.Path]::GetFullPath($sourceItem.FullName)
$stockFullName = [System.IO.Path]::GetFullPath($stockRoot.Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
if (-not $sourceFullName.StartsWith($stockFullName + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "SourcePath must be inside core/writing/1_stock. SourcePath: $sourceFullName"
}

if (-not $Date) {
    $Date = Get-Date -Format "yyMMdd"
}

if (-not $DestinationRoot) {
    $DestinationRoot = Join-Path $repoRoot "core/writing/2_in_progress"
}

$templateDir = Join-Path $repoRoot "core/writing/_templates/yymmdd_template"
if (-not (Test-Path -LiteralPath $templateDir)) {
    throw "Template directory not found: $templateDir"
}

if (-not $Title) {
    $Title = Get-SourceTitle $sourceItem.Name
}
$safeTitle = Get-SafeFileName $Title

if (-not $Step) {
    $Step = Get-StepId $Title
}

$articleDirName = "${Date}_$safeTitle"
$articleDir = Join-Path $DestinationRoot $articleDirName

if (Test-Path -LiteralPath $articleDir) {
    throw "Destination article directory already exists: $articleDir"
}

Copy-Item -LiteralPath $templateDir -Destination $articleDir -Recurse

$sourceDest = Join-Path $articleDir $sourceItem.Name
if ($MoveSource) {
    Move-Item -LiteralPath $sourceItem.FullName -Destination $sourceDest
} else {
    Copy-Item -LiteralPath $sourceItem.FullName -Destination $sourceDest
}

$docxCandidate = Join-Path $sourceItem.DirectoryName ([System.IO.Path]::GetFileNameWithoutExtension($sourceItem.Name) + ".docx")
if (Test-Path -LiteralPath $docxCandidate) {
    $docxDest = Join-Path $articleDir ([System.IO.Path]::GetFileName($docxCandidate))
    if ($MoveSource) {
        Move-Item -LiteralPath $docxCandidate -Destination $docxDest
    } else {
        Copy-Item -LiteralPath $docxCandidate -Destination $docxDest
    }
}

$postTemplate = Join-Path $articleDir "post-001_stepx-x_title.md"
$postSlug = Get-PostSlug $Title
$postFileName = "post-${Date}_${Step}_${postSlug}.md"
$postPath = Join-Path $articleDir $postFileName
if (Test-Path -LiteralPath $postTemplate) {
    Move-Item -LiteralPath $postTemplate -Destination $postPath
}

$briefPath = Join-Path $articleDir "brief.md"
$briefContent = @"
# brief

## Basic Info

- Title draft: $Title
- Purpose:
- Target reader:
- Search intent:
- CTA: <mark style="background-color: #ffcccc;">CTA</mark>
- Deadline:

## Client Direction

- Director instruction: Use source draft $($sourceItem.Name)
- Background:
- Priority:
- NG: Do not use CTA image

## Notes

- Notes:
- Stakeholder memo:

## Structure Logic Review

- Not done: Check internal contradiction, consistency, and logic issues in the structure draft
- Not done: Check consistency against source articles and related materials
- Not done: Search candidate reference articles and record titles and URLs
- Not done: Record structure changes, additions, and reasons

## Auto Execution Scope

- Human before trigger: Download received Google Drive materials into core/writing/1_stock and read the structure draft
- AI after trigger: Continue Article Workflow steps 2-5 in the same work turn
- Human+AI after step 5: Resume from human review of AI writing, then continue step 7 and later
"@
Set-Utf8File -Path $briefPath -Content $briefContent

$logPath = Join-Path $articleDir "log.md"
$action = if ($MoveSource) { "moved" } else { "copied" }
$logContent = @"
# log

## Work Log

- Date: $(Get-Date -Format "yyyy-MM-dd")
  - Done: Created article workspace with scripts/writing/start_writing_article.ps1. Copied template, $action source draft, and renamed post file to $postFileName.
  - Not done: Article Workflow steps 2-5 are not completed by this script itself.
  - Handoff: Agent should continue Article Workflow steps 2-5 in the same work turn: structure review, outline, draft, CTA, and figure placeholders.

## 作業報告 $(Get-Date -Format "yyyy-MM-dd HH:mm")

- 作業対象: $Title
- 今回の到達点: 記事フォルダ作成と初期セットアップまで完了
- 完了した工程: 執筆作業開始トリガーの初期セットアップ
- 更新したファイル: `brief.md`, `research.md`, `outline.md`, `$postFileName`, `log.md`, `README.md`
- 判断・変更メモ: 構成案を記事フォルダへ $action
- 未対応: 記事制作フロー 2〜5
- 次回の開始位置: 記事制作フロー 2「IDEで構成案の解釈と前提整理をする」
- 人間に確認してほしいこと: なし。AIが同じ作業ターン内で2〜5へ進む
"@
Set-Utf8File -Path $logPath -Content $logContent

$readmePath = Join-Path $articleDir "README.md"
$readmeContent = @"
# $articleDirName

## Source

- $($sourceItem.Name)

## Structure

text:
$articleDirName/
+-- brief.md
+-- research.md
+-- outline.md
+-- $postFileName
+-- log.md
+-- $($sourceItem.Name)
+-- assets/
    +-- thumbnail/
    +-- description/
"@
Set-Utf8File -Path $readmePath -Content $readmeContent

Write-Host "Created article workspace:"
Write-Host $articleDir
Write-Host ""
Write-Host "Next:"
Write-Host "1. Continue Article Workflow steps 2-5 in the same work turn"
Write-Host "2. Record review results in brief.md and output structure to outline.md"
Write-Host "3. Write draft, then place CTA and figure placeholders"
Write-Host "4. Stop before step 6: human review of AI writing"
