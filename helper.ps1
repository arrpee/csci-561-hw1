python .\graph_generator.py

$Files = Get-ChildItem ".\test_cases\" -Filter input*.txt
$Misses = @()
for ($i = 0; $i -lt $Files.Count; $i++) {
    $Percent = $i / $Files.Count * 100
    Write-Progress -Activity "Testing in Progress" -Status "$Percent/% Complete:" -PercentComplete $Percent

    Copy-Item -Path $Files[$i] -Destination ".\input.txt"
    python .\homework3.py
    $output_filename = $(Split-Path $Files[$i] -leaf).Replace("input", "output")
    Copy-Item -Path ".\output.txt" -Destination $(".\test_outputs\" + $output_filename)


    If (Compare-Object `
            -ReferenceObject (Get-Content -Path $(".\test_outputs\" + $output_filename) -TotalCount 1) `
            -DifferenceObject (Get-Content -Path $(".\test_cases\" + $output_filename) -TotalCount 1)) {
        $Misses += $Files[$i]
    }

}

Write-Host $Misses

Remove-Item -Path ".\input.txt"
Remove-Item -Path ".\output.txt"