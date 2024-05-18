cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/cmake-install" CACHE PATH "..." FORCE)
set(CMAKE_VERBOSE_MAKEFILE "TRUE" CACHE BOOL "..." FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS "TRUE" CACHE BOOL "..." FORCE)

block()
    set(fileName "util.cmake")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/${fileName}")
        file(REMOVE "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}")
        file(DOWNLOAD
            "https://raw.githubusercontent.com/exqudens/exqudens-cmake/1.0.1/src/main/cmake/${fileName}"
            "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}"
            EXPECTED_MD5 "d7dd546adf3830d9eb6cca7b0dda7d4e"
            STATUS downloadStatus
        )
        if(NOT "${downloadStatus}" STREQUAL "0;\"No error\"")
            message(FATAL_ERROR "downloadStatus: '${downloadStatus}'")
        endif()
        file(COPY "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/../common")
    endif()
endblock()

include("${CMAKE_CURRENT_BINARY_DIR}/../common/util.cmake")

string(REPLACE "." ";" PRESET_NAME_ELEMENTS "${PRESET_NAME}")
if("msvc-16-x64-x64" IN_LIST "PRESET_NAME_ELEMENTS")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/msvc-16-x64-x64-toolchain.cmake")
        set_msvc_toolchain(TOOLCHAIN_CONTENT
            PROCESSOR "x86_64"
            OS "${CMAKE_HOST_SYSTEM_NAME}"
            VERSION "16"
            HOST "x64"
            TARGET "x64"
            SET_CMAKE_SYSTEM_NAME "FALSE"
            OUTPUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/../common/msvc-16-x64-x64-toolchain.cmake"
        )
    endif()
    find_program(CONAN_COMMAND NAMES "conan.exe" PATHS ENV CONAN_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
elseif("gcc" IN_LIST PRESET_NAME_ELEMENTS)
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/gcc-toolchain.cmake")
        find_file(compilerFile NAMES "gcc" PATHS ENV GCC_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
        set_gnu_toolchain(TOOLCHAIN_CONTENT
            PROCESSOR "x86_64"
            OS "${CMAKE_HOST_SYSTEM_NAME}"
            PATH "${compilerFile}"
            SET_CMAKE_SYSTEM_NAME "FALSE"
            OUTPUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/../common/gcc-toolchain.cmake"
        )
    endif()
    find_program(CONAN_COMMAND NAMES "conan" PATHS ENV CONAN_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
endif()

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/name-version.txt" INFO)
string(REPLACE ":" ";" INFO_LIST "${INFO}")
list(GET INFO_LIST 0 RAW_NAME)
list(GET INFO_LIST 1 RAW_VERSION)
string(STRIP "${RAW_NAME}" NAME)
string(STRIP "${RAW_VERSION}" VERSION)
project("${NAME}" VERSION "${VERSION}" LANGUAGES "NONE")

message(STATUS "project: '${PROJECT_NAME}-${PROJECT_VERSION}'")

string(TOLOWER "${PROJECT_NAME}" PROJECT_NAME_LOWER)
set(PROJECT_VERSION_NOTWEAK "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")

message(STATUS "PROJECT_NAME_LOWER: '${PROJECT_NAME_LOWER}'")
message(STATUS "PROJECT_VERSION_NOTWEAK: '${PROJECT_VERSION_NOTWEAK}'")

enable_language("C")
enable_language("CXX")

set_conan_architecture(CONAN_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
set_conan_compiler(CONAN_COMPILER "${CMAKE_CXX_COMPILER_ID}")
set_conan_compiler_version(CONAN_COMPILER_VERSION "${CMAKE_CXX_COMPILER_ID}" "${CMAKE_CXX_COMPILER_VERSION}" MAX_ELEMENTS "1")
set_conan_compiler_runtime(CONAN_COMPILER_RUNTIME "${CMAKE_MSVC_RUNTIME_LIBRARY}")

set_python_boolean(CONAN_INTERFACE_ONLY "${INTERFACE_ONLY}")
set_python_boolean(CONAN_BUILD_SHARED_LIBS "${BUILD_SHARED_LIBS}")

set_conan_settings(CONAN_SETTINGS
    "arch=${CONAN_ARCH}"
    "os=${CMAKE_SYSTEM_NAME}"
    "compiler=${CONAN_COMPILER}"
    "compiler.version=${CONAN_COMPILER_VERSION}"
    "compiler.runtime=${CONAN_COMPILER_RUNTIME}"
    "compiler.libcxx=${CONAN_COMPILER_LIBCXX}"
    "build_type=${CMAKE_BUILD_TYPE}"
)
set_conan_options(CONAN_OPTIONS
    "shared=${CONAN_BUILD_SHARED_LIBS}"
    "reference=${PROJECT_NAME_LOWER}/${PROJECT_VERSION_NOTWEAK}"
    "name=${PROJECT_NAME_LOWER}"
    "version=${PROJECT_VERSION_NOTWEAK}"
)

set(CONAN_INSTALL_PREFIX "${PROJECT_BINARY_DIR}/conan-install")

if(NOT EXISTS "${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
    execute_process(
        COMMAND "${CONAN_COMMAND}" "install"
                "--install-folder" "${CONAN_INSTALL_PREFIX}"
                ${CONAN_SETTINGS}
                ${CONAN_OPTIONS}
                "${PROJECT_SOURCE_DIR}/install-conanfile.py"
        COMMAND_ECHO "STDERR"
        ENCODING "UTF-8"
        COMMAND_ERROR_IS_FATAL ANY
    )
    file(REMOVE "${CONAN_INSTALL_PREFIX}/${PROJECT_NAME_LOWER}-${PROJECT_VERSION_NOTWEAK}/conaninfo.txt")
    file(REMOVE "${CONAN_INSTALL_PREFIX}/${PROJECT_NAME_LOWER}-${PROJECT_VERSION_NOTWEAK}/conanmanifest.txt")
endif()
if(NOT EXISTS "${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
    message(FATAL_ERROR "Not exists: '${CONAN_INSTALL_PREFIX}/conan-packages.cmake'")
endif()

add_custom_target("conan-export"
    COMMAND "${CONAN_COMMAND}" "export-pkg"
            "--force"
            "--package-folder" "${CONAN_INSTALL_PREFIX}/${PROJECT_NAME_LOWER}-${PROJECT_VERSION_NOTWEAK}"
            ${CONAN_SETTINGS}
            "--options" "shared=${CONAN_BUILD_SHARED_LIBS}"
            "${PROJECT_SOURCE_DIR}/conanfile.py"
            #"gitlab-group+gitlab-sub-group+${PROJECT_NAME_LOWER}/stable"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    USES_TERMINAL
    VERBATIM
)

set_target_names(ALL_TARGETS "${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "all-targets:")
foreach(t IN LISTS ALL_TARGETS)
    message(STATUS "${t}")
endforeach()
