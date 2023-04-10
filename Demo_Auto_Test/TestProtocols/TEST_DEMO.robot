*** Settings ***
Suite Setup       init_test
Suite Teardown    close_test
Metadata          SW_VERSION    1.0
Library           ../../GX1Testlib.py
*** Test Cases ***
TEST_CASE_1_SCREENSHOT
    [Documentation]    This test case is for demo for the features of DVTFront of GX1.
    [Tags]    MAINPAGE    SCREENSHOT    DEMO
    Log    this is the test demo, started
    sleep    1s
    Screen Shot
    sleep    10s
    Log    this is the test demo, started

TEST_CASE_2_CLICK_AND_SCREEN_SHOT
    [Documentation]    This is the second case
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
