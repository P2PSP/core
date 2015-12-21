# Minimum CMake version required
cmake_minimum_required(VERSION 2.8)

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
REQUIRED)

find_package(OpenSSL REQUIRED)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)

include_directories(${Boost_INCLUDE_DIR} ${OPENSSL_INCLUDE_DIR})
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
file(GLOB CORE_SOURCES "src/core/*.cc")
file(GLOB UTIL_SOURCES "src/util/*.cc")

# Executables
add_executable(peer 
  "src/peer.cc"
  ${CORE_SOURCES}
  ${UTIL_SOURCES}
)

add_executable(splitter
  "src/splitter.cc"
  ${CORE_SOURCES}
  ${UTIL_SOURCES}
)

find_package(Threads)

# Libraries
target_link_libraries(peer 
  log4cpp 
  ${OPENSSL_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
  ${Boost_LIBRARIES}
)

target_link_libraries(splitter 
  log4cpp
  ${OPENSSL_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
  ${Boost_LIBRARIES}
)

# The code below only works for CMake 3.1.0 or later for C++11 activation
set_property(TARGET peer PROPERTY CXX_STANDARD 11)
set_property(TARGET peer PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET splitter PROPERTY CXX_STANDARD 11)
set_property(TARGET splitter PROPERTY CXX_STANDARD_REQUIRED ON)

