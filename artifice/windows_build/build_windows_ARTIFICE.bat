pyinstaller ARTIFICE.spec
xcopy /s /e ..\resources .\dist\resources
copy ..\config.yml .\dist
xcopy /s /e ..\builtin_protocols .\dist\builtin_protocols

