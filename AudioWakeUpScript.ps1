<#
    Script Name: AudioWakeUpScript.ps1

    Description: 
    This script is designed to periodically play a nearly inaudible sound file to keep speakers from going into sleep mode. 
    Some speakers may automatically go into sleep mode during periods of inactivity and may exhibit a delay when waking from sleep, 
    causing the first few sounds played to be cut off or distorted. By periodically playing a sound file, this script keeps the 
    speakers awake, preventing this from occurring. 

    Usage: 
    1. Set your desired .wav file path at the "$filePath" variable.
    2. Run this script in PowerShell.

    Note: 
    This script is set to play the sound file every 5 seconds indefinitely. You can adjust this timing by modifying the value in the Start-Sleep command.

    WARNING: 
    Be aware that this could potentially cause wear on your speakers if they are constantly kept awake. Use at your own risk.

    描述：
    该脚本旨在定期播放一个几乎听不到的声音文件，以防止扬声器进入睡眠模式。
    在不活动期间，某些扬声器可能会自动进入睡眠模式，并在从睡眠中唤醒时出现延迟，导致前几个播放的声音被截断或失真。
    通过定期播放声音文件，该脚本保持扬声器保持唤醒状态，防止这种情况发生。

    用法：
    1. 在"$filePath"变量中设置您想要的.wav文件的路径。
    2. 在PowerShell中运行此脚本。

    注意：
    该脚本被设置为每隔5秒播放一次声音文件，无限循环。您可以通过修改Start-Sleep命令中的值来调整此定时。

    警告：
    请注意，如果扬声器一直保持唤醒状态，可能会对其造成磨损。请自行承担风险。

#>

$filePath = ".\resources\AudioWakeUpScript_beep.wav"

if(-not (Test-Path $filePath)) {
    Write-Host "File does not exist."
    Pause
    Exit
}

while($true) {
    $player = New-Object System.Media.SoundPlayer
    $player.SoundLocation = $filePath
    $player.Play()

    Start-Sleep -Seconds 5
}
