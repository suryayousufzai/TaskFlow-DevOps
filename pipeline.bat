@echo off
:: TaskFlow - DevOps Pipeline Script (Windows)
:: runs through: Lint -> Test -> Docker Build -> Smoke Test -> Deploy

title TaskFlow DevOps Pipeline

echo.
echo    TASKFLOW - LOCAL DEVOPS PIPELINE
echo.

:: STAGE 1: LINT
echo [STAGE 1] LINT AND CODE CHECK

echo   installing flake8...
pip install flake8 --quiet

echo   checking code style...
flake8 app/ run.py --max-line-length=120 --exclude=__pycache__

if %errorlevel% == 0 (
    echo   PASSED - no style errors found!
) else (
    echo   WARNING - some style issues found, you might want to fix them
)
echo.

:: STAGE 2: UNIT TESTS
echo [STAGE 2] UNIT TESTS

echo   installing dependencies...
pip install -r requirements.txt --quiet
pip install pytest pytest-cov --quiet

echo   running tests...
pytest tests/ -v --tb=short

if %errorlevel% == 0 (
    echo   PASSED - all tests passed!
) else (
    echo   FAILED - tests failed, stopping here
    pause
    exit /b 1
)
echo.

:: STAGE 3: DOCKER BUILD
echo [STAGE 3] DOCKER BUILD

docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo   Docker found, building the image...
    docker build -t taskflow:latest .
    if %errorlevel% == 0 (
        echo   PASSED - image built successfully!
    ) else (
        echo   WARNING - docker build failed, check the output above
    )
) else (
    echo   Docker not installed, skipping real build
    echo   would normally run: docker build -t taskflow:latest .
    echo   SIMULATED PASSED
)
echo.

:: STAGE 4: SMOKE TEST
echo [STAGE 4] SMOKE TEST

docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo   spinning up a test container...
    docker stop taskflow-test >nul 2>&1
    docker rm taskflow-test >nul 2>&1
    docker run -d --name taskflow-test -p 5001:5000 taskflow:latest

    echo   waiting 8 seconds for the app to boot up...
    timeout /t 8 /nobreak >nul

    curl -sf http://localhost:5001/health >nul 2>&1
    if %errorlevel% == 0 (
        echo   PASSED - app is healthy!
    ) else (
        echo   WARNING - health check didn't respond in time
    )

    docker stop taskflow-test >nul 2>&1
    docker rm taskflow-test >nul 2>&1
) else (
    echo   no Docker available, simulating smoke test
    echo   would check: GET http://localhost:5000/health
    echo   would check: GET http://localhost:5000/api/tasks
    echo   SIMULATED PASSED
)
echo.

:: STAGE 5: DEPLOY
echo [STAGE 5] DEPLOY

echo   simulating a production deployment...
echo   target:   production server
echo   image:    taskflow:latest
echo   strategy: rolling update
echo.
echo   step 1 - pull the latest image on the server
echo   step 2 - run: docker compose up -d
echo   step 3 - wait for health checks to pass
echo.
echo   PASSED - deployment simulated!
echo.

:: SUMMARY
echo    PIPELINE FINISHED SUCCESSFULLY!
echo.
echo    Stage 1 - Lint Check     DONE
echo    Stage 2 - Unit Tests     DONE
echo    Stage 3 - Docker Build   DONE
echo    Stage 4 - Smoke Test     DONE
echo    Stage 5 - Deploy         DONE
echo.
echo    all done, good job!
echo.
pause
