*** Settings ***
Suite Setup       init_test
Suite Teardown    close_test
Metadata          SW_VERSION    1.0
Library           ../../GX1Testlib.py
*** Test Cases ***
TEST_CASE_1_CLICK_SCREENSHOT
    [Documentation]    This test case is for demo for the features of DVTFront of GX1.
    [Tags]    MAINPAGE    SCREENSHOT    DEMO
    Log    this is the test demo, started
    sleep    1s
    Screen Shot
    sleep    10s
    Log    this is the test demo, started
