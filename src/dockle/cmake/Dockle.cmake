include_guard(GLOBAL)

include(CMakeParseArguments)

# Create a target that builds documentation through Dockle.
#
# dockle_add_docs(<target> [ALL] [CONFIG <dockle.toml>] [WORKING_DIRECTORY
# <directory>] [TARGETS <dockle-target>...])
#
# The module first looks for the dockle console command. If it is not installed,
# it falls back to Python3 -m dockle. Set DOCKLE_EXECUTABLE before including
# this module to select a standalone Dockle executable.
function(dockle_add_docs target)
    # Add a build target that invokes Dockle's canonical command-line interface.
    set(options ALL)
    set(one_value_args CONFIG WORKING_DIRECTORY)
    set(multi_value_args TARGETS)
    cmake_parse_arguments(DOCKLE "${options}" "${one_value_args}"
                          "${multi_value_args}" ${ARGN})

    if(DOCKLE_UNPARSED_ARGUMENTS)
        message(
            FATAL_ERROR
                "Unknown dockle_add_docs arguments: ${DOCKLE_UNPARSED_ARGUMENTS}"
        )
    endif()

    set(dockle_config "${DOCKLE_CONFIG}")
    if(NOT dockle_config)
        set(dockle_config "${CMAKE_SOURCE_DIR}/dockle.toml")
    elseif(NOT IS_ABSOLUTE "${dockle_config}")
        cmake_path(ABSOLUTE_PATH dockle_config BASE_DIRECTORY
                   "${CMAKE_CURRENT_SOURCE_DIR}" NORMALIZE)
    endif()

    if(NOT EXISTS "${dockle_config}")
        message(FATAL_ERROR "Dockle configuration not found: ${dockle_config}")
    endif()

    if(NOT DOCKLE_WORKING_DIRECTORY)
        cmake_path(GET dockle_config PARENT_PATH dockle_working_directory)
    else()
        set(dockle_working_directory "${DOCKLE_WORKING_DIRECTORY}")
    endif()

    if(DOCKLE_EXECUTABLE)
        set(dockle_command "${DOCKLE_EXECUTABLE}")
    else()
        find_program(dockle_program NAMES dockle dockle.exe)
        if(dockle_program)
            set(dockle_command "${dockle_program}")
        else()
            find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
            set(dockle_command "${Python3_EXECUTABLE}" -m dockle)
        endif()
    endif()

    set(dockle_arguments --config "${dockle_config}" build)
    list(APPEND dockle_arguments ${DOCKLE_TARGETS})

    if(DOCKLE_ALL)
        add_custom_target(
            "${target}" ALL
            COMMAND ${dockle_command} ${dockle_arguments}
            WORKING_DIRECTORY "${dockle_working_directory}"
            COMMENT "Building documentation with Dockle"
            USES_TERMINAL VERBATIM)
    else()
        add_custom_target(
            "${target}"
            COMMAND ${dockle_command} ${dockle_arguments}
            WORKING_DIRECTORY "${dockle_working_directory}"
            COMMENT "Building documentation with Dockle"
            USES_TERMINAL VERBATIM)
    endif()
endfunction()
