# Upload sample document to Knowledge Assistant API

$filePath = "data\samples\science_class_ix.md"
$url = "http://localhost:8000/api/documents/upload/"

# Read file content
$fileContent = [System.IO.File]::ReadAllBytes($filePath)
$fileName = "science_class_ix.md"

# Create boundary
$boundary = [System.Guid]::NewGuid().ToString()

# Create multipart form data
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: text/markdown",
    "",
    [System.Text.Encoding]::UTF8.GetString($fileContent),
    "--$boundary",
    "Content-Disposition: form-data; name=`"title`"",
    "",
    "Science Class IX",
    "--$boundary--"
)

$body = $bodyLines -join "`r`n"

# Make request
try {
    $response = Invoke-RestMethod -Uri $url -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $body
    Write-Host "✓ Document uploaded successfully!" -ForegroundColor Green
    Write-Host "Document ID: $($response.id)"
    Write-Host "Title: $($response.title)"
    Write-Host "Chunks: $($response.chunk_count)"
    Write-Host "Processed: $($response.processed)"
} catch {
    Write-Host "✗ Error uploading document: $_" -ForegroundColor Red
}
