CXX			:= g++
CXXFLAGS	:= -std=c++11 -fPIC -pedantic-errors -Wall -Wextra # -Werror
LDFLAGS		:=
BUILD		:= ./build
OBJ_DIR		:= $(BUILD)/objects
TARGET		:= $(BUILD)/libdoping.so
INCLUDE		:= -Iinclude
SRC			:= \
	$(wildcard source/DynamicFunction/*.cpp) \
	$(wildcard source/SourceRenderingEngine/*.cpp)

OBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/%.o)
TESTOBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/test_%.o)

all: build $(TARGET)

$(OBJ_DIR)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(OBJ_DIR)/test_%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -DUNIT_TEST -o $@ -c $<

$(TARGET): source/dopingRuntime.cpp $(OBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $(OBJ_DIR)/dopingRuntime.o -c $<
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) $(OBJECTS) $(OBJ_DIR)/dopingRuntime.o -shared -o $@

.PHONY: all build clean debug release

build:
	@mkdir -p $(BUILD)
	@mkdir -p $(OBJ_DIR)

test: source/unit-test.cpp ${TESTOBJECTS}
	${CXX} ${CXXFLAGS} $(INCLUDE) ${TESTOBJECTS} $< -o run_tests
	./run_tests



clean:
	-@rm -rvf build
