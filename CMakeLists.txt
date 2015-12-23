# Minimum CMake version required
cmake_minimum_required(VERSION 2.8)

option(BUILD_REDUCED_LIB "Build a reduced version" ON)

option(BUILD_PEER "Build the peer" OFF)
option(BUILD_SPLITTER "Build the splitter" OFF)

# Project name
project(p2psp C CXX)

find_package(Boost COMPONENTS 
  system 
  filesystem 
  chrono 
  serialization
  timer
  thread
  program_options
  python
REQUIRED)

find_package(Threads REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(PythonLibs REQUIRED)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)

include_directories(
  ${Boost_INCLUDE_DIR} 
  ${OPENSSL_INCLUDE_DIR}
  ${PYTHON_INCLUDE_DIRS}
)

link_directories(${Boost_LIBRARY_DIR})

# Initialize CXXFLAGS
set(CMAKE_CXX_FLAGS                "-Wall -std=c++11")
set(CMAKE_CXX_FLAGS_DEBUG          "-O0 -g")
set(CMAKE_CXX_FLAGS_MINSIZEREL     "-Os -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE        "-O4 -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g")

# Compiler-specific C++11 activation
if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "GNU")
    execute_process(
        COMMAND ${CMAKE_CXX_COMPILER} -dumpversion OUTPUT_VARIABLE GCC_VERSION)
    if (NOT (GCC_VERSION VERSION_GREATER 4.7 OR GCC_VERSION VERSION_EQUAL 4.7))
        message(FATAL_ERROR "${PROJECT_NAME} requires g++ 4.7 or greater")
    endif ()
elseif ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
else ()
    message(FATAL_ERROR "Your C++ compiler does not support C++11")
endif ()

# Sources
if(NOT BUILD_REDUCED_LIB)
  file(GLOB CORE_SOURCES "src/core/*.cc")
else()
  file(GLOB CORE_SOURCES 
    "src/core/peer_ims.cc"
    "src/core/peer_dbs.cc"
    "src/core/python.cc"
  )
endif()

file(GLOB UTIL_SOURCES "src/util/*.cc")

# Executables
add_library(p2psp SHARED
  ${CORE_SOURCES}
  ${UTIL_SOURCES}
)

# Libraries
target_link_libraries(p2psp 
  log4cpp 
  ${OPENSSL_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
  ${Boost_LIBRARIES}
  ${PYTHON_LIBRARIES}
)

# The code below only works for CMake 3.1.0 or later for C++11 activation
set_property(TARGET p2psp PROPERTY CXX_STANDARD 11)
set_property(TARGET p2psp PROPERTY CXX_STANDARD_REQUIRED ON)

if(BUILD_PEER)
  # Executable
  add_executable(peer "src/peer.cc")

  # Libraries
  target_link_libraries(peer 
    p2psp
    ${CMAKE_THREAD_LIBS_INIT}
    ${Boost_LIBRARIES}
  )
  
  # Enable C+11 for CMake 3.1.0 or later
  set_property(TARGET peer PROPERTY CXX_STANDARD 11)
  set_property(TARGET peer PROPERTY CXX_STANDARD_REQUIRED ON)
endif()

if(BUILD_SPLITTER)
  # Executable
  add_executable(splitter "src/splitter.cc")
  
  # Libraries
  target_link_libraries(splitter 
    p2psp
    ${CMAKE_THREAD_LIBS_INIT}
    ${Boost_LIBRARIES}
  )

  # Enable C+11 for CMake 3.1.0 or later
  set_property(TARGET splitter PROPERTY CXX_STANDARD 11)
  set_property(TARGET splitter PROPERTY CXX_STANDARD_REQUIRED ON)
endif()