CXX			:= g++
CXXFLAGS	:= -std=c++11 -fPIC -pedantic-errors -Wall -Wextra -Werror
LDFLAGS		:= -ldl
BUILD		:= ./build
OBJ_DIR		:= $(BUILD)/objects
TARGET		:= $(BUILD)/libdoping.so
INCLUDE		:= -Iinclude
SRC			:= \
	$(wildcard source/DynamicFunction/*.cpp) \
	$(wildcard source/SourceRenderingEngine/*.cpp)

OBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/%.o)
TESTOBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/test_%.o)

all: $(TARGET)

debug: CXXFLAGS += -g
debug: all

release: CXXFLAGS += -O2
release: all

$(OBJ_DIR)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(OBJ_DIR)/test_%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) -g -Wno-error=address $(CXXFLAGS) $(INCLUDE) -DUNIT_TEST -o $@ -c $<

$(TARGET): source/dopingRuntime.cpp $(OBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $(OBJ_DIR)/dopingRuntime.o -c $<
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) $(OBJECTS) $(OBJ_DIR)/dopingRuntime.o -shared -o $@

.PHONY: all build clean debug release

test: source/unit-test.cpp ${TESTOBJECTS}
	${CXX} -g ${CXXFLAGS} $(INCLUDE) ${TESTOBJECTS} $< $(LDFLAGS) -o $(BUILD)/run_tests
	$(BUILD)/run_tests

clean:
	-@rm -rvf $(BUILD)
