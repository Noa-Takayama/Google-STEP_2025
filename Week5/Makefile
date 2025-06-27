# Makefile for compiling the C-based TSP solver

# Compiler
CC = gcc

# Compiler flags
# -O3: 最適化レベル3
# -Wall: 警告をすべて有効にする
# -lm: 数学ライブラリをリンクする
CFLAGS = -O3 -Wall -lm -std=c99

# The target executable
TARGET = solve_c

# The source file
SRC = solve_c.c

# Default target
all: $(TARGET)

# Rule to build the target
$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

# Rule to run the solver on a sample file (e.g., input_4.csv)
run_sample4: $(TARGET)
	./$(TARGET) input_4.csv output_4_c.csv