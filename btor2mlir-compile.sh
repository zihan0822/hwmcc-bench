#!/usr/bin/env bash
set -euo pipefail

# Usage function
usage() {
  echo "Usage: $0 -o <output_dir> <input.btor>"
  exit 1
}

# Parse arguments
if [[ $# -lt 2 ]]; then
  usage
fi

outdir=""
input=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output)
      outdir="$2"
      shift 2
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      input="$1"
      shift
      ;;
  esac
done

# Validate inputs
if [[ -z "$input" || -z "$outdir" ]]; then
  usage
fi

if [[ ! -f "$input" ]]; then
  echo "Error: File '$input' not found."
  exit 1
fi

# Create output directory if needed
mkdir -p "$outdir"

# Extract base filename (no path, no extension)
filename="$(basename "$input")"
base="${filename%.*}"

# Define output paths
mlir="${outdir}/${base}.mlir"
mlir_opt="${outdir}/${base}.mlir.opt"
ll="${mlir_opt}.ll"          # append .ll to .mlir.opt
exe="${outdir}/${base}"      # final executable

# Step 1: BTOR -> MLIR
echo "[1/4] Translating BTOR → MLIR..."
btor2mlir-translate --import-btor "$input" > "$mlir"

# Step 2: Optimize MLIR
echo "[2/4] Running MLIR optimizations..."
btor2mlir-opt \
  --btor-liveness \
  --convert-btornd-to-llvm \
  --convert-btor-to-memref \
  --convert-memref-to-llvm \
  --convert-btor-to-vector \
  --convert-vector-to-llvm \
  --convert-arith-to-llvm \
  --convert-btor-to-llvm \
  --convert-std-to-llvm \
  --convert-vector-to-llvm \
  --resolve-casts \
  --convert-btornd-to-llvm \
  --convert-btor-to-vector \
  --convert-arith-to-llvm \
  --convert-std-to-llvm \
  --convert-btor-to-llvm \
  --convert-vector-to-llvm \
 "$mlir" > "$mlir_opt"

# Step 3: MLIR -> LLVM IR
echo "[3/4] Translating MLIR → LLVM IR..."
btor2mlir-translate --mlir-to-llvmir "$mlir_opt" > "$ll"

# Step 4: LLVM IR -> Executable
echo "[4/4] Compiling LLVM IR → Executable..."
if [[ -z "${BTOR2MLIR:-}" ]]; then
  echo "Error: Environment variable BTOR2MLIR is not set."
  echo "Please export BTOR2MLIR to point to your btor2mlir repository root."
  exit 1
fi

clang++-14 -O3 btor2mlir-wrapper.cc "$ll" "$BTOR2MLIR/run/lib/libcex.a" -o "$exe"

echo "✅ Done. Generated in '$outdir':"
echo "  $(basename "$mlir")"
echo "  $(basename "$mlir_opt")"
echo "  $(basename "$ll")"
echo "  $(basename "$exe") (executable)"

