cmake_minimum_required(VERSION 3.16)
project(NeuroSightAI LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Qt Configuration
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Tell AUTOUIC where to find UI files
set(CMAKE_AUTOUIC_SEARCH_PATHS ${CMAKE_CURRENT_SOURCE_DIR}/ui)

# Find Qt packages (Qt 6.x)
find_package(Qt6 COMPONENTS 
    Core 
    Gui 
    Widgets 
    Network 
    REQUIRED
)

# Source files
set(PROJECT_SOURCES
    src/main.cpp
    src/mainwindow.h
    src/mainwindow.cpp
    src/modelhandler.h
    src/modelhandler.cpp
    ui/mainwindow.ui
    resources/resources.qrc
)

# Create executable
add_executable(NeuroSightAI ${PROJECT_SOURCES})

# Link Qt libraries (Qt 6.x)
target_link_libraries(NeuroSightAI 
    Qt6::Core 
    Qt6::Gui 
    Qt6::Widgets 
    Qt6::Network
)

# Include directories (ensure generated UI headers are found)
target_include_directories(NeuroSightAI PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/ui
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}/src
)

# Platform-specific settings
if(WIN32)
    set_target_properties(NeuroSightAI PROPERTIES WIN32_EXECUTABLE ON)
elseif(APPLE)
    set_target_properties(NeuroSightAI PROPERTIES MACOSX_BUNDLE ON)
endif()

# Installation rules
install(TARGETS NeuroSightAI
    BUNDLE DESTINATION .
    RUNTIME DESTINATION bin
)

#