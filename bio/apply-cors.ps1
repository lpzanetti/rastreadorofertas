# Aplica CORS no bucket GCS usado pelo feed de produtos.
# Pré-requisito: gcloud auth login (conta com permissão no bucket)

$ErrorActionPreference = "Stop"

$gcloud = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
$gsutil = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd"
$corsFile = Join-Path $PSScriptRoot "cors.json"
$bucket = "gs://rastreador-ofertas-lp"

if (-not (Test-Path $gcloud)) {
  throw "gcloud nao encontrado. Instale o Google Cloud SDK."
}

Write-Host "Contas autenticadas:"
& $gcloud auth list

Write-Host "`nCORS atual:"
& $gsutil cors get $bucket

Write-Host "`nAplicando CORS de $corsFile ..."
& $gsutil cors set $corsFile $bucket

Write-Host "`nCORS depois:"
& $gsutil cors get $bucket

Write-Host "`nTeste rapido de header:"
curl.exe -sI -H "Origin: https://www.rastreadordeofertas.com.br" "https://storage.googleapis.com/rastreador-ofertas-lp/produtos/atual.json"
