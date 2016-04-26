cmake_minimum_required(VERSION 2.8)

add_definitions(-std=c++11 -fPIC)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake)

# Finding python and boost-python
find_package(Boost COMPONENTS python)

find_package(PythonInterp 2.7.6 REQUIRED)
find_package(PythonLibs 2.7.6 REQUIRED)
find_package(NumPy REQUIRED)
include_directories( ${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS}
			cpp/Boost.NumPy )
link_directories( ${Boost_LIBRARY_DIR} )

include_directories( ${NUMPY_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS} cpp cpp/polycont)

add_subdirectory(cpp)

# Create python library
add_library( tstab SHARED cpp/polycont/python.cpp cpp/clipper/clipper.cpp)
target_link_libraries( tstab boost_numpy ${Boost_LIBRARIES} ${PYTHON_LIBRARIES} )
set_target_properties( tstab PROPERTIES PREFIX "")

