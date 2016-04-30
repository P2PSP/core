# Minimum CMake version required
cmake_minimum_required(VERSION 2.8)

option(BUILD_LIB "Build the library" ON)
option(BUILD_REDUCED_LIB "Build a reduced version" OFF)

option(BUILD_TEST "Build the test" ON)

#option(BUILD_PEER "Build the peer" ON)
#option(BUILD_SPLITTER "Build the splitter" ON)

option(BUILD_PYTHON_WRAPPER "Build the Python wrapper" ON)

option(BUILD_WITH_CLANG "Build using the Clang compiler" OFF)

if(BUILD_WITH_CLANG)
  set(CMAKE_C_COMPILER clang)
  set(CMAKE_CXX_COMPILER clang++)
endif()

# Project name
project(p2psp C CXX)

list(APPEND BOOST_REQUIRED_COMPONENTS
  system
  filesystem
  chrono
  serialization
  timer
  thread
  log
  log_setup
  date_time
  program_options
)

if(BUILD_PYTHON_WRAPPER)
  execute_process(COMMAND sh -c "ldconfig -p | grep libboost_python-py34" RESULT_VARIABLE res_var)
  if("${res_var}" STREQUAL "0")
    # on Ubuntu, python-py34 is available
    list(APPEND BOOST_REQUIRED_COMPONENTS python-py34)
  else()
    # on Arch, python3 is available
    list(APPEND BOOST_REQUIRED_COMPONENTS python3)
  endif()
endif()

find_package(Boost COMPONENTS
  ${BOOST_REQUIRED_COMPONENTS}
REQUIRED)

ADD_DEFINITIONS(-DBOOST_LOG_DYN_LINK)

find_package(Threads REQUIRED)
find_package(OpenSSL REQUIRED)

if(BUILD_PYTHON_WRAPPER)
  find_package(PythonLibs 3 REQUIRED)
endif()

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)

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
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
else ()
    message(FATAL_ERROR "Your C++ compiler does not support C++11")
endif ()

# Sources
if(NOT BUILD_REDUCED_LIB)
  file(GLOB P2PSP_SOURCES
    "src/core/*.cc"
    "src/util/*.cc"
  )
else()
  file(GLOB P2PSP_SOURCES
    "src/core/peer_ims.cc"
    "src/core/peer_dbs.cc"
    "src/core/python.cc"
    "src/util/*.cc"
  )
endif()

if(NOT BUILD_PYTHON_WRAPPER)
  list(REMOVE_ITEM P2PSP_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/src/core/python.cc")
endif()

if(BUILD_LIB)
  # Executables
  add_library(p2psp SHARED
    ${P2PSP_SOURCES}
  )

  # Libraries
  target_link_libraries(p2psp
    ${OPENSSL_LIBRARIES}
    ${CMAKE_THREAD_LIBS_INIT}
    ${Boost_LIBRARIES}
    ${PYTHON_LIBRARIES}
  )

  # Enable C++11 for CMake 3.1.0 or later
  set_property(TARGET p2psp PROPERTY CXX_STANDARD 11)
  set_property(TARGET p2psp PROPERTY CXX_STANDARD_REQUIRED ON)
endif()

#if(BUILD_PEER AND NOT BUILD_REDUCED_LIB)
  # Executable
#  add_executable(peer "src/peer.cc")

  # Libraries
#  target_link_libraries(peer
#    p2psp
#    ${CMAKE_THREAD_LIBS_INIT}
#    ${Boost_LIBRARIES}
#  )

  # Enable C++11 for CMake 3.1.0 or later
#  set_property(TARGET peer PROPERTY CXX_STANDARD 11)
#  set_property(TARGET peer PROPERTY CXX_STANDARD_REQUIRED ON)
#endif()

#if(BUILD_SPLITTER AND NOT BUILD_REDUCED_LIB)
  # Executable
#  add_executable(splitter "src/splitter.cc")

  # Libraries
#  target_link_libraries(splitter
#    p2psp
#    ${CMAKE_THREAD_LIBS_INIT}
#    ${Boost_LIBRARIES}
#  )

  # Enable C++11 for CMake 3.1.0 or later
#  set_property(TARGET splitter PROPERTY CXX_STANDARD 11)
#  set_property(TARGET splitter PROPERTY CXX_STANDARD_REQUIRED ON)
#endif()

if(BUILD_TEST)
  # Executable
  add_executable(test
    "src/test.cc"
    "src/util/trace.cc"
  )

  # Libraries
  target_link_libraries(test
    ${CMAKE_THREAD_LIBS_INIT}
    ${Boost_LIBRARIES}
    ${PYTHON_LIBRARIES}
  )

  # Enable C++11 for CMake 3.1.0 or later
  set_property(TARGET test PROPERTY CXX_STANDARD 11)
  set_property(TARGET test PROPERTY CXX_STANDARD_REQUIRED ON)
endif()
