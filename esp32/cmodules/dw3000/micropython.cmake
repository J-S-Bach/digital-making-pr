add_library(usermod_dw3000 INTERFACE)

target_sources(usermod INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/SPI.cpp
    ${CMAKE_CURRENT_LIST_DIR}/dw3000_wrapper.cpp
    ${CMAKE_CURRENT_LIST_DIR}/micropython.c
    ${CMAKE_CURRENT_LIST_DIR}/DW3000_Arduino/DW3000/src/DW3000.cpp
)

target_include_directories(usermod INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/DW3000_Arduino/DW3000/src
)

target_compile_features(usermod INTERFACE cxx_std_17)

target_link_libraries(usermod INTERFACE usermod_dw3000)

message(STATUS "DW3000 List Dir: ${CMAKE_CURRENT_LIST_DIR}")
