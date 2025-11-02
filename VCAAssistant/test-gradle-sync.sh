#!/bin/bash
# Test Gradle Sync and Capture Detailed Errors
# Run this to see ACTUAL error messages that Android Studio hides

cd /home/indigo/my-project3/Dappva/VCAAssistant

echo "======================================================"
echo "Testing Gradle Sync with Full Error Output"
echo "======================================================"
echo ""

# Test 1: Basic sync (what Android Studio does)
echo "Test 1: Gradle Projects (basic sync)..."
./gradlew projects --stacktrace --info 2>&1 | tee gradle-sync-test.log

echo ""
echo "======================================================"
echo "Test Complete!"
echo "======================================================"
echo ""
echo "Log saved to: gradle-sync-test.log"
echo ""
echo "Checking for errors..."
grep -i "error\|exception\|failed\|failure" gradle-sync-test.log | head -20
