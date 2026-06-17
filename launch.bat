@echo off

if not exist fyppro_env (
    mkdir fyppro_env
    tar -xzf fyppro_packed.tar.gz -C fyppro_env
)

pause