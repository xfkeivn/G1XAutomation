*** Settings ***
Suite Setup       init_test
Suite Teardown    close_test
Metadata          SW_VERSION    1.0
Metadata          FW_VERSION    2.0
Library           ../../GX1Testlib.py
*** Test Cases ***
TEST_CASE_1_SCREENSHOT
    [Documentation]    This test case is for demo for the features of DVTFront of GX1.
    [Tags]    MAINPAGE    SCREENSHOT    DEMO    stimulation
    Log    this is the test demo, started
    sleep    1s
    Mouse Xy    722    161
    sleep    0.5s
    Screen Shot
    Mouse XY    426    718
    sleep    10s
    Start Scenario    ImpedanceRamp
    Start Scenario    RampMeasure
    sleep    10s
    Stop Scenario    RampMeasure
    Screen Shot
    sleep    1s
    Start Scenario    RampMeasure
    sleep    5s
    Stop Scenario    RampMeasure
    Stop Scenario    ImpedanceRamp
    sleep    5s
    Log    this is the test demo, started
    Screen Shot

TEST_CASE_2_CLICK_AND_SCREEN_SHOT
    [Documentation]    This is the second case
    [Tags]    VOLTAGE    POWER
    Log    this is the test demo, started
    sleep    1s
    Mouse Click    OneTouch
    sleep    5s
    Screen Shot
    sleep    1s
    Mouse Click    Stimulation
    sleep    1s
    Set Command Response    C046    u8_OutputStatus=1    u8_ButtonStatus=1
    sleep    1s
    Screen Shot
    sleep    1s
    Set Command Response    C046    u8_OutputStatus=0    u8_ButtonStatus=1
    sleep    1s
    Screen Shot
    Mouse Click    PulseRF
    Screen Shot
    Log    this is the test demo, started

TEST_CASE_3_COMMAND_SEARCH
    [Tags]    VOLTAGE    STIMULATION
    Log    this test is for testing the search command logged in the queue
    Clean Command Logging Queue
    sleep    5s
    @{command_list}    Find Logged Commands    0xC049    0    ar_measured_channels[0].u8_TempRefAvailable=1
    ${message_count}    Get Length    ${command_list}
    Log    ${command_list[0].data.ar_measured_channels[0].u16_TempRef}
    Log    ${command_list[1].data.ar_measured_channels[0].u16_TempRef}
