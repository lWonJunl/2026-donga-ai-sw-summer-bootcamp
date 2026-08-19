$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw ".venv was not found: $Python" }

# CPU wheel only: do not install a CUDA build.
& $Python -m pip install --upgrade pip
& $Python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.0+cpu
& $Python -m pip install --only-binary=:all: -r (Join-Path $ProjectRoot 'requirements-cpu.txt')
& $Python -m pip check
& $Python -c "import torch, transformers, peft; assert not torch.cuda.is_available(); print('torch=', torch.__version__, 'cuda=', torch.cuda.is_available()); print('transformers=', transformers.__version__); print('peft=', peft.__version__)"
