CXX=g++
CXXFLAGS=-std=c++11


SOURCES=SourceRenderingEngine/SourceRenderingEngine.cpp

all:
	${CXX} ${CXXFLAGS} -c -shared -fpic dopingRuntime.cpp -ldl

compiletests: ${SOURCES}
	${CXX} ${CXXFLAGS} -Iutils unit-test.cpp ${SOURCES} -o run_tests

test: compiletests
	./run_tests


