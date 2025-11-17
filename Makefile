BTOR_FILES := $(shell find data -name "*.btor")
BTOR2MLIR_BINARIES := $(patsubst data/%,build/%,$(BTOR_FILES))

all: hwmcc 
.PHONY: btor2mlir run

btor2mlir:
	@mkdir -p btor2mlir/build
	@cd btor2mlir/build && \
	 cmake -G Ninja .. \
    	-DCMAKE_C_COMPILER=$(LLVM)/bin/clang-14 \
    	-DCMAKE_CXX_COMPILER=$(LLVM)/bin/clang++-14 \
    	-DMLIR_DIR=$(LLVM)/lib/cmake/mlir \
    	-DLLVM_DIR=$(LLVM)/lib/cmake/llvm \
    	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
    	-DLLVM_ENABLE_LLD=ON \
    	-DCMAKE_INSTALL_PREFIX=$(shell pwd)/run && \
    	ninja && \
    	ninja install

hwmcc: btor2mlir $(BTOR2MLIR_BINARIES)
	
build/%.btor: data/%.btor
	@mkdir -p $(dir $@)
	@./btor2mlir-compile.sh -o $(dir $@) $<
	